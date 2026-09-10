# IMPACT FILTER — the gate every candidate must clear

Sections A–D are copied verbatim from the v1 prompt (Aug 2026) and are the binding criteria.
Section E is a weighing guide added in v2 — it explains how to apply A–D to a raw headline; it
never loosens them. Section F is the importance grade assigned AFTER an item has cleared the gate.

---

## A. IMPACT RUBRIC — SILENT GATE (the core filter)

Before any headline or catalyst earns a place, score it internally — never print the scores. Only items that pass the gate appear in the dashboard. For each candidate, judge:

1. Magnitude — plausibly moves price >1% on the affected name or >0.3% on a broad index? If no, cut.

2. Surprise / priced-in — genuinely new information, or already absorbed? A consensus-matching print, a reiterated rating, or a known-for-days story is priced in → cut, even if "important." Beats/misses matter only vs. expectations, not vs. the printed estimate. (Carve-out: a state variable still setting fresh extremes is not "known for days" — see the STATE-VARIABLE PROMOTION RULE; the extreme, not the trend, is the news, and freshness resets on each new crossing.)

3. Reach — single name, sector, or broad tape. Broad-tape items rank above single-name.

4. Freshness — still actively repricing, or fading? Fading → cut unless it gates a forward event. A release that printed earlier in the coverage window is judged here — still repricing → it's a News/conditions item with actual vs. consensus; absorbed → cut.

5. Forward consequence for me — affects a position I could open now or am already carrying within the hold window? No forward consequence → it does not go in, however interesting.

An item must clear Magnitude AND not be priced-in AND have a forward consequence to appear. Borderline → keep but compress to one clause. (Internal rule, never surfaced as a question.)

---

## B. STATE-VARIABLE PROMOTION RULE (extremes are events — the fix for metric-blindness)

The continuous state variables this briefing tracks — SPY, QQQ, VIX, the 2-yr / 10-yr / 30-yr yields and the curve, WTI, Fear & Greed — normally live as Market-conditions metric cards, and a metric card can never become the day's story no matter what level it crosses. That is a structural blind spot: a 19-year high in the 30-year yield is a session driver with no 8-K, no docket and no scheduled time attached. This rule is the promotion path:

* Promotion trigger — a tracked state variable is PROMOTED from metric to candidate story when, on or into the covered window, it (a) sets a fresh extreme against at least its trailing 6 months (longer lookbacks — "highest since 20XX" — promote a fortiori), or (b) moves ≥2σ of its trailing-month daily changes in one session or cumulatively over ≤5 sessions, or (c) is named by two or more Tier 1/2 sources as the session's primary equity driver. **In v2, triggers (a) and (b) are computed by `scripts/market_data.py` and listed under `promotion_candidates` in `run/market.json`; trigger (c) is judged by the headlines gatherer.**

* A promoted variable is treated as an EVENT dated to the crossing or move. The headlines gatherer (or a deep-dive) runs a focused cause search — Treasury auction results and supply calendar, corporate bond issuance (including AI-capex debt supply), fiscal/deficit headlines, inflation repricing, positioning — grounded per the SOURCE HIERARCHY.

* Rendering: a promoted variable earns a Heads-up card (macro colour class), and the toplead when it is the dominant driver, phrased per the WRITING RULES with the stated carve-out: the crossing itself is actor + action + date ("30-yr yield tops 5.33%, highest since 2007, on X and Y — feeds Z"). If the cause is contested or unidentified after the search, print the crossing anyway with "driver contested: A / B" or "driver unidentified" — a promoted extreme is NEVER routed to Cut for cause for lacking a tidy trigger; suppressing a multi-year extreme is a worse error than printing it without a clean cause. This honest-out applies ONLY to promoted state variables; ordinary single-name moves keep the cause-first rule.

* Cap: at most ONE promoted-variable Heads-up card per run — the biggest. Additional promoted variables ride the Conditions tone line. A promotion candidate that fails the rubric still gets its metric card's delta line annotated with the fact ("new 6-mo high") — the script does this automatically.

---

## C. CATEGORY GATES — extra thresholds for scheduled / mechanical items (plumbing, corporate structure, filings)

Plumbing, corporate-structure and filings items are mostly known in advance, which makes them the easiest way to bloat the page with things that are already in the price. They pass the rubric above AND these additional tests, or they do not appear. These gates are hard numbers, not judgement calls.

* Effective date, not announcement date. A mechanical event is judged on the session it TAKES EFFECT. An index add announced three weeks ago still qualifies on the day it goes effective and on no other day. Never re-run an announcement as news.

