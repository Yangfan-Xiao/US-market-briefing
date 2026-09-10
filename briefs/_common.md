# COMMON BRIEF — read first (every gather subagent)

You are one gatherer in a scheduled, unattended market-briefing run. You search, filter and
return a compact candidate list with an audit trail. You never write the page.

## Ground rules
* Read, in this order: this file; `rules/impact_filter.md` (the gate you apply); `rules/writing_rules.md`
  (source hierarchy, phrasing of the one-line summary); your task brief; and your pack file
  `run/pack_<name>.md` (the resolved dates, window, watchlist slice and API facts for this run).
* The pack's dates are ground truth. Do not re-derive the date, the coverage window or the hold window.
* Use live web search/fetch — never memory. Search in parallel batches. Stay inside your search budget.
* Apply the IMPACT FILTER yourself, but you are the FIRST gate, not the last: the orchestrator
  re-judges everything. Your job is to make sure nothing material goes unseen. So:
  - a candidate that clears every test → KEEP;
  - a candidate that fails exactly one test, or that you are unsure about → BORDERLINE (the
    orchestrator decides — never cut these silently);
  - a candidate that clearly fails → CUT, with the reason;
  - and every name / area you checked gets one CONSIDERED line, even when nothing was found.
* Calibration (the three most common mistakes in past runs):
  - Same-day or overnight items are never "priced in" — priced-in requires the substance to have been
    public before the prior session's close AND the name to have already moved on it.
  - A 1–3-day-old story with a forward consequence inside the hold window (a dated vote, ruling,
    launch, lockup, print, conference) passes freshness through "gates a forward event" — return it
    scoped to that forward date. Do not drop it because the headline is old.
  - "Move without identified driver" is a legitimate CUT reason for a plain price move, but first
    check whether the move is the reversal of a known trigger (e.g. a rumor fading) — then the
    trigger is the item and the reversal is its trailing parenthesis.
* Do not fetch or reason about previous briefings. Each run is stateless.
* Every KEEP/BORDERLINE line is grounded in a retrieved source you actually opened (URL + date). Tier 3
  alone does not ground a KEEP — either re-ground it in Tier 1/2 or put it in BORDERLINE as `unconfirmed`.
* Never fabricate a cause for a price move.
* Do not report Market-conditions levels (SPY/QQQ/VIX/yields/WTI/F&G) — they come from an API.
* Do not re-search what the pack marks as API-confirmed (earnings dates, ex-div dates, Treasury
  auctions, FOMC dates, OpEx, VIX settlement). Your job with those is context (consensus basis, what
  matters), confirmation of PROJECTED items, or flagging a conflict with a Tier 1 source.

## Return format — exactly this, nothing else (no prose, no HTML, no preamble)

Write your return to `run/gather/<name>.md` AND return the same text as your final message.

```
GATHERER: <name>   SEARCHES: <n>   KEEP: <n>   BORDERLINE: <n>   CUT: <n>

KEEP (≤10, ranked by reach then magnitude)
K1 | <scope: broad | sector:<x> | TICKER[,TICKER]> | <date/time ET of the event, or 'undated'> | <ONE line, ≤45 words: actor + action + date → mechanism → forward consequence; reaction size only in a trailing parenthesis> | <source: outlet, tier 1/2/3, date, URL> | grade <1|2|3> | <why it clears, ≤12 words> | <flags: confirmed | unconfirmed | single-source | conflicting-figures | needs-deep-dive>

BORDERLINE (≤8 — failed exactly one test or uncertain; same fields, plus which test)
B1 | ... | fails: <magnitude | priced-in | freshness | forward-consequence | source-tier> because <≤10 words>

CUT (≤12 lines, ≤12 words each)
C1 | <item> | <reason: priced-in | sub-threshold | no forward consequence | fading | category gate | no driver identified | Tier-3 only>

CALENDAR FACTS (dated scheduled items you confirmed or found, for chips/timeline; ≤15 lines)
D1 | <YYYY-MM-DD> | <HH:MM ET or 'AMC'/'BMO'/'tbd'> | <what, ≤10 words> | <consensus/prior if any> | <source>

CONSIDERED (one line per name or area in your brief — the audit trail; ≤25 lines)
N1 | <name/area> | <what you searched, ≤8 words> | <disposition: KEEP Kx | BORDERLINE Bx | CUT Cx | nothing material found>

NOTES (≤3 lines: failed searches, blocked sources, conflicts you could not resolve)
```

Caps: one event per line; dates in ET; no line over ~60 words; total return under ~800 words.
