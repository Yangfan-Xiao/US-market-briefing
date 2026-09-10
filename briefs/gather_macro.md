# GATHERER: macro — scheduled macro, Fed/Treasury plumbing, market structure, policy deadlines

Covers v1 Phases 2, 3 and 4. Search budget: ≤ 16 searches/fetches. Pack: `run/pack_macro.md`.

**Already computed for you (in the pack, from APIs/rules — do NOT re-search, but DO carry them into
CALENDAR FACTS with any consensus/context you find):** Treasury coupon auctions with sizes and the
gate flag; FOMC meeting/decision/minutes/blackout dates; monthly OpEx, quad witching, VIX settlement,
month/quarter-end; projected ETF ex-div dates. Your budget goes to the things that only a search
can establish: data-release dates/times/consensus, Fed speakers, other central banks, policy deadlines,
and whether a recent auction tailed.

## What to establish (all dates/times in ET)

1. **Coverage-window releases.** Every US data release scheduled inside the coverage window (pack gives
   the exact start/end), with exact time, consensus and prior. Sources: BLS/BEA/Census release
   calendars (Tier 1), a wire's "US data this week" (Tier 2), or an economic-calendar page (e.g.
   TradingView, Trading Economics — cross-check against a second source). Mark top-tier releases
   (CPI, PPI, PCE, NFP, FOMC decision/minutes, retail sales, ISM Mfg & Services, GDP, UMich/Conf. Board).
2. **Hold-window release sweep — a checklist, not a judgement.** For every trading day in the hold
   window (pack lists them), locate the scheduled US releases and return each top-tier one under
   CALENDAR FACTS with date, time ET, consensus and prior. Checklist to tick off explicitly (state
   "not in window" for absent ones under CONSIDERED): CPI · PPI · PCE/personal income · NFP · retail
   sales · ISM Manufacturing · ISM Services · GDP · UMich sentiment (prelim = 2nd Friday, final = 4th
   Friday, 10:00 ET) · Conference Board confidence · JOLTS · weekly jobless claims (every Thu 08:30) ·
   housing starts/permits · durable goods · Philly/Empire Fed · Treasury refunding (QRA). Sources: BLS
   and Census release schedules (Tier 1), sca.isr.umich.edu, ismworld.org, conference-board.org; a
   wire's weekly calendar as the cross-check.
3. **FOMC.** Next meeting date(s); decision / SEP / presser / minutes / Beige Book times if inside the
   window. Communications blackout: does it start or end inside the window (starts the second Saturday
   before an FOMC, ends the Thursday after). Current market-implied odds for the next decision (CME
   FedWatch, Tier 1) — one line.
4. **Fed speakers** inside the window — apply the CATEGORY GATE (Chair / Vice Chairs / voters only,
   policy-path relevance). Give name, role, voting status, date/time.
5. **Treasury supply.** Coupon auctions in the window (3y/10y/30y, 20y, TIPS) with auction and results
   times; whether the most recent 10y/30y tailed (Treasury results PDF or Tier 2). Quarterly Refunding
   Announcement date if in window. Apply the CATEGORY GATE (10y/30y only unless duration is the story).
6. **Other central banks with US spillover** in the window: ECB, BoJ, BoE — decision date/time ET.
7. **Market structure.** Monthly OpEx and quad-witching dates; VIX monthly settlement (the Wednesday
   30 days before next month's standard SPX expiry); month-end / quarter-end rebalance dates —
   which fall inside the window. Confirm holidays/early closes in the window against the NYSE calendar
   only if the pack flags a holiday (the pack's calendar is authoritative otherwise).
8. **Fiscal / policy / trade deadlines** with a dated effect inside the window or ≤5 sessions past its
   edge: funding deadlines, debt-ceiling dates, tariff/sanction effective dates, court or agency
   deadlines with market consequence, OPEC+ meetings, EIA weekly (only if oil is a live driver).

## What to return as KEEP (through the filter)
Only items that would change what the reader does: a top-tier print inside the coverage window; an
FOMC event; a gated auction when rates are a live driver; a policy deadline with a dated effect;
a central-bank decision with US spillover. Everything else that is merely scheduled goes under
CALENDAR FACTS, not KEEP.

## Consensus discipline
Every consensus figure carries its source and, for earnings-like figures, its basis. Prior values
carry the release they came from. If two sources disagree, return both with the flag `conflicting-figures`.