* Treasury auctions — only the 10-yr and 30-yr (and 20-yr / TIPS when duration is visibly the day's story), or the Quarterly Refunding Announcement. Bills, CMBs, FRNs and routine 2s/5s/7s are out unless a recent auction tailed badly AND rates are a live driver of the tape that session.

* Fed speakers — only the Chair, Vice Chair, Vice Chair for Supervision, or a current voting member, scheduled inside the session or window, AND either speaking for the first time since a regime-relevant data point or speaking on the policy path. Non-voters, repeats of a known stance, and ceremonial appearances are out. A communications blackout is worth one line only on the session it starts or ends.

* Buyback blackout — only for names running a repurchase program big enough to matter (roughly ≥2% of shares outstanding annually), and only on the session the blackout starts or ends inside the window. Derive the dates from the confirmed earnings dates in `run/events.json`; do not report a blackout as a standalone story.

* Offerings / lockups / dilution — only if ≥5% of shares outstanding, or any size for a name where dilution IS the live story (e.g. an ATM program funding a balance sheet). Shelf registrations count only when a takedown is priced or announced, not when the shelf is filed.

* Index events — only announced adds, deletes or rebalances with an effective date inside the window.

* Insider filings (Form 4) — only a cluster (≥3 insiders, same direction, within 5 sessions), a non-10b5-1 transaction over ~$5M, or a first open-market buy by an officer or director. Single scheduled 10b5-1 sales, RSU vests and tax withholding are out.

* 13D / 13G — only a new stake, a change of ≥1 percentage point, or a change of intent (13G → 13D). Passive re-filings and routine amendments are out.

* Short interest / borrow — only when short interest is ≥10% of float AND the latest reading moved ≥20% relative to the prior, or the borrow fee spiked; and only with a stated reason it matters inside the window.

* Positioning reads (prime-brokerage flow, COT) — descriptive context only, never a story of their own: reported only at the stated extremes, rendered as a tone-line clause or one News line at most, never a Heads-up card, never framed as a directional cue.

* Policy / fiscal deadlines — only with a dated deadline inside the window or ≤5 sessions past its edge.

Anything that fails a category gate is not "compressed to one clause" — it is cut, and it belongs in Cut for cause if it was ever a serious candidate.

---

## D. HARD EXCLUSIONS — never include

* Routine analyst reiterations at unchanged PT.
* Articles recapping the prior close or summarizing yesterday's move.
* "Stock X could do Y" speculation / target-price think-pieces.
* Any event already in the scheduled-events table (no double-counting).
* Posts from famous figures (Musk, etc.) that don't change a forecast or a flow — genuinely market-moving posts and rumors are captured by the headlines gatherer, not excluded here.
* Routine plumbing: bill and short-coupon auctions, non-voting Fed speakers, scheduled 10b5-1 insider sales, RSU vests, passive 13G re-filings, shelf filings with no takedown, dividend declarations that merely confirm the existing rate.
* Re-reporting an announcement whose effective date is outside the window, or re-reporting on a later day an effective-date event already covered on its effective day.
* Anything included only to look thorough. Thoroughness lives in the gather; the page is ruthless.

---

## E. HOW TO WEIGH A HEADLINE (v2 guide — applies A–D, never relaxes them)

Run the questions in this order and stop at the first "no":

1. **What is the event?** Name the actor, the action, the date/time (ET) and the document or statement it comes from. If you can only describe a price move ("NVDA −4% on AI worries"), you do not have an event yet — search for the trigger. No trigger in Tier 1/2 → it is a "move without identified driver" → Cut for cause. (Exception: a promoted state variable, section B.)
2. **What is the mechanism?** How does this event change cash flows, discount rates, supply/demand of shares, or the probability of a dated outcome? If you cannot state a mechanism in one clause, the item is colour, not a catalyst.
3. **Magnitude** — apply A.1 literally: >1% plausible on the name, or >0.3% on SPY/QQQ. Use the size of past reactions to the same kind of event as the yardstick, not the loudness of the coverage.
4. **Already in the price?** — apply A.2. Test: was the substance public before the last session's close, and did the name already move on it? Yes → cut. A restated fact with a new date attached is still priced in. A scheduled event (earnings, CPI) is never "priced in" as an event — its outcome is unknown; that is exactly what makes it a binary.
5. **Reach** — who is exposed? For a watchlist name not named in the headline, state the exposure channel explicitly (supplier, customer, competitor, index weight, rate sensitivity). "Sector sympathy" without a channel is not reach.
6. **Freshness** — is it still repricing, or does it gate a forward dated event inside the coverage window or hold window? Neither → cut.
7. **Forward consequence** — apply A.5: what would a holder of a 7–30 DTE vertical spread on this name do differently because of it (avoid opening, exit before a date, manage a short leg)? Nothing → cut.
8. **Scheduled or mechanical item?** → also apply the CATEGORY GATES (C) as hard thresholds.
9. **Source** — Tier 3 alone never grounds a page item; re-ground in Tier 1/2 or tag [REPORTED — unconfirmed] and gate harder.

Common traps: (i) treating an old story's new article as fresh; (ii) counting analyst target changes as events (they are opinions unless they carry new information); (iii) letting a dramatic percentage move stand in for a cause; (iv) promoting a single-name item because it is on the watchlist — reach is judged, not assumed; (v) inventing a mechanism to rescue a headline that "feels important".

---

## F. IMPORTANCE GRADE (assigned only to items that cleared A–D)

* **3 — must-watch.** Should change what the reader does inside the coverage window: a top-tier macro print, FOMC decision/minutes, a promoted state-variable extreme, a geopolitical or policy shock that is moving the whole tape, or a watchlist-name binary (earnings, court/agency decision, dated regulatory outcome) dated inside the coverage window. The toplead's driver is always grade 3.
* **2 — material.** Cleared every test with a clear forward consequence, but one of: single-name/sector reach rather than broad tape; dated inside the hold window but after the coverage window; broad reach but moderate magnitude; a mechanical event (auction, lockup, index flow) big enough to matter on its effective date.
* **1 — context.** Cleared the gate but is borderline on one dimension — unconfirmed (Tier 3 / rumor), small magnitude at the threshold, an ex-div or blackout note, or a story that gates a forward event without being one. Compress to one clause. If it would not survive being compressed to one clause, it did not clear the gate.

Caps are unchanged by grading: Heads-up ≤5, News ≤6, ≤4 page items from plumbing/structure/filings combined, ≤4 chips per calendar cell. Order every section by grade, then by reach.
