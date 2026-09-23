# Scheduled-task prompt for Claude (web / cloud)

Paste the block below as the prompt of the scheduled task. Replace `<REPO_URL>`. The artifact URL is
already filled in: it is the format-test page published on 2026-09-10 from the migration session, owned
by you, so every run republishes to that same link. Keep the prompt short — the runbook lives in the repo.

---

Run the US market daily briefing.

1. Set up the workspace:
   ```
   git clone --depth 1 https://github.com/Yangfan-Xiao/US-market-briefing.git us-market-briefing && cd us-market-briefing
   export SEC_UA="us-market-briefing <your-contact-email>"
   ```
   If the clone fails, stop and report the exact git error in one line — do not attempt a briefing
   without the repo.
2. Open `SKILL.md` in the repo and follow it phase by phase. It is the complete runbook: scripts for
   dates and market data, eight parallel Sonnet gatherers, deep-dives, a QC pass, script rendering,
   and delivery. Do not improvise a different workflow and do not reproduce or read any HTML template.
3. Delivery settings for this task:
   * Latest-briefing artifact URL: `https://claude.ai/code/artifact/4a9b0e0c-e4c9-458b-b9e7-5443a95b77da`
     (read it with the Artifact tool first, then publish run/artifact.html to that url so the link stays
     stable; if the update is refused, publish a new artifact and print its URL).
   * Also send the standalone HTML file into this chat.
4. Final message: 2–3 lines only (coverage window · the toplead sentence · counts · artifact link).

This is unattended: never ask a question; make the most reasonable default and log it in the
briefing's Assumptions footer.

---

## Schedule (cron is UTC)

Recommended: `30 11 * * 1-5` → 19:30 GMT+8 on weekdays = 07:30 ET (EDT) / 06:30 ET (EST).
Because the coverage rule is relative to the run start ("→ the first open ≥24h ahead"), this fixed
UTC time needs **no DST edits**: in both seasons the run covers today's session → tomorrow's open,
and Friday's run covers Friday → Monday's open.

If you prefer a run closer to the open (e.g. 08:30 ET), use `30 12 * * 1-5` in summer and
`30 13 * * 1-5` in winter — and remember a run that slips past 09:30 ET rolls the coverage window
to the day after tomorrow's open (by design).

## Model
Set the task's model to Opus (orchestrator quality decides the briefing). Gatherers, deep-dives and
QC are pinned to Sonnet inside the runbook. Approximate cost per run: one Opus context of ~40–60K
tokens plus 8–13 Sonnet subagent runs of ~25–50K each (gatherers read a short filter card and fetch
fewer full pages than before, so the eighth gatherer roughly pays for itself).

## SEC_UA
EDGAR (the filings sweep) refuses requests whose User-Agent has no contact address. Put any address you
are happy for SEC to see in the `export SEC_UA=...` line above. It stays in the task prompt, not the
public repo. Without it the filings step logs an error and the flows gatherer falls back to search.
