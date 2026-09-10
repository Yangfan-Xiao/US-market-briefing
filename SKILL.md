---
name: us-market-briefing
description: Scheduled, unattended US market briefing for an options trader's 23-name watchlist — API data + 7 parallel gatherers + deep-dives + QC, rendered by script into a fixed HTML template and published as an artifact.
---

# US MARKET BRIEFING — orchestrator runbook (v2, cloud)

You are the orchestrator of a scheduled, unattended run. You own judgement (the filter gate, grading,
deep-dive selection, writing, QC handling). Scripts own facts that can be computed (dates, market
data, earnings/ex-div dates, rendering, validation). Sonnet subagents own searching. You never
hand-write HTML and you never type a market-data number.

Reader context: `rules/writing_rules.md` §"Who reads this". Report context and catalysts only — never
trade ideas. Every item on the page is grounded in a retrieved source and re-verified by QC.

## Non-negotiables
* No questions, no pauses: this is unattended. Decide, act, log the assumption in `assumptions`.
* Stateless: never read previous briefings or any state file. No continuity language.
* One pass, one deliverable. Finish even if a gatherer fails — log it.
* Coverage window = run start → the first regular-session open ≥ 24h ahead (computed by script).
  The timeline axis = the focus session; everything inside the window is listed with its date.
* Repo root is the working directory for every command below (`cd` into it first).

## Phase 0 — Setup (script, ~1 min)
```
bash scripts/run_setup.sh
```
Then read `run/summary.md` (only that — do not open the JSON files unless a script failed).
It gives: run start in ET/GMT+8, coverage end, sessions in window, focus axis day, hold-window days,
the API market snapshot with PROMOTION CANDIDATES, and API-confirmed earnings / ex-div dates.
If a script failed, note it for `assumptions` and continue (the gatherers can cover the gap).

## Phase 1 — Gather (7 Sonnet subagents in ONE parallel batch, ~6–8 min)
Launch all seven with the Agent tool, `model: sonnet`, in a single message. Each prompt is short —
the subagent reads its files itself. Use this prompt, substituting NAME / BRIEF / PACK:

> You are gatherer NAME for a scheduled market briefing. Working directory: <repo path>. Read, in
> order: briefs/_common.md, rules/impact_filter.md, rules/writing_rules.md, briefs/BRIEF, run/PACK.
> Then do the job the brief describes, within its search budget, and return EXACTLY the format in
> briefs/_common.md (also write it to run/gather/NAME.md). No prose outside that format.

| NAME | BRIEF | PACK |
|---|---|---|
| macro | gather_macro.md | pack_macro.md |
| flows | gather_flows.md | pack_flows.md |
| headlines | gather_headlines.md | pack_headlines.md |
| G-A_index_macro_names | gather_symbols.md | pack_G-A_index_macro_names.md |
| G-B_megacap | gather_symbols.md | pack_G-B_megacap.md |
| G-C_semis_ai | gather_symbols.md | pack_G-C_semis_ai.md |
| G-D_highbeta | gather_symbols.md | pack_G-D_highbeta.md |

(Group names come from `config/watchlist.json` → `gather_groups`; if the user edits groups, the packs
and this table follow automatically — use whatever `run/pack_G-*.md` files exist.)

A gatherer that errors or returns nothing gets ONE retry; then log "gatherer X failed" in `assumptions`.

## Phase 2 — Triage (you; no tools except reading the returns)
Pool every KEEP line. Re-apply `rules/impact_filter.md` §A–D yourself — a gatherer's "keep" is a
nomination, not a decision. Then:
1. Merge duplicates across gatherers (the same event reported by two gatherers is one item; keep the
   best-sourced line).
2. Assign the grade per §F. Order by grade, then reach.
3. Decide the page: ≤5 Heads-up (grade 3 first; at most ONE promoted state variable), ≤6 News,
   symbol cards only for names with a cleared catalyst, timeline rows for every dated item inside the
   coverage window, calendar chips for every dated item in the hold window (≤4 per day), Cut for cause
   for serious candidates that failed (with the reason).
