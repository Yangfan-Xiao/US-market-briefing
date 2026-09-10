# GATHERER: flows — corporate structure, index flow, filings, positioning, ETF distributions

Covers v1 Phases 6 (ETF part), 7 and 11. Search budget: ≤ 14 searches/fetches. Pack: `run/pack_flows.md`.
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
9. **Filings** (named-source, fresh-only): 13D/13G new stakes or ≥1pp changes; Form 4 clusters (≥3
   insiders, same direction, 5 sessions) or non-10b5-1 sales > ~$5M or first open-market officer buys;
   8-K surprises (material agreements, CEO/CFO departures, auditor changes, guidance withdrawal);
   424B pricings. Start with MSTR, COIN, TSLA, NVDA, PLTR, SPCX, then a general sweep.
10. **Short interest / borrow** for MSTR, SPCX, HOOD, PLTR, COIN, NBIS — only at the gate thresholds
    (≥10% of float AND ≥20% change, or a borrow-fee spike) and only with a stated in-window reason.
11. **Positioning** (context only, never a card): Goldman prime-brokerage weekly read as echoed by
    Reuters/Bloomberg/CNBC; CFTC COT on ES/NQ when the weekly shift is extreme; ETF creation/redemption
    anomalies for SPY/QQQ/IWM from named sources.

## Tagging
Filing-grounded → `[FILED]`; named-source reporting → `[REPORTED]`; anything not both fresh-in-window
and named-source is omitted. Effective date, not announcement date, decides the day an item belongs to.
