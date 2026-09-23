# us-market-briefing (v2, cloud)

Scheduled, unattended US market briefing for a 23-name options watchlist. Rebuilt from the v1
single-prompt desktop task so it runs in Claude's cloud with the PC off, in roughly a third of the
tokens, with a fixed page format and a QC pass.

```
SKILL.md                 orchestrator runbook (what the scheduled session follows)
TASK_PROMPT.md           the short prompt to paste into the scheduled task + cron + model notes
config/watchlist.json    the 23 names, search aliases, gatherer groups  ← edit to change coverage
config/exposure_map.json read-through companies (supplier/customer/peer → watchlist name + channel) + theme clusters
config/nyse_calendar.json  holidays / early closes 2026–2028 (from nyse.com)
rules/impact_filter.md   the gate (v1 rubric, category gates, exclusions VERBATIM) + weighing guide + grade 1–3
rules/gatherer_filter.md the condensed gate card gatherers read instead of impact_filter + writing_rules
rules/writing_rules.md   who reads it, data rules, stateless rule, writing rules, tag taxonomy, sources, caps
rules/qc_checklist.md    the two-layer QC step
briefs/                  one brief per subagent role (common, macro, flows, symbols, headlines, crossimpact, deep_dive, qc_verify)
schema/content.schema.json  the strict shape of what the writer produces; content.skeleton.json = shape only
scripts/session_window.py   coverage window / focus axis / hold window (deterministic, self-tested)
scripts/market_data.py      SPY QQQ VIX 2Y 10Y 30Y WTI SOX BTC F&G from APIs + promotion check (6-mo extremes, 2σ)
scripts/watchlist_events.py earnings dates (+ is-estimate, consensus) and ex-div dates for all names + read-through earnings
scripts/edgar_filings.py    recent 8-K/6-K items, 13D/G, S-3/424B, 144 and Form 4 counts per stock (SEC EDGAR API; needs SEC_UA)
scripts/make_packs.py       per-gatherer pack files + run/summary.md
scripts/run_setup.sh        Phase 0 in one command
scripts/render_briefing.py  validates run/content.json (schema, dates, earnings guard, banned phrasing) and renders
template/briefing_template.html  the page — CSS/DOM/JS of the original reference; Jinja placeholders; NO prose
tests/                      fixture + smoke test (do not let the orchestrator read tests/)
run/                        per-run working files (git-ignored)
```

## How a run works

```
Phase 0  bash scripts/run_setup.sh         → run/window.json, market.json, events.json, filings.json, pack_*.md, summary.md   (0 tokens)
Phase 1  8 Sonnet gatherers in parallel    macro · flows · headlines · crossimpact · 4 symbol groups   (compact returns, ≤800 words each)
Phase 2  orchestrator triage               re-apply the filter, grade 1–3, choose ≤4 deep-dives
Phase 3  ≤4 Sonnet deep-dives              verify single-source / conflicting / promoted-extreme items; cross-impact
Phase 4  orchestrator writes run/content.json  → python3 scripts/render_briefing.py --check-only (loop until clean)
Phase 5  Sonnet QC verifier                every figure/date/name re-checked; corrections applied; re-validated
Phase 6  python3 scripts/render_briefing.py → standalone HTML (chat file) + artifact fragment (published, stable URL)
Phase 7  2–3-line chat message
```

Why it is cheaper and steadier than v1:
* Market conditions, earnings/ex-div dates, the promotion check, the calendar scaffold and every
  ET↔GMT+8 conversion are computed, not searched or typed.
* 7 gatherers instead of 13, each with a search budget and a hard return format (≤8 keeps); the
  orchestrator never sees the raw articles, only the candidate lines.
* Depth goes where it is needed: the deep-dive stage spends searches only on shortlisted items.
* The template never enters the model's context (the renderer fills it), so ~15K tokens/run vanish
  and prose cloning is impossible. Format is byte-stable day to day.
* Structural guards: an event can only sit on the day it is dated; a watchlist earnings date must
  match the API; banned constructions and continuity tokens are rejected before rendering.

## v2.1 (after the first real run, 2026-09-10)
The first run under-gathered: it missed the Sep 10 30-yr auction, UMich prelim (Sep 11) and the ETF
ex-divs, and returned 1 news line / 2 symbol cards. Fixes: `scripts/scheduled_events.py` now pulls
Treasury coupon auctions (TreasuryDirect API), FOMC dates/blackout (config/fomc.json), OpEx / quad
witching / VIX settlement / quarter-end (rules) and projected ETF ex-divs (Yahoo dividend history),
and the validator rejects a page that omits a gated 10y/30y auction or FOMC decision. Gatherers now
return a BORDERLINE list and a CONSIDERED audit trail (one line per name/area), the symbol brief
captures dated forward events, the macro brief carries a release checklist, and the triage rules
say explicitly that same-day items are never "priced in" and that a dated in-window pivot keeps an
older story alive. Expect a normal day to yield 3–5 heads-up, 2–6 news lines and 3–8 symbol cards —
thinner than v1 (which re-listed carry-over stories for weeks), but not 1 and 2.

