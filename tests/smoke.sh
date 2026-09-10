#!/usr/bin/env bash
# smoke.sh — verify the deterministic parts end-to-end without any LLM work.
# 1) coverage-window self-tests  2) live market data  3) render the fixture for a simulated run
set -u
cd "$(dirname "$0")/.."
echo "== 1. session_window self-test =="; python3 scripts/session_window.py --selftest || exit 1
echo; echo "== 2. simulated run start (fixture is written for Thu 2026-09-10 08:45 ET) =="
python3 scripts/session_window.py --at 2026-09-10T08:45 >/dev/null || exit 1
python3 scripts/market_data.py | tail -3
# the fixture's earnings dates are frozen in time; drop live events.json so the guard does not fire on stale data
rm -f run/events.json
echo; echo "== 3. validator must REJECT the bad fixture =="
python3 - <<'PY'
import json,copy
c=json.load(open('tests/fixture_content.json'))
b=copy.deepcopy(c); b['timeline'][3]['date']='2026-09-09'; b['toplead']='Whether the tape bounces is the question.'
json.dump(b,open('run/content.bad.json','w'))
PY
python3 scripts/render_briefing.py --content run/content.bad.json --check-only && { echo "FAIL: bad fixture accepted"; exit 1; }
echo; echo "== 4. render the good fixture =="
python3 scripts/render_briefing.py --content tests/fixture_content.json || exit 1
echo; echo "SMOKE OK — open run/briefing-2026-09-10-0845.html"