4. **Deep-dive shortlist (≤4):** any grade-3 or grade-2 item that is single-source, Tier-3 only,
   flagged `conflicting-figures` or `needs-deep-dive`, a promoted state variable whose cause is
   contested/unidentified, or a cross-impact question raised by the headlines gatherer ("which
   watchlist names are exposed to X?"). Grade-1 items are never deep-dived — compress or cut.

## Phase 3 — Deep-dive (≤4 Sonnet subagents, parallel, ~3 min)
Prompt per item:
> Deep-dive for a scheduled market briefing. Working directory: <repo path>. Read briefs/deep_dive.md,
> then rules/impact_filter.md §E. ITEM: <the KEEP line verbatim>. CONTEXT: <one line on why it was
> shortlisted; related lines from other gatherers if any>. Return exactly the format in
> briefs/deep_dive.md and write it to run/deep_dive/<slug>.md.

Apply verdicts: CORRECTED → use the corrected facts; UNCONFIRMED → grade 1 with `[REPORTED — unconfirmed]`
or cut; CUT → Cut for cause.

## Phase 4 — Write `run/content.json` (you)
Copy the shape from `schema/content.skeleton.json`; the binding rules are in
`schema/content.schema.json` and `rules/writing_rules.md`. Writing checklist:
* `toplead`: one declarative sentence — driver (grade 3) + mechanism + resolution/invalidator.
* `heads_up`: ≤5; `kind`/`badge_class` per the taxonomy; `when` in ET and GMT+8 (ET +12h EDT / +13h EST —
  `run/summary.md` says which); set `date`, `ticker`, `event_type` on dated items so the validator can check them.
* `conditions_tone`: read the API snapshot in `run/summary.md`; do not restate every number.
* `timeline`: only dated items inside the coverage window (the validator rejects others); `time_et`
  24h ET or null with a label (`Pre-open`, `All session`, `AMC`); the renderer adds open/close rows.
  An after-close event on day D is dated D with label `AMC` — never placed on another day.
* `news`: ≤6, cause-first; `direction` off/pos/neutral; `tag` names scope, tier+outlet, date.
* `symbols`: only names with cleared catalysts; pills from the taxonomy; `source` names the highest
  tier used; add `events` for earnings/ex-div so dates are validated. Ex-div items for several names
  may share one card with ticker `EX-DIV`.
* `calendar`: keys are hold-window trading days from `run/summary.md`; ≤4 chips; closed days get no key.
* `edge`: dated items just past the window edge. `bottom_line`: per the writing rules.
* `cut_for_cause`: 8–20 lines. `assumptions`: every default, conflict, gap, failed gatherer.
Then run `python3 scripts/render_briefing.py --check-only` and fix every error it reports (re-run
until clean). Warnings: act on them or explain in `assumptions`.

## Phase 5 — QC (one Sonnet subagent, ~4 min; Opus if the task's model budget allows)
> QC verifier for a scheduled market briefing. Working directory: <repo path>. Read briefs/qc_verify.md
> and rules/qc_checklist.md, then verify run/content.json as instructed. Return exactly the format in
> briefs/qc_verify.md and write it to run/qc_report.md.

Apply every CORRECTION verbatim; remove UNVERIFIABLE figures (or the item); replace STALE facts; fix
CONSISTENCY discrepancies; add the QC summary line to `assumptions`. Re-run `--check-only` until clean.

## Phase 6 — Render and deliver (script + tools, ~1 min)
```
python3 scripts/render_briefing.py
```
It writes `run/briefing-<date>-<HHMM>.html` (standalone) and `run/artifact.html` (fragment).
1. `cp run/briefing-*.html /mnt/user-data/outputs/` and `SendUserFile` that file (status: proactive).
2. Publish the artifact: if the task prompt gives a LATEST_ARTIFACT_URL, first `Artifact action:read`
   with that url, then `Artifact` with `file_path: run/artifact.html`, `url: <that url>`. Otherwise
   publish new with `favicon: "📈"`, `description: "US market briefing — <coverage window>"`, and put the
   returned URL in your final message so the user can pin it in the task prompt.
   If the Artifact tool is unavailable, skip — the file delivery stands.
3. If the `mcp__remote-devices__*` tools are present AND a call succeeds (the user's PC is on), also
   `device_commit_files` the HTML into `D:\Files\文档\Investment\Briefings\Output\`. If not, skip silently.

## Phase 7 — Final message (2–3 lines)
Coverage window · the toplead sentence · counts (heads-up / news / symbol cards / QC corrections) ·
artifact link. Nothing else.

## Budget guardrails
Orchestrator context stays small: read `run/summary.md`, the seven returns, ≤4 deep-dives, one QC
report, and the validator output. Do not open pack files, gather JSON, the template, or past outputs.
Target wall-clock ≈ 15 min; if Phase 1 exceeds 12 min, proceed with whatever has returned and log it.
