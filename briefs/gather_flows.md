# GATHERER: flows — corporate structure, index flow, filings, positioning, ETF distributions

Covers v1 Phases 6 (ETF part), 7 and 11. Search budget: ≤ 12 searches/fetches. Pack: `run/pack_flows.md`.
The filings sweep is done by script (EDGAR API → the pack's "SEC filings" section) — you read and gate
those rows instead of searching for filings; spend the saved budget on items 5, 6 and 11.
Every item here must pass the CATEGORY GATES in `rules/impact_filter.md` §C — they are hard numbers.

## What to establish

1. **ETF distributions.** The pack lists PROJECTED ex-div dates for SPY / QQQ / IWM (from last
   year's pattern). Confirm each projected date that falls inside the hold window on the issuer's own
   page (SSGA distribution schedule / Invesco / iShares) — one fetch each — and return the confirmed
   date and amount (or "amount TBD until declaration date") under CALENDAR FACTS. If the issuer page is
   stale or unreachable, return the projected date marked "projected — issuer page not updated"; never
   drop it. USO makes no regular distributions.
2. **Stock ex-dividends in the pack** — verify the amount for any in-window ex-date (the API gives the
   date, not the amount). One search each; NVDA's $0.01 needs no verification.
3. **Buyback blackouts.** From the pack's confirmed earnings dates, which watchlist names with a
   repurchase program ≥ ~2% of shares outstanding annually enter or exit a blackout inside the window
   (conventional window ≈ 4 weeks before the report through ~2 sessions after). Report the mechanical
   loss/return of the corporate bid, never the blackout as a story.
4. **New or expanded buyback authorisations, ASRs, dividend initiations or rate changes** announced
   inside the window (8-K / press release).
5. **Lock-up expirations, follow-ons, ATMs, convertibles, priced shelf takedowns** across the watchlist,
   with size as % of shares outstanding and the date. SPCX (post-IPO lockup series) and MSTR
   (ATM-funded) are standing checks every run.
6. **Index events.** S&P 500 / Nasdaq-100 / DJIA adds, deletes, rebalances; Russell reconstitution —
   only with an effective date inside the window, grounded in the index provider's own announcement.
7. **Splits, spin-offs, M&A closings/termination dates, ticker changes** with a dated event in window.
8. **Dated non-earnings corporate events**: investor/analyst days, product keynotes, shareholder
   meetings, scheduled operating-data releases (deliveries, monthly units, subscriber prints).
9. **Filings — from the pack, not from search.** The pack lists every watchlist 8-K/6-K (with item
   codes), 13D/13G, S-3/424B and 144 filed in the last few sessions, plus Form 4 counts, each with its
   EDGAR URL (Tier 1). Open only the rows that could clear a CATEGORY GATE: 8-K items 1.01/1.02/2.01/
   2.03/2.05/2.06/4.01/4.02/5.01/5.02/7.01/8.01; any 13D or 13G; any 424B (size as % of shares out); a
   Form 4 count ≥3 (check the cluster gate on the filings: same direction, non-10b5-1). If the pack
   reports EDGAR errors for some names, sweep only those names by search (EDGAR full-text search).
10. **Short interest / borrow** for MSTR, SPCX, HOOD, PLTR, COIN, NBIS — only at the gate thresholds
    (≥10% of float AND ≥20% change, or a borrow-fee spike) and only with a stated in-window reason.
11. **Positioning** (context only, never a card): Goldman prime-brokerage weekly read as echoed by
    Reuters/Bloomberg/CNBC; CFTC COT on ES/NQ when the weekly shift is extreme; ETF creation/redemption
    anomalies for SPY/QQQ/IWM from named sources.

## Tagging
Filing-grounded → `[FILED]`; named-source reporting → `[REPORTED]`; anything not both fresh-in-window
and named-source is omitted. Effective date, not announcement date, decides the day an item belongs to.
