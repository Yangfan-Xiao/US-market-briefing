#!/usr/bin/env python3
"""
edgar_filings.py — recent SEC filings for every watchlist stock, from EDGAR's free JSON API.

Replaces the flows gatherer's search-based filings sweep with a deterministic list the gatherers read
from their packs. For each stock in config/watchlist.json (ETFs and indices skipped):
  - resolves the CIK from sec.gov/files/company_tickers.json (override with "cik" in watchlist.json)
  - reads data.sec.gov/submissions/CIK##########.json and keeps filings from the last LOOKBACK
    calendar days of these forms: 8-K / 6-K (with item codes), 4, SC 13D / SC 13G (+ amendments),
    S-3 / S-3ASR / 424B*, 144
  - counts Form 4 filings per issuer (a hint for the insider-cluster gate — the gate still needs
    >= 3 insiders, same direction, within 5 sessions, checked on the filings themselves)

SEC requires a descriptive User-Agent with a contact address. Set it in the environment:
  export SEC_UA="us-market-briefing yourname@example.com"
Without SEC_UA the script still tries with a generic agent; if SEC refuses, it writes an empty
result with the error and the flows gatherer falls back to searching.

Writes run/filings.json. Reads run/window.json for the run date.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOKBACK = 4  # calendar days — covers the last 3 sessions across a weekend
UA = os.environ.get("SEC_UA") or "us-market-briefing research script (set SEC_UA with a contact email)"

KEEP_FORMS = ("8-K", "6-K", "4", "SC 13D", "SC 13G", "SCHEDULE 13D", "SCHEDULE 13G", "S-3", "S-3ASR", "144")
# 8-K items worth a look; the rest (e.g. 9.01 exhibits alone, 5.07 routine votes) rarely clear the gate
ITEM_HINTS = {
    "1.01": "material agreement", "1.02": "agreement terminated", "1.03": "bankruptcy",
    "2.01": "acquisition/disposal completed", "2.02": "results of operations", "2.03": "new debt obligation",
    "2.05": "restructuring costs", "2.06": "impairment", "3.01": "listing notice", "3.02": "unregistered equity sale",
    "4.01": "auditor change", "4.02": "non-reliance on financials", "5.01": "change in control",
    "5.02": "officer/director change", "5.03": "charter/bylaw amendment", "5.07": "shareholder vote",
    "7.01": "Reg FD disclosure", "8.01": "other events", "9.01": "exhibits",
}
LOW_SIGNAL_ITEMS = {"5.07", "9.01", "5.03"}


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read()


def form_kept(form):
    f = form.upper()
    return f in KEEP_FORMS or f.rstrip("/A") in KEEP_FORMS or f.startswith("424B") or f.startswith("SC 13") or f.startswith("SCHEDULE 13")


def main():
    with open(os.path.join(ROOT, "config", "watchlist.json"), encoding="utf-8") as f:
        wl = json.load(f)
    wpath = os.path.join(ROOT, "run", "window.json")
    run_day = dt.datetime.now(ET).date()
    if os.path.exists(wpath):
        with open(wpath, encoding="utf-8") as f:
            run_day = dt.date.fromisoformat(json.load(f)["run_start_et"][:10])
    since = run_day - dt.timedelta(days=LOOKBACK)

    out = {"generated_et": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), "since": since.isoformat(),
           "source": "SEC EDGAR submissions API (data.sec.gov) — Tier 1", "by_ticker": {}, "errors": []}
    stocks = [s for s in wl["symbols"] if s["type"] == "stock"]
    try:
        tmap = {v["ticker"].upper(): int(v["cik_str"]) for v in json.loads(get("https://www.sec.gov/files/company_tickers.json")).values()}
    except Exception as e:
        tmap = {}
        out["errors"].append(f"company_tickers.json: {type(e).__name__}: {e}")

    for s in stocks:
        t = s["ticker"]
        cik = s.get("cik") or tmap.get(t)
        if not cik:
            out["errors"].append(f"{t}: no CIK (add \"cik\" to config/watchlist.json)")
            continue
        try:
            d = json.loads(get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"))
        except Exception as e:
            out["errors"].append(f"{t}: {type(e).__name__}: {e}")
            continue
        r = d.get("filings", {}).get("recent", {})
        rows = []
        for i, form in enumerate(r.get("form", [])):
            fdate = r["filingDate"][i]
            if fdate < since.isoformat():
                break  # newest first
            if not form_kept(form):
                continue
            acc = r["accessionNumber"][i]
            items = [x.strip() for x in (r.get("items", [""] * (i + 1))[i] or "").split(",") if x.strip()]
            doc = r.get("primaryDocument", [""] * (i + 1))[i]
            rows.append({"form": form, "filed": fdate, "items": items,
                         "item_hints": [ITEM_HINTS.get(x, x) for x in items if x not in LOW_SIGNAL_ITEMS],
                         "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"})
        form4 = [x for x in rows if x["form"] in ("4", "4/A")]
        other = [x for x in rows if x["form"] not in ("4", "4/A")]
        out["by_ticker"][t] = {"cik": int(cik), "form4_count": len(form4), "filings": other,
                               "form4_latest": form4[:3]}
        time.sleep(0.15)  # SEC fair-access limit is 10 req/s

    with open(os.path.join(ROOT, "run", "filings.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    for t, v in out["by_ticker"].items():
        if v["filings"] or v["form4_count"]:
            forms = ", ".join(f"{x['form']}{'[' + ','.join(x['items']) + ']' if x['items'] else ''} {x['filed'][5:]}" for x in v["filings"])
            print(f"{t:5} Form4×{v['form4_count']}  {forms}")
    if out["errors"]:
        print("Errors:", "; ".join(out["errors"][:6]))
    print(f"-> wrote run/filings.json (since {since})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
