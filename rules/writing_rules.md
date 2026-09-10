# WRITING & DATA RULES (v2 — carried from v1 with the continuity rules removed)

## Who reads this and how they trade (frame everything around this)

* Near-the-money, 7–30 DTE vertical debit spreads, directional, on a fixed watchlist (`config/watchlist.json`). A net premium buyer; every spread has a short leg that can be assigned.
* Based in Shanghai (GMT+8); active window 8pm–12am GMT+8 ≈ the first hours of the US session.
* Holds up to ~10 trading sessions or until 7 DTE — so dated events days ahead matter for managing open trades, not just for new entries.
* Exits before binary events unless there is a strong reason to bet on them.

## Data rules

* Anchor every time to both ET and GMT+8 (the renderer converts clock times automatically; write ET in `time_et` and let the template add GMT+8; in prose give both).
* No technicals. No chart levels, EMAs, RSI, MACD, support/resistance, price targets, VWAP, IV, put/call, OI walls. The reader handles all of that on his own charts.
* No trade recommendations or directional calls. Concise and factual; lead with what matters most. Don't pad names that have no catalyst.
* Market-conditions numbers come ONLY from `run/market.json` (rendered automatically). Never type an index level, yield, oil price or Fear & Greed value into prose from a web page; if a prose sentence needs one, copy it from `run/market.json`.
* Every consensus figure names its basis and source ("EPS $1.74 adj., Yahoo/S&P Global" — not "$1.74"). GAAP vs adjusted mixing is the most common factual error in past briefings.
* Every earnings date for a watchlist name must match `run/events.json` (API-confirmed) or be explicitly marked "unconfirmed — company IR not yet published". The renderer rejects a mismatch.

## Stateless by design

Each briefing is written from scratch for its own coverage window. Never reference a previous briefing, never use "day N", "UPDATE", "NEW", "RESOLVED", "carry-over", "as flagged yesterday". A story that has been running for weeks is described by its current state and its next dated pivot, nothing else. (The renderer rejects continuity tokens.)

## Writing rules (every printed line — toplead, Heads-up, News, Symbol bullets, timeline "why", tone, Bottom line)

* **Toplead = a thesis, not a question.** One declarative sentence naming (a) the single dominant driver of the coverage window, (b) the mechanism by which it moves the tape, and (c) when/how it resolves or what would invalidate it. Banned constructions: "whether …", "if …", "watch if/for", "eyes on", and any sentence whose content reduces to "the market could go either way on X" — that is chart-watching, which the reader does himself. Litmus test: if the sentence would be equally true on a day the driver rallies and a day it dumps, rewrite it.
  – Bad: "whether the weak July jobs report cements September rate-cut pricing"
  – Good: "Sept rate-cut repricing drives the tape: July payrolls −23K vs +83K consensus with −103K back-revisions (printed 8:30 ET) — invalidated only if Fed speakers push back; next test is the Aug 12–13 auctions."

* **Cause first, tape last.** Every line leads with the causal event — actor + action + date + mechanism — and its forward consequence. A price or volatility move may appear only as a trailing parenthesis quantifying the reaction, never as the subject of the sentence. A line whose only content is a move plus a vague attribution ("on capex concerns") fails: either name the concrete trigger (which document / statement / decision, from whom, when) or send the item to Cut for cause as "move without identified driver". Never invent or upgrade a speculative attribution to fill the slot. (One deliberate exception: a promoted state variable — there the level-crossing itself is the event and may lead the sentence.)

* **Card titles name the causal event, not the price pattern.** "OpenAI IPO-delay report keeps AI-capex financing in question", not "AI sell-off — follow-through risk".

* **Overhang lines state a resolution condition or review date.** An undated risk with no way to resolve is not printable.

* **Bottom line** — 1–2 sentences: risk posture, the driver statement, the next dated pivot(s), the specific moment to be careful, and any short-leg management note (ex-div / assignment). Declarative throughout.

* Light markup only: `**bold**` for the key phrase. No HTML, no links, no other markdown. The renderer escapes everything else.

## Tag taxonomy (fixed vocabulary — pills never carry freeform text)

Pills (symbol cards): `⚠ binary` · `overhang` · `flow` · `capital return` · `ex-div` · `[FILED]` · `[REPORTED]` · `rumor · unconfirmed`
* ⚠ binary — dated event with gap risk: earnings, top-tier macro, court or agency decision with a date.
* overhang — live UNDATED risk narrative; the line must state a resolution condition or a review date.
* flow — mechanical supply/demand: index add/delete, lockup, rebalance, settlement.
* capital return — buyback live or blackout, dividend initiation or rate change.
* ex-div — ex-dividend date + the early-assignment note.
* [FILED] / [REPORTED] — filing-grounded fact vs. named-source reporting.
* rumor · unconfirmed — unverified chatter; always name the platform in the text.
Descriptors like "customer loss" or "leadership exodus" belong in the summary sentence, never on the pill.

Calendar chips: `e-bin` (dated binary) · `e-macro` (auctions, QRA, Fed speakers, central banks, policy deadlines, second-tier data) · `e-exdiv` · `e-flow` (index adds, rebalance flows) · `e-struct` (blackout starts/ends, lockups, offerings, splits, OpEx/witching, half-days) · `e-pos` (capital-return events) · `e-quiet` (only when a day has nothing).

Heads-up card colour (`kind`): `bin` (dated binary) · `macro` (rates/plumbing/state-variable) · `flow` · `news` (unscheduled headline) · `exdiv`. Badge (`badge_class`): `b-bin` "Binary · top-tier" · `b-name` "Single-name binary" · `b-broad` "Broad tape" / "Broad · rates" / "Sector · semis" · `b-exdiv` "Carried positions".

## Source hierarchy (what counts as grounding)

* Tier 1 — primary / official (preferred; cite whenever available): EDGAR full-text search and filings, BLS / BEA / Census, federalreserve.gov (speeches, minutes, H.4.1), home.treasury.gov (QRA documents, auction results), index-provider announcement pages (S&P DJI, Nasdaq, FTSE Russell), company IR / 8-K, CME FedWatch, USTR / BIS / Federal Register for trade actions, court dockets for rulings, official statistical releases.
* Tier 2 — major wires: Reuters, Bloomberg, WSJ, FT, AP, CNBC.
* Tier 3 — leads only, NEVER the sole grounding for a page item: Benzinga, Motley Fool, FXLeaders, TradingKey, MarketBeat, StockTitan, ZeroHedge, HNGN, Yahoo aggregation pages, DigiTimes-via-blogs, and similar SEO/aggregator outlets. A Tier-3-only finding is re-grounded in Tier 1/2 during the run, or tagged [REPORTED — unconfirmed] and gated harder, or cut.
* Every `source` line names the highest-tier source actually used, with its date.

## Anti-bloat caps (enforced by the renderer where mechanical)

* Heads-up: max 5 cards. News: max 6, highest impact first — fewer is correct; may be empty.
* Symbol catalysts: only names with a live, gated catalyst; no "nothing to report" rows. Prefer adding a bullet to an existing card over opening a new one; max 4 bullets per card.
* Plumbing / corporate-structure / filings items combined: at most 4 page items (a Heads-up card, a News line, or a symbol card that exists only because of them). Timeline rows and calendar chips are exempt, but no calendar day carries more than 4 chips.
* Every line carries information the reader would act on. No restatement, no hedging filler, no padding.
