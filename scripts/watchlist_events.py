#!/usr/bin/env python3
"""
watchlist_events.py — scheduled corporate events for every watchlist name, from APIs.

For each symbol in config/watchlist.json:
  - next earnings date(s) + is-estimate flag + consensus EPS / revenue   (Yahoo quoteSummary.calendarEvents)
  - next ex-dividend date / pay date                                     (Yahoo quoteSummary.calendarEvents)
  - Nasdaq earnings-calendar cross-check for every trading day in the hold window (report time: BMO/AMC)
  - last price and day change (Yahoo chart meta) — context only

Writes run/events.json with derived lists:
  earnings_in_coverage, earnings_in_hold_window, exdiv_in_hold_window, date_conflicts, unverified.

Reads run/window.json (run session_window.py first).
Consensus basis note: Yahoo consensus is the S&P Global/LSEG "adjusted" (non-GAAP) mean; Nasdaq's
epsForecast is Zacks consensus. The briefing must name the basis when quoting a consensus figure.
"""
import datetime as dt
import http.cookiejar
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url, extra=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(extra or {})
    return opener.open(urllib.request.Request(url, headers=h), timeout=timeout).read()


def yahoo_crumb():
    try:
        get("https://fc.yahoo.com")
    except Exception:
        pass  # 404 is normal; the call only seeds cookies
    return get("https://query2.finance.yahoo.com/v1/test/getcrumb").decode()


def fmt_date(obj):
    if not obj:
        return None
    if isinstance(obj, dict):
        return obj.get("fmt")
    if isinstance(obj, (int, float)):
        return dt.datetime.fromtimestamp(obj, ET).date().isoformat()
    return str(obj)


def yahoo_calendar(sym, crumb):
    u = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(sym)}"
         f"?modules=calendarEvents,price&crumb={urllib.parse.quote(crumb)}")
    d = json.loads(get(u))
    res = d["quoteSummary"]["result"]
    if not res:
        raise RuntimeError("no result")
    r = res[0]
    ce = r.get("calendarEvents") or {}
    e = ce.get("earnings") or {}
    p = r.get("price") or {}
    dates = [fmt_date(x) for x in (e.get("earningsDate") or [])]
    out = {
        "earnings_dates": [x for x in dates if x],
        "earnings_is_estimate": e.get("isEarningsDateEstimate"),
        "earnings_call_date": (fmt_date((e.get("earningsCallDate") or [None])[0]) if e.get("earningsCallDate") else None),
        "eps_consensus": (e.get("earningsAverage") or {}).get("raw"),
        "eps_low": (e.get("earningsLow") or {}).get("raw"),
        "eps_high": (e.get("earningsHigh") or {}).get("raw"),
        "rev_consensus": (e.get("revenueAverage") or {}).get("raw"),
        "ex_dividend_date": fmt_date(ce.get("exDividendDate")),
        "dividend_pay_date": fmt_date(ce.get("dividendDate")),
        "last_price": (p.get("regularMarketPrice") or {}).get("raw"),
        "day_change_pct": (p.get("regularMarketChangePercent") or {}).get("raw"),
        "pre_market_pct": (p.get("preMarketChangePercent") or {}).get("raw"),
        "post_market_pct": (p.get("postMarketChangePercent") or {}).get("raw"),
        "market_state": p.get("marketState"),
        "source": "Yahoo Finance quoteSummary (calendarEvents, price)",
    }
    if out["day_change_pct"] is not None:
        out["day_change_pct"] = round(out["day_change_pct"] * 100, 2)
    for k in ("pre_market_pct", "post_market_pct"):
        if out[k] is not None:
            out[k] = round(out[k] * 100, 2)
    return out


