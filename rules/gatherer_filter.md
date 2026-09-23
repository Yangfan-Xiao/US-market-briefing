# GATHERER FILTER CARD — the condensed gate for gather subagents

The full rules (`rules/impact_filter.md`, `rules/writing_rules.md`) bind the orchestrator, deep-dives and
QC. Gatherers read only this card: it carries every threshold you apply. You are the FIRST gate —
when unsure, return BORDERLINE; never cut silently.

## The reader
Buys near-the-money 7–30 DTE vertical debit spreads on a fixed watchlist; holds up to ~10 sessions;
exits before binary events. An item matters only if it changes what that holder does inside the
hold window (avoid opening, exit before a date, manage a short leg).

## Rubric (A) — an item needs all four
1. **Magnitude** — plausibly >1% on the affected name, or >0.3% on SPY/QQQ (yardstick: past reactions
   to the same kind of event, not how loud the coverage is).
2. **Not priced in** — priced-in requires the substance to be public before the prior session's close
   AND the name to have already moved on it. Same-day/overnight news is never priced in. A scheduled
   event's outcome is never priced in.
3. **Fresh** — still repricing, OR gates a dated forward event inside the hold window (then scope the
   line to that forward date — a 1–3-day-old story with a dated pivot passes).
4. **Forward consequence** for a watchlist holder inside the hold window.
Reach (single name < sector < broad tape) ranks items; for a name not in the headline, state the
channel (supplier, customer, competitor, index weight, rate sensitivity, input cost). "Sector
sympathy" is not a channel.

## Event test
Name actor + action + date/time ET + the document or statement. A price move alone is not an event —
find the trigger; none in Tier 1/2 → CUT "no driver identified" (unless it is the reversal of a known
trigger — then the trigger is the item). Exception: a state variable flagged in the pack's PROMOTION
CANDIDATES is an event by itself; never drop it for lacking a cause ("driver contested: A / B" or
"driver unidentified").

## Category gates (C) — hard numbers for plumbing / structure / filings
| Item | Passes only if |
|---|---|
| Treasury auctions | 10-yr / 30-yr, or QRA. 20-yr/TIPS only when duration is the day's story. 2/3/5/7-yr and bills: out unless a recent auction tailed badly AND rates drive the tape |
| Fed speakers | Chair, Vice Chairs, or a current voter, on the policy path, first time since a regime-relevant print. Blackout: one line on the session it starts/ends |
| Offerings / lockups / ATM | ≥5% of shares out, or any size where dilution IS the story. Shelf filings only when a takedown prices |
| Index events | announced add/delete/rebalance with an effective date inside the window (effective date, not announcement date) |
| Form 4 | cluster (≥3 insiders, same direction, ≤5 sessions), non-10b5-1 >~$5M, or a first open-market officer/director buy |
| 13D / 13G | new stake, ≥1pp change, or 13G→13D |
| Short interest | ≥10% of float AND ≥20% change (or borrow-fee spike) AND a stated in-window reason |
| Positioning (COT, prime brokerage) | context only, at stated extremes — never a card |
| Buyback blackout | program ≥~2% of shares/yr, only on the start/end session |
| Policy / fiscal deadlines | dated effect inside the window or ≤5 sessions past it |

## Hard exclusions (D)
Reiterations at an unchanged PT · recaps of yesterday's move · "stock X could" speculation / PT
think-pieces · items already in the pack's scheduled-events lists · famous-figure posts that change no
forecast or flow · routine plumbing (bills, short coupons, non-voters, 10b5-1 sales, RSU vests, passive
13G, shelf with no takedown, dividend at an unchanged rate) · announcements whose effective date is
outside the window · anything included only to look thorough.

## Sources
* **Tier 1** — filings (EDGAR), agencies (BLS/BEA/Census/Fed/Treasury), index providers, company IR /
  8-K, CME FedWatch, USTR/BIS/Federal Register, court dockets.
* **Tier 2** — exactly these outlets: Reuters, Bloomberg, WSJ, FT, AP, CNBC, Barron's, MarketWatch,
  Nikkei Asia; SCMP / Caixin for China policy only.
* **Tier 3** — everything else (Yahoo aggregation, Benzinga, Motley Fool, Kiplinger, Investopedia,
  MarketBeat, StockTitan, TipRanks, Seeking Alpha, ZeroHedge, blogs, X posts). A lead, never the
  grounding: re-ground in Tier 1/2 or return as BORDERLINE `unconfirmed`.
* Never fabricate a cause. Every KEEP/BORDERLINE line cites a source you actually opened, with its date.

## Search & fetch discipline (token budget)
* Triage from search-result snippets. Fetch a full page only for a candidate that could clear the gate,
  and fetch the Tier 1/2 original — never a Tier-3 page to "confirm" something.
* Prefer domain-restricted searches (the search tool's allowed-domains option, or `site:` operators)
  for the Tier 1/2 list above.
* Hard cap: 8 full-page fetches per gatherer, on top of your search budget.

## One-line phrasing (for KEEP/BORDERLINE)
Cause first: actor + action + date → mechanism → forward consequence; the price/vol reaction only as
a trailing parenthesis. Figures carry their basis (adj. vs GAAP; Yahoo/S&P Global vs Zacks) and source.
