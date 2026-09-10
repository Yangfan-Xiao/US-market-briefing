# GATHERER: symbols — single-name catalyst sweep for ONE watchlist group

Covers v1 Phases 8, 9 and 10 for the names listed in your pack (`run/pack_<group>.md`, 5–6 names).
Search budget: 1 baseline search per name + up to 6 follow-ups for the whole group (≤ 12 total).

## Procedure — two passes, not one search per angle

**Pass 1 — baseline scan (one search per name, all launched in parallel).**
Query: `<Company name> <TICKER> news` restricted to the last 48 hours (use the search tool's recency
if available; otherwise include the month and day). Read the result list, open at most two articles
per name, and decide: does anything here plausibly clear the IMPACT FILTER, or come close (BORDERLINE)?
Many names on many days produce nothing — they get a CONSIDERED line ("nothing material found") and
no KEEP/BORDERLINE line. ETFs in your group (SPY, QQQ, IWM, USO): search the driver, not the ticker — "S&P 500
ETF flows / rebalance news" for SPY/QQQ/IWM, "crude oil ETF USO news" for USO.

**Pass 2 — follow-ups (only where Pass 1 surfaced a candidate; ≤6 for the group).**
For each candidate: (a) find the primary or Tier-2 grounding (company IR / 8-K / court docket /
Reuters / Bloomberg) if Pass 1 only gave Tier 3; (b) pin the date, time (ET) and the concrete
figures; (c) if the candidate is a price move, find the trigger — no trigger in Tier 1/2 → cut as
"move without identified driver". Do not spend follow-ups on names with nothing.

## What counts (from v1)
Product launches, conferences/keynotes with a date, regulatory/court decisions, M&A, major investment
commitments, company guidance & operating updates (capex plans, delivery/production/shipment numbers,
unit/subscriber/bookings metrics, pre-announcements, guidance raises or cuts), analyst PT/rating
changes (mostly priced-in noise — run through the filter; a reiteration at an unchanged PT is a
hard exclusion), unusual move → identify the TRIGGERING EVENT and report the trigger. A dated
operating release inside the window (deliveries, monthly sales) is a CALENDAR FACT as well.

## Earnings context (only for names whose pack entry shows earnings inside the hold window)
Do not search for the date — it is API-confirmed in the pack. Do one search for the setup: what the
Street is focused on (one clause), the consensus with its basis, and any pre-announcement. Flag a
conflict if a Tier 1 source (company IR) shows a different date from the pack.

## Forward dates (cheap and valuable — capture them while reading)
While reading Pass 1 results, note every DATED forward event for your names inside the hold window
or just past its edge: conference/keynote appearances, product events, court/agency dates, votes,
lockup tranches, operating-data releases, investor days. Return them under CALENDAR FACTS with the
source, even if the underlying story is a few days old — a dated pivot inside the window is what
keeps an older story relevant ("gates a forward event").

## Audit trail
Every name in your group gets exactly one CONSIDERED line (what you searched, disposition). A
name with nothing material is "nothing material found" — that line never reaches the page, but it
proves the name was covered.

## Cross-impact hint
If a headline about a non-watchlist company clearly transmits to one of your names through a stated
channel (supplier, customer, competitor, regulator), you may return it scoped to your name with the
channel named. Do not return generic "sector sympathy".
