# GATHERER: crossimpact — out-of-scope news that transmits to the watchlist

Search budget: ≤ 12 searches + the fetch cap in the filter card. Pack: `run/pack_crossimpact.md`
(read-through earnings from the API, the standing theme clusters from `config/exposure_map.json`, the
market snapshot and the watchlist).

## Mandate
The symbol gatherers search the watchlist names themselves; the headlines gatherer reads the whole tape.
You cover the gap between them: **companies, counterparties and policy threads that are NOT on the
watchlist but move a watchlist name through a stated channel** — a supplier's earnings, a customer's
capex cut, a peer's guidance, an export-control ruling, bitcoin-ETF flows. Every line you return is
scoped to the exposed watchlist tickers with the channel named: `NVDA(HBM supplier),AMD(HBM supplier)`.
Never return a watchlist name's own news.

## Procedure

**Step 1 — read-through earnings (≤ 4 searches, parallel).** The pack lists non-watchlist earnings in
the coverage window, the hold window and just past it, already dated by the API. Do not re-search the
dates. For each one in the **coverage** window, and for the 2–3 biggest in the **hold** window (by market
cap and by how many watchlist names they touch):
* what the Street is focused on — the single metric that transmits to the watchlist names (e.g. Micron:
  HBM pricing and AI-memory guidance → NVDA/AMD capacity; Costco: comps and tariff pass-through → WMT);
* the consensus with its basis (the pack's EPS figure is Zacks — name it);
* for a report that has ALREADY printed (before run start): actual vs consensus and the guidance line,
  then judge whether the read-through is still repricing the exposed names.
Return a KEEP for a report inside the coverage window or a printed report still repricing; every other
read-through report goes under CALENDAR FACTS (the orchestrator turns them into `e-read` chips).

**Step 2 — theme clusters (one search per cluster that is live, ≤ 6 searches).** For each cluster in
the pack, run ONE search over the last 48 hours on Tier 1/2 domains combining its angles, e.g.
`(TSMC revenue OR export controls OR hyperscaler capex OR OpenAI financing) chips` restricted to
reuters.com / bloomberg.com / cnbc.com. Skip a cluster whose search returns nothing new. For a hit:
find the primary event, the date, the mechanism, and name the exposed watchlist tickers and channel.

**Step 3 — out-of-watchlist movers (1–2 searches).** "premarket movers" / "biggest stock movers today"
(Tier 2). For any non-watchlist company moving ≥5% on news, with a market cap above ~$50B or a stated
channel in the exposure map, find the trigger and decide whether it transmits to a watchlist name
(supplier/customer/peer re-rating). A move with no channel → CUT "no watchlist channel".

## What to return
The standard format from `briefs/_common.md`. KEEP/BORDERLINE lines are scoped to exposed tickers with
channels. CALENDAR FACTS carry every read-through report in the hold window you confirmed or added
context to, as `D<n> | date | BMO/AMC | <TICKER> earnings → <exposed tickers> | cons (basis) | source`.
Under CONSIDERED, one line per theme cluster and per read-through report you looked at. Under NOTES,
list clusters you skipped as quiet.
