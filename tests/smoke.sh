#!/usr/bin/env bash
# smoke.sh — verify the deterministic parts end-to-end without any LLM work.
# 1) coverage-window self-tests  2) live market data  3) validator rejects a bad fixture
# 3b) the earnings guard fires on an API date conflict  3c) category gate / exposure / freshness checks
# 4) render the good fixture
set -u
cd "$(dirname "$0")/.."

fail() { echo "FAIL: $*"; exit 1; }

echo "== 1. session_window self-test =="; python3 scripts/session_window.py --selftest || exit 1
echo; echo "== 2. simulated run start (fixture is written for Thu 2026-09-10 08:45 ET) =="
python3 scripts/session_window.py --at 2026-09-10T08:45 >/dev/null || exit 1
python3 scripts/market_data.py | tail -3
# Steps 3/3b below assert on *validation* output, so they only mean something if the inputs the
# validator needs actually exist. Without this check a market_data.py failure makes step 3 exit
# non-zero for the wrong reason ("missing market.json") and the step passes while testing nothing.
[ -f run/market.json ] || fail "run/market.json missing — market_data.py did not produce output; steps 3/3b cannot be trusted"

# the fixture's earnings dates are frozen in time; drop live events.json so the guard does not fire on stale data
rm -f run/events.json

echo; echo "== 3. validator must REJECT the bad fixture =="
python3 - <<'PY'
import json, copy, io
c = json.load(io.open('tests/fixture_content.json', encoding='utf-8'))
b = copy.deepcopy(c)
b['timeline'][3]['date'] = '2026-09-09'
b['toplead'] = 'Whether the tape bounces is the question.'
json.dump(b, io.open('run/content.bad.json', 'w', encoding='utf-8'))
PY
out=$(python3 scripts/render_briefing.py --content run/content.bad.json --check-only 2>&1); rc=$?
echo "$out"
[ $rc -ne 0 ] || fail "bad fixture accepted"
# assert on the specific errors, not just a non-zero exit
echo "$out" | grep -q "banned construction" || fail "banned-construction check did not fire"
echo "$out" | grep -q "outside the coverage window" || fail "coverage-window check did not fire"

echo; echo "== 3b. earnings guard must REJECT a date the API contradicts =="
# The fixture dates ORCL earnings 2026-09-10. Feed a conflicting API-confirmed date and require the
# guard to catch it on every surface that carries the date.
python3 - <<'PY'
import json, io
ev = {"generated_et": "2026-09-10 08:45 ET",
      "symbols": {"ORCL": {"earnings_dates": ["2026-09-14"], "is_estimate": False}},
      "earnings_in_hold_window": [{"ticker": "ORCL", "date": "2026-09-14",
                                   "confirmation": "Yahoo + Nasdaq agree on the date",
                                   "is_estimate": False}],
      "earnings_just_past_edge": [], "ex_div": []}
json.dump(ev, io.open('run/events.json', 'w', encoding='utf-8'))
PY
out=$(python3 scripts/render_briefing.py --content tests/fixture_content.json --check-only 2>&1); rc=$?
echo "$out"
rm -f run/events.json
[ $rc -ne 0 ] || fail "earnings guard did not fire on an API date conflict"
for surface in "timeline" "heads_up" "symbols" "calendar"; do
  echo "$out" | grep -q "^  .*$surface.*API-confirmed date is 2026-09-14" \
    || fail "earnings guard did not fire on $surface"
done

echo; echo "== 3c. category gate / exposure / freshness / consistency checks =="
python3 - <<'PY'
import json, copy, io
c = json.load(io.open('tests/fixture_content.json', encoding='utf-8'))
b = copy.deepcopy(c)
b['calendar']['2026-09-15'].append({"text": "2-yr auction $69B 13:00", "class": "e-macro"})   # short coupon → error
b['news'][0]['exposed'].append({"ticker": "MU", "channel": "HBM"})                            # not on watchlist → error
b['news'][1]['event_date'] = '2026-09-01'                                                      # 7 sessions old, no gates_date → warning
b['calendar']['2026-09-16'].append({"text": "GDP Q2 third est 08:30", "class": "e-macro"})     # also cut → warning
b['cut_for_cause'].append({"item": "GDP Q2 third estimate Sep 16", "reason": "stale revision"})
b['toplead'] = b['toplead'] + " " + " ".join(["padding"] * 20)                                 # over budget → warning
json.dump(b, io.open('run/content.bad.json', 'w', encoding='utf-8'))
PY
out=$(python3 scripts/render_briefing.py --content run/content.bad.json --check-only 2>&1); rc=$?
echo "$out"
[ $rc -ne 0 ] || fail "short-coupon chip / off-watchlist exposure accepted"
echo "$out" | grep -q "2/3/5/7-yr auctions fail the CATEGORY GATE" || fail "short-coupon gate did not fire"
echo "$out" | grep -q "MU is not on the watchlist" || fail "exposed-ticker check did not fire"
# the warnings are only printed when there are no errors — re-check with the two errors removed
python3 - <<'PY'
import json, io
b = json.load(io.open('run/content.bad.json', encoding='utf-8'))
b['calendar']['2026-09-15'].pop()
b['news'][0]['exposed'].pop()
json.dump(b, io.open('run/content.bad.json', 'w', encoding='utf-8'))
PY
out=$(python3 scripts/render_briefing.py --content run/content.bad.json --check-only 2>&1); rc=$?
echo "$out"
[ $rc -eq 0 ] || fail "warnings-only content was rejected"
echo "$out" | grep -q "fails Freshness" || fail "stale-news warning did not fire"
echo "$out" | grep -q "an item in Cut for cause gets no chip" || fail "cut-vs-chip warning did not fire"
echo "$out" | grep -q "toplead: .* words (budget 45)" || fail "toplead length warning did not fire"

echo; echo "== 4. render the good fixture =="
python3 scripts/render_briefing.py --content tests/fixture_content.json || exit 1
echo; echo "SMOKE OK — open run/briefing-2026-09-10-0845.html"
