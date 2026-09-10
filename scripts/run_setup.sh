#!/usr/bin/env bash
# run_setup.sh — Phase 0 in one command. Run from anywhere: bash scripts/run_setup.sh [--at YYYY-MM-DDTHH:MM]
# Produces run/window.json, run/market.json, run/events.json, run/pack_*.md, run/summary.md
set -u
cd "$(dirname "$0")/.."
mkdir -p run/gather run/deep_dive
rm -f run/gather/*.md run/deep_dive/*.md run/pack_*.md run/content.json run/artifact.html run/qc_report.md run/render_report.json 2>/dev/null

python3 -c "import jinja2, jsonschema" 2>/dev/null || pip install jinja2 jsonschema --break-system-packages -q

echo "== session window =="
python3 scripts/session_window.py "$@" || { echo "session_window.py FAILED"; exit 1; }
echo; echo "== market data =="
python3 scripts/market_data.py || echo "market_data.py failed — metrics will render as n/a; say so in Assumptions"
echo; echo "== scheduled events (auctions / FOMC / OpEx / ETF ex-div) =="
python3 scripts/scheduled_events.py || echo "scheduled_events.py failed — the macro gatherer must confirm auctions/FOMC/OpEx itself"
echo; echo "== watchlist events =="
python3 scripts/watchlist_events.py || echo "watchlist_events.py failed — earnings/ex-div dates unknown; the macro gatherer must confirm them"
echo; echo "== packs =="
python3 scripts/make_packs.py
echo; echo "Setup complete. Read run/summary.md next."
