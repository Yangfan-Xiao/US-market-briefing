#!/usr/bin/env python3
"""
scheduled_events.py — mechanical, known-in-advance events for the hold window, from APIs and rules.

  - Treasury coupon auctions (TreasuryDirect API: upcoming + announced) with the category-gate flag
    (10y / 20y / 30y / TIPS = gated → calendar chip required; 2s/3s/5s/7s and bills = listed only)
  - FOMC: meetings, decision/SEP time, minutes release (end + 21 days, 14:00 ET), blackout dates
    (config/fomc.json — from federalreserve.gov)
  - Options structure: monthly OpEx (3rd Friday), quad witching (Mar/Jun/Sep/Dec), VIX monthly
    settlement (the Wednesday 30 days before the following month's 3rd Friday), month/quarter end
  - ETF ex-dividend projections for SPY / QQQ / IWM from Yahoo dividend history (last year's
    same-quarter ex-date + 52 weeks, nudged to a trading day) — PROJECTED, to be confirmed on the
    issuer page by the flows gatherer

Writes run/scheduled.json. Reads run/window.json.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "run")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36", "Accept": "application/json"}


def get(u, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout).read()


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def third_friday(y, m):
    d = dt.date(y, m, 15)
    while d.weekday() != 4:
        d += dt.timedelta(days=1)
    return d


def prev_trading_day(d, hol):
    while d.weekday() >= 5 or d in hol:
        d -= dt.timedelta(days=1)
    return d


def next_trading_day(d, hol):
    while d.weekday() >= 5 or d in hol:
        d += dt.timedelta(days=1)
    return d


def main():
    w = load_json(os.path.join(RUN, "window.json"))
    cal = load_json(os.path.join(ROOT, "config", "nyse_calendar.json"))
    hol = {dt.date.fromisoformat(k) for k in cal["holidays"]}
    fomc = load_json(os.path.join(ROOT, "config", "fomc.json"))
    today = dt.datetime.now(ET).date()
    first = dt.date.fromisoformat(w["hold_window"]["first"])
    last = dt.date.fromisoformat(w["hold_window"]["last"])
    edge_last = dt.date.fromisoformat(w["hold_window"]["edge_days"][-1]["date"])
    cov_end = dt.date.fromisoformat(w["coverage"]["end_session_date"])

    def in_hold(d):
        return first <= d <= last

    def in_edge(d):
        return last < d <= edge_last

    errors = []

    # ---- Treasury auctions ----
    auctions = []
    try:
        rows = json.loads(get("https://www.treasurydirect.gov/TA_WS/securities/upcoming?format=json"))
        for t in ("Note", "Bond", "TIPS", "FRN"):
            try:
                rows += json.loads(get(f"https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=45&type={t}"))
            except Exception:
                pass
        seen = set()
        for s in rows:
            ad = (s.get("auctionDate") or "")[:10]
            if not ad:
                continue
            d = dt.date.fromisoformat(ad)
            key = (ad, s.get("securityType"), s.get("securityTerm"))
            if key in seen or d < today or not (in_hold(d) or in_edge(d)):
                continue
            seen.add(key)
            term = s.get("securityTerm") or ""
            stype = s.get("securityType") or ""
            if (s.get("tips") or "").lower() == "yes":
                stype = "TIPS"
            if (s.get("frnIndexDeterminationDate") or "") and stype == "Note":
                stype = "FRN"
            years = 0
            try:
                years = int(term.split("-")[0])
            except Exception:
                pass
            gated = stype == "Bond" or stype == "TIPS" or (stype == "Note" and years >= 9)
            label = {"Bond": "30-yr" if years >= 25 else "20-yr", "Note": f"{years + (1 if 'Month' in term else 0)}-yr",
                     "TIPS": f"{years + (1 if 'Month' in term else 0)}-yr TIPS", "Bill": f"{term} bill", "FRN": "2-yr FRN"}.get(stype, term)
            amt = s.get("offeringAmount")
            auctions.append({
                "date": ad, "weekday": d.strftime("%a"), "type": stype, "term": term, "label": label,
                "size_bn": round(float(amt) / 1e9, 1) if amt else None,
                "reopening": s.get("reopening") == "Yes",
                "time_et": "13:00" if stype != "Bill" else "11:30",
                "results_et": "13:02" if stype != "Bill" else "11:32",
                "gated": gated, "in_hold_window": in_hold(d), "in_coverage": d <= cov_end,
                "source": "TreasuryDirect TA_WS API",
            })
        auctions.sort(key=lambda x: (x["date"], x["type"]))
    except Exception as e:
        errors.append(f"treasury auctions: {type(e).__name__}: {e}")

    # ---- FOMC ----
    fomc_out = []
    for m in fomc["meetings"]:
        s, e = dt.date.fromisoformat(m["start"]), dt.date.fromisoformat(m["end"])
        minutes = e + dt.timedelta(days=21)
        # blackout: second Saturday before the meeting start → Thursday after the meeting
        sat = s - dt.timedelta(days=(s.weekday() - 5) % 7)      # Saturday on/before start
        blackout_start = sat - dt.timedelta(days=7)
        blackout_end = e + dt.timedelta(days=(3 - e.weekday()) % 7)  # Thursday after
        items = []
        if in_hold(s) or in_edge(s):
            items.append({"date": s.isoformat(), "what": "FOMC meeting begins (day 1)", "time_et": None, "gated": False})
        if in_hold(e) or in_edge(e):
            items.append({"date": e.isoformat(), "what": f"FOMC decision + statement{' + SEP/dot plot' if m['sep'] else ''} 14:00 · presser 14:30", "time_et": "14:00", "gated": True})
        if in_hold(minutes) or in_edge(minutes):
            items.append({"date": minutes.isoformat(), "what": f"FOMC minutes ({s.strftime('%b %d')} meeting) 14:00", "time_et": "14:00", "gated": True})
        if in_hold(blackout_start):
            items.append({"date": blackout_start.isoformat(), "what": "Fed communications blackout begins", "time_et": None, "gated": False})
        if in_hold(blackout_end):
            items.append({"date": blackout_end.isoformat(), "what": "Fed communications blackout ends", "time_et": None, "gated": False})
        for it in items:
            it.update({"in_hold_window": in_hold(dt.date.fromisoformat(it["date"])), "source": "config/fomc.json (federalreserve.gov)"})
        fomc_out += items
        if s <= last <= blackout_end or blackout_start <= first <= blackout_end:
            pass
    blackout_now = None
    for m in fomc["meetings"]:
        s, e = dt.date.fromisoformat(m["start"]), dt.date.fromisoformat(m["end"])
        sat = s - dt.timedelta(days=(s.weekday() - 5) % 7)
        bs, be = sat - dt.timedelta(days=7), e + dt.timedelta(days=(3 - e.weekday()) % 7)
        if bs <= today <= be:
            blackout_now = {"start": bs.isoformat(), "end": be.isoformat(), "meeting": f"{m['start']}..{m['end']}"}
    if not fomc_out and last > dt.date.fromisoformat(fomc["meetings"][-1]["end"]):
        errors.append("hold window extends past config/fomc.json — extend the FOMC calendar")

    # ---- options structure ----
    structure = []
    d = first
    while d <= edge_last:
        tf = third_friday(d.year, d.month)
        if d == prev_trading_day(tf, hol) and (in_hold(d) or in_edge(d)):
            quad = d.month in (3, 6, 9, 12)
            structure.append({"date": d.isoformat(), "what": ("Quad witching · quarterly OpEx" if quad else "Monthly OpEx"), "gated": True, "in_hold_window": in_hold(d)})
        # VIX settlement: Wednesday 30 days before the NEXT month's 3rd Friday
        ny, nm = (d.year + (d.month == 12), d.month % 12 + 1)
        vix = third_friday(ny, nm) - dt.timedelta(days=30)
        if d == vix and (in_hold(d) or in_edge(d)):
            if vix in hol:
                vix = vix - dt.timedelta(days=1)
            structure.append({"date": vix.isoformat(), "what": "VIX monthly settlement (SOQ at the open)", "gated": False, "in_hold_window": in_hold(vix)})
        nxt = d + dt.timedelta(days=1)
        if nxt.month != d.month and (in_hold(d) or in_edge(d)):
            q = d.month in (3, 6, 9, 12)
            structure.append({"date": prev_trading_day(d, hol).isoformat(), "what": ("Quarter-end · rebalance flows" if q else "Month-end · rebalance flows"), "gated": q, "in_hold_window": in_hold(d)})
        d += dt.timedelta(days=1)
    # dedupe
    seen, s2 = set(), []
    for x in structure:
        k = (x["date"], x["what"])
        if k not in seen:
            seen.add(k)
            s2.append(x)
    structure = s2

    # ---- ETF ex-div projections ----
    etf = []
    for sym in ("SPY", "QQQ", "IWM"):
        try:
            dd = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2y&interval=1d&events=div"))
            ev = dd["chart"]["result"][0].get("events", {}).get("dividends", {})
            hist = sorted((dt.datetime.fromtimestamp(int(k), ET).date(), v["amount"]) for k, v in ev.items())
            # any actual ex-date already inside the window?
            actual = [h for h in hist if in_hold(h[0]) or in_edge(h[0])]
            if actual:
                for h in actual:
                    etf.append({"ticker": sym, "ex_date": h[0].isoformat(), "amount": h[1], "status": "declared (Yahoo history)", "in_hold_window": in_hold(h[0])})
                continue
            for h in hist:
                proj = h[0] + dt.timedelta(weeks=52)
                proj = prev_trading_day(proj, hol) if proj.weekday() >= 5 or proj in hol else proj
                if in_hold(proj) or in_edge(proj):
                    etf.append({"ticker": sym, "ex_date": proj.isoformat(), "last_amount": h[1], "last_ex_date": h[0].isoformat(),
                                "status": "PROJECTED from last year's pattern — confirm on issuer page (SSGA / Invesco / iShares)",
                                "in_hold_window": in_hold(proj)})
        except Exception as e:
            errors.append(f"{sym} dividend history: {type(e).__name__}: {e}")

    out = {"generated_et": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "hold_window": [first.isoformat(), last.isoformat()], "edge_last": edge_last.isoformat(),
           "treasury_auctions": auctions, "fomc": sorted(fomc_out, key=lambda x: x["date"]),
           "fed_blackout_now": blackout_now, "structure": sorted(structure, key=lambda x: x["date"]),
           "etf_exdiv": etf, "errors": errors,
           "gate_note": "gated=true items are calendar-chip material by the CATEGORY GATES (10y/20y/30y/TIPS auctions, FOMC decision/minutes, OpEx/quad witching, quarter-end). Bills and 2s/3s/5s/7s are listed for context only."}
    with open(os.path.join(RUN, "scheduled.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("Treasury auctions in window/edge: " + ("; ".join(f"{a['date']} {a['label']} ${a['size_bn']}B {a['time_et']}{' [GATED]' if a['gated'] else ''}" for a in auctions if a["type"] != "Bill") or "none (or API unavailable)"))
    print("FOMC: " + ("; ".join(f"{x['date']} {x['what']}" for x in fomc_out) or "none in window") + (f" · blackout in force {blackout_now['start']}..{blackout_now['end']}" if blackout_now else ""))
    print("Structure: " + ("; ".join(f"{x['date']} {x['what']}" for x in structure) or "none"))
    print("ETF ex-div: " + ("; ".join(f"{x['ticker']} {x['ex_date']} ({x['status'][:9]})" for x in etf) or "none"))
    if errors:
        print("Errors:", "; ".join(errors))
    print("-> wrote run/scheduled.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
