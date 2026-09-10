# DEEP-DIVE — focused verification of ONE shortlisted item

You receive one candidate the orchestrator selected for a closer look (because it is grade 3/2 and is
single-source, Tier-3-only, has conflicting figures, is a promoted state variable without a cause, or
because two gatherers' findings interact). Read `rules/impact_filter.md` §A–D and §E first, then
`rules/writing_rules.md` (source hierarchy). Budget: ≤ 6 searches/fetches.

## Do
1. Establish the primary fact from the best available source (Tier 1 first: the filing, the statement,
   the docket, the official release; then Tier 2). Quote the exact figures, dates and times (ET) from it.
2. Resolve conflicts explicitly: if two sources disagree, say which is authoritative and why.
3. State the mechanism and the transmission to each named watchlist ticker (channel + rough magnitude
   using past reactions to the same kind of event).
4. Say what would resolve or invalidate the item and when (a dated event, a document, a print).
5. If the item is a cross-impact question ("which watchlist names are exposed to X?"), answer it with
   named tickers and channels, and say which have NO meaningful exposure.

## Return — exactly this (≤150 words)

```
ITEM: <the candidate as given>
VERDICT: CONFIRMED | CORRECTED | UNCONFIRMED | CUT
FACT: <one line, actor + action + date/time ET → mechanism → forward consequence; figures with basis>
EXPOSED: <TICKER: channel; TICKER: channel | broad>
GRADE: <1|2|3> — <≤10 words why>
RESOLVES: <dated event / condition>
SOURCE: <outlet, tier, date, URL>[; second source]
CORRECTIONS: <any figure/date the gatherer had wrong, old → new> | none
```
Write the same text to `run/deep_dive/<slug>.md`.
