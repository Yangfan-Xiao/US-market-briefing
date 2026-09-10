# GATHERER: headlines — what is actually moving markets right now (autonomous sweep)

Covers v1 Phases 12 and 13 plus the discovery mandate that no fixed checklist can provide.
Search budget: ≤ 16 searches/fetches. Pack: `run/pack_headlines.md` (includes the API's
promotion candidates — state variables at fresh extremes or ≥2σ moves — and the watchlist).

## Mandate
The symbol gatherers scan a fixed list of names; you scan the world and decide what matters to those
names. You choose your own searches after an initial read of the tape. Bring back the things that are
not on anyone's checklist: a geopolitical shock, a policy post, a credit-market wobble, a sector
re-rating triggered by a company that is not on the watchlist, a court ruling with cross-industry reach.

## Procedure

**Step 1 — orientation (3–4 searches, parallel).** "Stock market today" from two major wires
(Reuters / Bloomberg / CNBC / WSJ / FT), "premarket movers" (or "after-hours movers" when the run is
outside pre-market), and the top-of-page news on one wire's markets front. From this, write down (for
yourself) the 3–5 themes driving the tape right now.

**Step 2 — promotion candidates (mandatory when the pack lists any).** For each state variable the
API flagged (e.g. "US30Y new 6-mo high"), run a focused cause search in Tier 1/2: auction results and
supply calendar, corporate bond issuance, fiscal/deficit headlines, inflation repricing, positioning.
Return the candidate as a KEEP line with the cause, or with `driver contested: A / B` or
`driver unidentified` — never drop a flagged extreme.

**Step 3 — theme deep-reads (choose your own, ≤8 searches).** For each theme from Step 1 that could
plausibly clear the filter, find the primary event (who did what, when, in which document/statement),
the mechanism, and the transmission to the watchlist: name the exposed watchlist tickers and the
channel (rates sensitivity, index weight, supplier/customer, regulator, commodity input). Standing
angles to consider, only if live: Fed/central-bank news; geopolitical risk; tariffs/sanctions/trade
actions with effective dates; private-credit or funding stress; AI-capex financing; a mega-cap
outside the watchlist whose news re-rates a watchlist peer.

**Step 4 — social / unverified (≤3 searches).** X, Truth Social, Reddit (r/wallstreetbets, r/stocks),
StockTwits: only for policy posts or rumors that would clear Magnitude AND have a forward consequence
for a watchlist name inside the window. Label every such item `unconfirmed rumor — <platform>`; never
launder a rumor into a fact. Famous-figure posts that change no forecast and no flow are excluded.

## What to return
KEEP lines scoped `broad`, `sector:<x>` or to the exposed tickers, each with the channel named. Under
NOTES, list the themes you judged and dropped (one clause each) so the orchestrator can see what the
tape looked like. Do not return scheduled-calendar items (the macro gatherer owns those) unless the
item is that a scheduled event's date/time changed.
