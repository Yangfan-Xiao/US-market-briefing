# GATHERER: symbols — single-name catalyst sweep for ONE watchlist group

Covers v1 Phases 8, 9 and 10 for the names listed in your pack (`run/pack_<group>.md`, 5–6 names).
Search budget: 2 searches per name (≤ 12 for a 6-name group) + up to 6 full-page fetches for the whole
group. Searches are cheap; full pages are what cost tokens — spend on searches, economise on fetches.

## Procedure — two targeted queries per name, then follow-ups

**Pass 1 — two queries per name, all launched in parallel. Decide from the snippets.**
* **Q1 recency (Tier 1/2 only):** `<Company name> <TICKER>` restricted to the last 48 hours and to the
  Tier-2 outlet list in the filter card (use the search tool's allowed-domains / recency options; else
  `site:reuters.com OR site:bloomberg.com OR site:cnbc.com OR site:wsj.com` plus the month and day).
* **Q2 forward-dated:** `<Company name> (conference OR keynote OR "investor day" OR hearing OR ruling OR
  deadline OR launch OR vote OR lockup) <Month> <Year>` — any domain. This is how dated pivots inside the
  hold window get found (broker conferences with the CEO/CFO, court and agency dates, product events).
Read the snippets and decide per name: candidate (plausibly clears the filter or is BORDERLINE) or
nothing. Do not open articles in Pass 1. Many names on many days produce nothing — they get a
CONSIDERED line ("nothing material found") and no KEEP/BORDERLINE line.
ETFs in your group (SPY, QQQ, IWM, USO): search the driver, not the ticker — "S&P 500 ETF flows /
rebalance news" for SPY/QQQ/IWM, "crude oil supply news" for USO; Q2 becomes "index rebalance / OPEC+
meeting <Month> <Year>".
**Filings are already in your pack** (EDGAR API, Tier 1): read the listed 8-K items / 13D / 424B lines
for your names and treat a material one as a candidate — do not search for filings.

**Pass 2 — follow-ups (only where Pass 1 surfaced a candidate; ≤ 6 fetches for the group).**
For each candidate: (a) open the primary or Tier-2 grounding (company IR / 8-K from the pack / court
docket / Reuters / Bloomberg); (b) pin the date, time (ET) and the concrete figures; (c) if the
candidate is a price move, find the trigger — no trigger in Tier 1/2 → cut as "move without identified
driver". One fetch per candidate; do not spend follow-ups on names with nothing.

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
channel named. Do not return generic "sector sympathy". Read-through EARNINGS listed in your pack are
owned by the crossimpact gatherer — do not spend searches on them.