def nasdaq_earnings(date_iso):
    u = f"https://api.nasdaq.com/api/calendar/earnings?date={date_iso}"
    d = json.loads(get(u, {"Accept": "application/json, text/plain, */*", "Origin": "https://www.nasdaq.com",
                          "Referer": "https://www.nasdaq.com/"}))
    rows = ((d.get("data") or {}).get("rows")) or []
    return {r["symbol"]: {"time": r.get("time"), "eps_forecast": r.get("epsForecast"),
                          "fiscal_quarter_ending": r.get("fiscalQuarterEnding"), "no_of_ests": r.get("noOfEsts")}
            for r in rows}


TIME_MAP = {"time-after-hours": "AMC (after close)", "time-pre-market": "BMO (before open)",
            "time-not-supplied": "time not supplied"}


def main():
    with open(os.path.join(ROOT, "config", "watchlist.json"), encoding="utf-8") as f:
        wl = json.load(f)
    wpath = os.path.join(ROOT, "run", "window.json")
    if not os.path.exists(wpath):
        print("run/window.json missing — run scripts/session_window.py first", file=sys.stderr)
        return 1
    with open(wpath, encoding="utf-8") as f:
        w = json.load(f)
    today = dt.datetime.now(ET).date()
    cov_end = dt.date.fromisoformat(w["coverage"]["end_session_date"])
    hold_days = [d["date"] for d in w["hold_window"]["days"] if not d["closed"]]
    hold_last = dt.date.fromisoformat(w["hold_window"]["last"])
    edge_days = [d["date"] for d in w["hold_window"]["edge_days"]]

    crumb = None
    try:
        crumb = yahoo_crumb()
    except Exception as e:
        print("Yahoo crumb failed:", e, file=sys.stderr)

    symbols, errors = {}, []
    for s in wl["symbols"]:
        if s["type"] == "index":
            symbols[s["ticker"]] = {"type": "index", "note": "index — no corporate events"}
            continue
        try:
            symbols[s["ticker"]] = dict(type=s["type"], **yahoo_calendar(s["yahoo"], crumb)) if crumb else {"error": "no crumb"}
        except Exception as e:
            symbols[s["ticker"]] = {"type": s["type"], "error": f"{type(e).__name__}: {e}"}
            errors.append(f"{s['ticker']}: {e}")
        time.sleep(0.4)

    # Nasdaq cross-check for hold window + edge days
    nasdaq, nq_errors = {}, []
    for d in hold_days + edge_days:
        try:
            nasdaq[d] = nasdaq_earnings(d)
        except Exception as e:
            nq_errors.append(f"{d}: {type(e).__name__}: {e}")
        time.sleep(0.3)
    wl_tickers = {s["ticker"] for s in wl["symbols"]}
    nasdaq_hits = {}
    for d, rows in nasdaq.items():
        for t, info in rows.items():
            if t in wl_tickers:
                nasdaq_hits.setdefault(t, []).append(dict(date=d, **info))

    earnings_cov, earnings_hold, earnings_edge, exdiv_hold, exdiv_edge, conflicts, unverified = [], [], [], [], [], [], []
    for t, info in symbols.items():
        if "error" in info or info.get("type") == "index":
            continue
        y_dates = info.get("earnings_dates") or []
        nq = nasdaq_hits.get(t, [])
        nq_dates = [x["date"] for x in nq]
        # a Yahoo date inside the hold window or on the edge
        for d in y_dates:
            dd = dt.date.fromisoformat(d)
            if dd < today:
                continue
            rec = {"ticker": t, "date": d, "yahoo_is_estimate": info.get("earnings_is_estimate"),
                   "eps_consensus_yahoo": info.get("eps_consensus"), "rev_consensus_yahoo": info.get("rev_consensus"),
                   "nasdaq": next((x for x in nq if x["date"] == d), None)}
            if rec["nasdaq"]:
                rec["report_time"] = TIME_MAP.get(rec["nasdaq"]["time"], rec["nasdaq"]["time"])
                rec["confirmation"] = "Yahoo + Nasdaq agree on the date"
            elif nq_dates:
                rec["confirmation"] = f"DATE CONFLICT: Yahoo {d} vs Nasdaq {nq_dates}"
                conflicts.append(rec)
            elif info.get("earnings_is_estimate") is False:
                rec["confirmation"] = "Yahoo says confirmed; not on Nasdaq calendar for that day — verify with company IR"
                unverified.append(rec)
            else:
                rec["confirmation"] = "ESTIMATE only (Yahoo) — do not treat as scheduled until confirmed by company IR"
                unverified.append(rec)
            if dd <= cov_end:
                earnings_cov.append(rec)
            if dd <= hold_last:
                earnings_hold.append(rec)
            elif d in edge_days:
                earnings_edge.append(rec)
        # Nasdaq-only hits (Yahoo missing the date)
        for x in nq:
            if x["date"] not in y_dates:
                rec = {"ticker": t, "date": x["date"], "report_time": TIME_MAP.get(x["time"], x["time"]),
                       "eps_forecast_nasdaq": x["eps_forecast"], "confirmation": "Nasdaq calendar only — Yahoo has a different/no date; verify"}
                (earnings_hold if x["date"] <= hold_last.isoformat() else earnings_edge).append(rec)
                if x["date"] <= cov_end.isoformat():
                    earnings_cov.append(rec)
                conflicts.append(rec)
        xd = info.get("ex_dividend_date")
        if xd:
            xdd = dt.date.fromisoformat(xd)
            rec = {"ticker": t, "ex_date": xd, "pay_date": info.get("dividend_pay_date"),
                   "note": "amount not provided by API — verify amount if inside window"}
            if today <= xdd <= hold_last:
                exdiv_hold.append(rec)
            elif xd in edge_days:
                exdiv_edge.append(rec)

    out = {
        "generated_et": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
        "coverage_end_date": cov_end.isoformat(), "hold_window_last": hold_last.isoformat(),
        "consensus_basis": "Yahoo = S&P Global/LSEG adjusted (non-GAAP) mean; Nasdaq epsForecast = Zacks consensus. Name the basis when quoting.",
        "earnings_in_coverage": sorted(earnings_cov, key=lambda r: r["date"]),
        "earnings_in_hold_window": sorted(earnings_hold, key=lambda r: r["date"]),
        "earnings_just_past_edge": sorted(earnings_edge, key=lambda r: r["date"]),
        "exdiv_in_hold_window": sorted(exdiv_hold, key=lambda r: r["ex_date"]),
        "exdiv_just_past_edge": sorted(exdiv_edge, key=lambda r: r["ex_date"]),
        "date_conflicts": conflicts, "unverified": unverified,
        "symbols": symbols,
        "nasdaq_calendar_days_checked": sorted(nasdaq.keys()),
        "errors": errors + nq_errors,
    }
    op = os.path.join(ROOT, "run", "events.json")
    with open(op, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Earnings in coverage (≤ {cov_end}): " + (", ".join(f"{r['ticker']} {r['date']} {r.get('report_time','')} [{r['confirmation'][:40]}]" for r in out['earnings_in_coverage']) or "none"))
    print(f"Earnings in hold window (≤ {hold_last}): " + (", ".join(f"{r['ticker']} {r['date']}" for r in out['earnings_in_hold_window']) or "none"))
    print("Earnings just past edge: " + (", ".join(f"{r['ticker']} {r['date']}" for r in out['earnings_just_past_edge']) or "none"))
    print("Ex-div in hold window: " + (", ".join(f"{r['ticker']} {r['ex_date']}" for r in out['exdiv_in_hold_window']) or "none"))
    if conflicts:
        print("DATE CONFLICTS: " + "; ".join(f"{r['ticker']} {r['date']}" for r in conflicts))
    if errors or nq_errors:
        print("Errors:", "; ".join(errors + nq_errors))
    print(f"-> wrote {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
