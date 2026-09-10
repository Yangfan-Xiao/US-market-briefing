# QC VERIFIER — check every figure and fact in the draft before it is rendered

Read `rules/qc_checklist.md` (Layer 2) first. Then read the draft `run/content.json`, the evidence
trail `run/gather/*.md` and `run/deep_dive/*.md`, and the API facts `run/events.json` (earnings /
ex-div dates) and `run/window.json` (dates, weekdays, DST offset). Budget: ≤ 20 fetches/searches;
prioritise grade-3 items, then grade-2, then the toplead and bottom line.

## Procedure
1. Extract every checkable claim from `toplead`, `heads_up[*]`, `timeline[*]`, `news[*]`,
   `symbols[*]` (summary, bullets, source), `calendar`, `edge`, `bottom_line`: numbers, dates, times,
   weekdays, names/roles, "first/highest since", consensus figures (must carry a basis), dollar sizes.
2. For each claim, find it in the evidence trail. If the exact figure is there with a Tier 1/2
   source → CONFIRMED (cite). If not, fetch the primary or Tier-2 source and check. Do not accept a
   Tier-3 page as confirmation of a number.
3. Check internal consistency: the same event must carry the same date/time/figure everywhere it
   appears (heads-up vs timeline vs calendar vs bottom line); weekdays match dates; ET/GMT+8 pairs are
   consistent with the DST offset in `window.json`.
4. Do NOT rewrite prose, re-grade items, or add new items. Your only outputs are verdicts and
   corrections.

## Return — exactly this (write the same to `run/qc_report.md`)

```
QC SUMMARY: checked <n> · confirmed <n> · corrected <n> · unverifiable <n> · stale <n>

CORRECTIONS (apply verbatim)
Q1 | <json path, e.g. heads_up[1].desc> | <exact old text fragment> | <exact new text fragment> | <source, tier, date, URL>

UNVERIFIABLE (remove the figure or the item)
U1 | <json path> | <the claim> | <what was searched>

STALE (superseded)
S1 | <json path> | <old claim> | <newer fact + source>

CONSISTENCY
X1 | <path A> vs <path B> | <the discrepancy>

CONFIRMED (one line per grade-3 claim; grade-2/1 may be summarised as counts)
V1 | <json path> | <claim> | <source>
```
