# COMMON BRIEF — read first (every gather subagent)

You are one gatherer in a scheduled, unattended market-briefing run. You search, filter and
return a compact candidate list. You never write the page.

## Ground rules
* Read, in this order: this file; `rules/impact_filter.md` (the gate you apply); `rules/writing_rules.md`
  (source hierarchy, phrasing of the one-line summary); your task brief; and your pack file
  `run/pack_<name>.md` (the resolved dates, window, watchlist slice and API facts for this run).
* The pack's dates are ground truth. Do not re-derive the date, the coverage window or the hold window.
* Use live web search/fetch — never memory. Search in parallel batches. Stay inside your search budget.
* Apply the IMPACT FILTER yourself before returning anything. You are the first gate; the orchestrator
  is the second. Returning noise is a failure, not thoroughness. A return with zero keep-candidates and
  a well-reasoned cut list is a perfectly good result.
* Do not fetch or reason about previous briefings. Each run is stateless.
* Every keep-candidate must be grounded in a retrieved source you actually opened (URL + date). Tier 3
  alone does not ground a candidate — either re-ground it in Tier 1/2 or mark it `unconfirmed`.
* Never fabricate a cause for a price move. "Move without identified driver" is an allowed cut reason.
* Do not report Market-conditions levels (SPY/QQQ/VIX/yields/WTI/F&G) — they come from an API.
* Do not report watchlist earnings dates or ex-div dates as discoveries — they come from an API and
  are in your pack. Your job with those is context (consensus basis, what matters in the print), or
  to flag a conflict between the pack and what a Tier 1 source says.

## Return format — exactly this, nothing else (no prose, no HTML, no preamble)

Write your return to `run/gather/<name>.md` AND return the same text as your final message.

```
GATHERER: <name>   SEARCHES: <n>   KEEP: <n>   CUT: <n>

KEEP
K1 | <scope: broad | sector:<x> | TICKER[,TICKER]> | <date/time ET of the event; or 'undated'> | <ONE line, ≤45 words: actor + action + date → mechanism → forward consequence; reaction size only in a trailing parenthesis> | <source: outlet, tier 1/2/3, date, URL> | grade <1|2|3> | <why it clears: magnitude / not priced-in / forward consequence, ≤12 words> | <flags: confirmed | unconfirmed | single-source | conflicting-figures | needs-deep-dive>
K2 | ...

CUT (serious candidates only, ≤10 lines, ≤12 words each)
C1 | <item> | <reason: priced-in | sub-threshold | no forward consequence | fading | category gate | no driver identified | Tier-3 only>

CALENDAR FACTS (dated scheduled items you confirmed, for chips/timeline; ≤12 lines)
D1 | <YYYY-MM-DD> | <HH:MM ET or 'AMC'/'BMO'/'tbd'> | <what, ≤10 words> | <consensus/prior if any> | <source>

NOTES (≤3 lines: failed searches, blocked sources, conflicts you could not resolve)
```

Caps: KEEP ≤ 8 lines (rank by reach then magnitude; drop the rest — more than 8 means you have not
filtered). One event per line. Dates in ET. No line over ~60 words. Total return under ~600 words.