## v2.2 (review of the 2026-09-22 run)
* **Out-of-watchlist reach.** `config/exposure_map.json` maps ~40 non-watchlist companies to the watchlist
  names they move (MU → NVDA/AMD HBM, COST → WMT, CRWV → NBIS/ORCL, …) plus theme clusters (export
  controls, BTC-ETF flows, FAA, …). `watchlist_events.py` pulls their earnings from the Nasdaq calendar rows
  it already fetches (no extra calls), plus any ≥$200B company. A new `crossimpact` gatherer researches them
  and the clusters. The Sep 22 page missed Micron (Sep 30), Costco (Sep 24), Accenture and Nike (Oct 1).
* **Cluster drivers.** SOX and BTC are metric cards with the promotion check (semis ×6, crypto ×3 names).
* **Depth for fewer tokens.** Symbol gatherers run two targeted queries per name (Tier-2-domain recency +
  a forward-dated event query), triage from snippets and fetch ≤6 pages per group. Filings come from EDGAR
  by script. Gatherers read a ~900-word filter card (`rules/gatherer_filter.md`) instead of ~3.4K words of rules.
* **Readability.** Heads-up cards and News lines carry `exposed` ticker chips and a `resolves` line. A
  watchlist exposure strip under Conditions tints each name by the highest grade touching it. The timeline
  axis hides when it has only open/close. There are word budgets for the toplead (45) and cards (55).
* **Consistency guards.** 2/3/5/7-yr auction chips are rejected. The validator warns on a chip that repeats a
  Cut-for-cause item and on a News line more than 3 sessions old without a forward pivot. The Tier-2 list is closed.

## Migration to Claude web (cloud)

1. **Repo.** Create a GitHub repo and push this folder. Auth caveat: a cloud session can clone a
   *public* repo with no setup. For a *private* repo, either (a) run the task in a Claude web
   environment that has your GitHub connected (test with the prompt below), or (b) use a fine-grained
   personal access token limited to Contents: read on this one repo and put it in the clone URL
   (`https://<TOKEN>@github.com/<you>/us-market-briefing.git`) — revocable, but visible to anyone who
   can see the task prompt. Nothing in this repo is sensitive, so public is a reasonable choice.
2. **Test the plumbing first** (a manual, non-scheduled cloud session):
   > Clone `<REPO_URL>`, run `bash scripts/run_setup.sh`, then `bash tests/smoke.sh`, and paste the
   > last 30 lines of output. Do not run the briefing.
   You want: the 7 self-tests OK, all 10 metrics fetched, filings.json populated, ORCL-style earnings guard firing, a rendered
   fixture. If `market_data.py` reports a host as unavailable, that host is blocked by the cloud
   egress policy — tell me which and I'll swap the source.
3. **First real run** manually (same prompt as the scheduled task, from `TASK_PROMPT.md`). Check the
   page, then copy the artifact URL into the task prompt as `LATEST_ARTIFACT_URL` so later runs
   republish to the same link.
4. **Schedule it**: create the scheduled task in Claude web with the prompt from `TASK_PROMPT.md`,
   cron `30 11 * * 1-5` (19:30 GMT+8, DST-proof), model Opus.
5. **Retire the desktop task** once two cloud runs look right.

## Editing behaviour later
* Add/remove a name or regroup gatherers: `config/watchlist.json` only.
* Add a read-through company or theme: `config/exposure_map.json` (key = the US ticker on the Nasdaq calendar).
* Change the filter: `rules/impact_filter.md` (sections A–D are the binding criteria) — and mirror any
  threshold change in `rules/gatherer_filter.md`, the card the gatherers actually read.
* Change phrasing rules or caps: `rules/writing_rules.md` (caps that the renderer enforces live in
  `schema/content.schema.json` — `maxItems`).
* Change the look: `template/briefing_template.html` (Jinja2). Run `bash tests/smoke.sh` after.
* New holidays: `config/nyse_calendar.json`.

## Local dry run (any machine with Python 3.11+, `pip install jinja2 jsonschema`)
```
bash scripts/run_setup.sh --at 2026-09-10T08:45     # simulate a run start (ET)
bash tests/smoke.sh                                  # self-tests + fixture render → run/briefing-*.html
python3 scripts/session_window.py --selftest         # the seven coverage-window cases
```
