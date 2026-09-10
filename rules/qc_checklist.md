# QC CHECKLIST — accuracy verification before the page is rendered

Two layers. Layer 1 is mechanical (script). Layer 2 is a verification subagent that re-checks
every figure and fact in the draft against sources. The orchestrator applies the corrections,
re-runs Layer 1, and only then renders.

## Layer 1 — `python3 scripts/render_briefing.py --check-only`

Rejects (exit 1, nothing rendered):
* content.json that violates `schema/content.schema.json` (unknown fields, caps, enums, grades outside 1–3)
* any timeline row dated outside the coverage window; an open/close row on a non-session day
* a watchlist earnings date (timeline, heads-up, symbol card, calendar chip) that contradicts `run/events.json`
* calendar chips on a closed day or outside the hold window
* banned constructions ("whether", "watch if", "eyes on", "remains to be seen") in the toplead, bottom line, heads-up, news, symbol lines, timeline "why"
* continuity tokens ("UPDATE — day N", "day 3 ·", "NEW.", "RESOLVED", "carry-over", "previous briefing")
* a symbol card for a name not on the watchlist; duplicate cards

Warns (renders, but the orchestrator must read the warnings): an API-confirmed earnings without a calendar chip; unusual time labels.

## Layer 2 — verification subagent (`briefs/qc_verify.md`)

Scope: every proper noun, number, date, time and consensus figure in `toplead`, `heads_up`, `timeline`, `news`, `symbols`, `calendar`, `edge`, `bottom_line`. Not in scope: Market-conditions numbers (API), prose style.

For each checkable claim the verifier must:
1. Locate the claim's grounding — first in `run/gather/*.md` and `run/deep_dive/*.md` (the evidence trail), then by a fresh fetch of the primary or Tier-2 source when the evidence trail does not contain the exact figure.
2. Return one of: **CONFIRMED** (source + date) · **CORRECTED** (old → new, source) · **UNVERIFIABLE** (what was searched) · **STALE** (true earlier, superseded — with the newer fact).
3. Pay special attention to the recurring error classes:
   * consensus figures without a stated basis (GAAP vs adjusted; Yahoo/S&P Global vs Zacks vs FactSet) → require the basis to be named
   * report timing (BMO vs AMC) and dates that shifted (holiday delays: EIA, BLS)
   * "first time since …" / "highest since …" claims → require the comparison date to be sourced
   * dollar sizes of auctions, offerings, lockup tranches, buyback authorisations
   * times in ET: DST offset, 08:15 ECB vs 08:45 presser, 13:00 auction results vs 13:01 wire
   * names/roles (voting status of Fed speakers; CEO/CFO names)
   * which day of the week a date falls on

Orchestrator handling of the verifier's return:
* CORRECTED → apply the correction to content.json verbatim; if the correction changes the item's grade or whether it clears the filter, re-decide and note it in `assumptions`.
* UNVERIFIABLE → either delete the number (keep the claim qualitative and mark it "unverified") or move the item to Cut for cause; never leave an unverifiable figure on the page.
* STALE → replace with the newer fact or cut.
* Log a one-line QC summary in `assumptions`: "QC: N claims checked, N corrected, N removed as unverifiable."

Budget: the verifier gets at most ~40 claims; if the draft has more, the orchestrator prioritises grade-3 and grade-2 items and the toplead/bottom line, and notes the unchecked remainder in `assumptions`.
