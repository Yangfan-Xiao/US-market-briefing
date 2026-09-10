#!/usr/bin/env python3
"""
market_data.py — fixed Market-Conditions metrics from APIs (no web pages, no LLM).

Fixed list: SPY, QQQ, VIX, US 2Y, US 10Y, US 30Y, WTI, CNN Fear & Greed.
Sources (all reachable from the cloud container without keys, verified 2026-09-10):
  - Yahoo Finance chart API  (SPY, QQQ, ^VIX, ^TNX=10Y, ^TYX=30Y, 2YY=F=2Y yield futures, CL=F=WTI)
  - US Treasury daily par yield curve XML (official prior-close 2Y/10Y/30Y)
  - CNN Fear & Greed JSON

Writes run/market.json. Every metric carries value, delta line, direction, as-of time and source.
A metric that cannot be fetched is written with "ok": false — the renderer shows "n/a" and the
briefing must say so in Assumptions. The model must never type metric numbers by hand.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept": "*/*"}


def get(url, extra=None, timeout=25):
    h = dict(UA)
    h.update(extra or {})
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout).read()


def yahoo_chart(sym, rng, interval, prepost=False):
    u = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym)}"
         f"?range={rng}&interval={interval}&includePrePost={'true' if prepost else 'false'}")
    d = json.loads(get(u))
    r = d["chart"]["result"][0]
    ts = r.get("timestamp") or []
    closes = r["indicators"]["quote"][0].get("close") or []
    pts = [(t, c) for t, c in zip(ts, closes) if c is not None]
    return r["meta"], pts


def fmt_ts(epoch):
    return dt.datetime.fromtimestamp(epoch, ET).strftime("%a %H:%M ET")


def session_state(meta, epoch):
    ctp = meta.get("currentTradingPeriod") or {}
    def within(k):
        p = ctp.get(k) or {}
        return p.get("start") is not None and p["start"] <= epoch < p["end"]
    if within("regular"):
        return "regular"
    if within("pre"):
        return "pre-market"
    if within("post"):
        return "after-hours"
    return "closed"


def promotion_check(daily, last, last_epoch):
    """STATE-VARIABLE PROMOTION RULE, computed: fresh 6-month extreme, or a >=2σ 1-day / 5-day move
    measured against the trailing month's daily changes. Returns a dict; 'flag' True = candidate."""
    today_et = dt.datetime.fromtimestamp(last_epoch, ET).date()
    closes = [c for t, c in daily if dt.datetime.fromtimestamp(t, ET).date() < today_et]
    out = {"flag": False, "extreme": None, "z1": None, "z5": None, "lookback_days": len(closes)}
    if len(closes) < 40:
        return out
    hi, lo = max(closes), min(closes)
    if last >= hi:
        out["extreme"] = f"new {round(len(closes)/21)}-mo high"
    elif last <= lo:
        out["extreme"] = f"new {round(len(closes)/21)}-mo low"
    chg = [b - a for a, b in zip(closes[-22:-1], closes[-21:])]   # last ~21 daily changes
    if len(chg) >= 15:
        mu = sum(chg) / len(chg)
        sd = (sum((x - mu) ** 2 for x in chg) / (len(chg) - 1)) ** 0.5
        if sd > 0:
            out["z1"] = round((last - closes[-1] - mu) / sd, 2)
            out["z5"] = round((last - closes[-5] - 5 * mu) / (sd * 5 ** 0.5), 2)
    out["flag"] = bool(out["extreme"]) or (out["z1"] is not None and abs(out["z1"]) >= 2) or (out["z5"] is not None and abs(out["z5"]) >= 2)
    return out


def yahoo_metric(sym, label, kind):
    """kind: 'price' (2 decimals), 'vix', 'yield' (percent, 2-3 decimals), 'oil'."""
    meta, daily = yahoo_chart(sym, "6mo", "1d")
    try:
        _, intra = yahoo_chart(sym, "1d", "5m", prepost=True)
    except Exception:
        intra = []
    last_epoch, last = (intra[-1] if intra else (meta.get("regularMarketTime"), meta.get("regularMarketPrice")))
    if last is None:
        raise RuntimeError("no price")
    state = session_state(meta, last_epoch)
    # Previous close = last COMPLETED daily bar (dated before the day of the last print).
    # NOTE: meta.chartPreviousClose is the close before the *range* start — wrong for range=1mo.
    today_et = dt.datetime.fromtimestamp(last_epoch, ET).date()
    completed = [(t, c) for t, c in daily if dt.datetime.fromtimestamp(t, ET).date() < today_et]
    prev_close = completed[-1][1] if completed else None
    # sanity cross-check with Yahoo's own day-change fields when the last print is a regular-session print
    rmp, rcp = meta.get("regularMarketPrice"), meta.get("regularMarketChangePercent")
    if prev_close and rmp and rcp is not None and state == "regular":
        implied = rmp / (1 + rcp / 100.0)
        if abs(implied - prev_close) / prev_close > 0.004:   # >0.4% disagreement → trust Yahoo's implied value
            prev_close = implied
    wk_close = completed[-5][1] if len(completed) >= 5 else None
    chg = last - prev_close if prev_close else None
    pct = (chg / prev_close * 100) if (chg is not None and prev_close) else None
    wk_chg = (last - wk_close) if wk_close else None
    wk_pct = (wk_chg / wk_close * 100) if wk_close else None

    if kind == "yield":
        val = f"{last:.2f}%"
        dline = (f"{'▲' if chg > 0 else '▼' if chg < 0 else '■'} {chg*100:+.0f} bp vs prev close"
                 + (f" · wk {wk_chg*100:+.0f} bp" if wk_chg is not None else "")) if chg is not None else "—"
    elif kind == "vix":
        val = f"{last:.2f}"
        dline = (f"{'▲' if chg > 0 else '▼' if chg < 0 else '■'} {chg:+.2f} ({pct:+.1f}%) vs prev close"
                 + (f" · wk {wk_pct:+.1f}%" if wk_pct is not None else "")) if chg is not None else "—"
    else:
        val = f"${last:,.2f}"
        dline = (f"{'▲' if chg > 0 else '▼' if chg < 0 else '■'} {pct:+.2f}% vs prev close"
                 + (f" · wk {wk_pct:+.1f}%" if wk_pct is not None else "")) if chg is not None else "—"
    direction = "flat" if chg is None or abs(chg) < 1e-9 else ("up" if chg > 0 else "down")
    promo = promotion_check(daily, last, last_epoch)
    if promo.get("extreme"):
        dline += f" · {promo['extreme']}"
    return {
        "ok": True, "label": label, "value": val, "delta": dline, "direction": direction,
        "raw": {"last": last, "prev_close": prev_close, "chg": chg, "pct": pct,
                "week_ago_close": wk_close, "week_pct": wk_pct},
        "promotion": promo,
        "as_of": fmt_ts(last_epoch), "as_of_epoch": last_epoch, "session_state": state,
        "source": f"Yahoo Finance chart API ({sym})",
    }


def treasury_yields():
    now = dt.datetime.now(ET)
    rows = []
    for ym in [now.strftime("%Y%m"), (now.replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m")]:
        u = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
             f"?data=daily_treasury_yield_curve&field_tdr_date_value_month={ym}")
        x = get(u).decode("utf-8", "ignore")
        for entry in re.findall(r"<entry>(.*?)</entry>", x, flags=re.S):
            def g(tag):
                m = re.search(rf"<d:{tag}[^>]*>([^<]*)</d:{tag}>", entry)
                return m.group(1) if m else None
            d = g("NEW_DATE")
            if not d:
                continue
            rows.append((d[:10], {"2Y": g("BC_2YEAR"), "10Y": g("BC_10YEAR"), "30Y": g("BC_30YEAR")}))
    rows.sort()
    if not rows:
        raise RuntimeError("no treasury rows")
    latest = rows[-1]
    prev = rows[-2] if len(rows) > 1 else None
    return {"date": latest[0], "yields": {k: float(v) for k, v in latest[1].items() if v},
            "prev_date": prev[0] if prev else None,
            "prev_yields": {k: float(v) for k, v in prev[1].items() if v} if prev else None,
            "source": "US Treasury daily par yield curve (home.treasury.gov)"}


def fear_greed():
    d = json.loads(get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                       {"Accept": "application/json", "Referer": "https://www.cnn.com/markets/fear-and-greed"}))
    fg = d["fear_and_greed"]
    score = fg["score"]
    prev = fg.get("previous_close")
    wk = fg.get("previous_1_week")
    mo = fg.get("previous_1_month")
    rating = fg.get("rating", "").title()
    parts = []
    if prev is not None:
        parts.append(f"prev {prev:.0f}")
    if wk is not None:
        parts.append(f"1w {wk:.0f}")
    if mo is not None:
        parts.append(f"1m {mo:.0f}")
    direction = "flat" if prev is None else ("up" if score > prev else "down" if score < prev else "flat")
    ts = fg.get("timestamp")
    as_of = ts
    try:
        as_of = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ET).strftime("%a %H:%M ET")
    except Exception:
        pass
    return {"ok": True, "label": "CNN Fear & Greed", "value": f"{score:.0f}", "delta": f"{rating} · " + " · ".join(parts),
            "direction": direction, "raw": {"score": score, "rating": rating, "prev": prev, "week": wk, "month": mo},
            "as_of": as_of, "source": "CNN Fear & Greed index JSON"}


def safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def main():
    out_path = os.path.join(ROOT, "run", "market.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tsy = safe(treasury_yields)

    metrics = []
    metrics.append(dict(key="SPY", **safe(yahoo_metric, "SPY", "S&P 500 · SPY", "price")))
    metrics.append(dict(key="QQQ", **safe(yahoo_metric, "QQQ", "Nasdaq 100 · QQQ", "price")))
    metrics.append(dict(key="VIX", **safe(yahoo_metric, "^VIX", "VIX", "vix")))

    # Yields.
    #  10Y / 30Y: live CBOE indices via Yahoo (^TNX / ^TYX); official Treasury prior close appended.
    #  2Y: no liquid live index is reachable → official Treasury close is the value; the CBOT 2-yr
    #      yield future (2YY=F) is appended only when its last print is < 4h old.
    def treasury_metric(label, tkey):
        off = tsy["yields"][tkey]
        prev = (tsy.get("prev_yields") or {}).get(tkey)
        chg = (off - prev) * 100 if prev is not None else None
        return {"ok": True, "label": label, "value": f"{off:.2f}%",
                "delta": (f"{'▲' if chg > 0 else '▼' if chg < 0 else '■'} {chg:+.0f} bp vs prior close" if chg is not None else "—")
                         + f" · Treasury close {tsy['date'][5:]}",
                "direction": "flat" if not chg else ("up" if chg > 0 else "down"),
                "raw": {"last": off, "prev_close": prev}, "as_of": f"{tsy['date']} close", "session_state": "closed",
                "source": tsy["source"]}

    for key, sym, label, tkey in [("US10Y", "^TNX", "US 10-yr", "10Y"), ("US30Y", "^TYX", "US 30-yr", "30Y")]:
        m = safe(yahoo_metric, sym, label, "yield")
        if m.get("ok") and tsy.get("date") and tsy["yields"].get(tkey) is not None:
            off = tsy["yields"][tkey]
            m["delta"] += f" · Tsy close {tsy['date'][5:]}: {off:.2f}%"
            m["official_prior_close"] = {"date": tsy["date"], "yield": off, "source": tsy["source"]}
        elif not m.get("ok") and tsy.get("date") and tsy["yields"].get(tkey) is not None:
            m = treasury_metric(label, tkey)
            m["fallback"] = "Yahoo unavailable; Treasury official close used"
        metrics.append(dict(key=key, **m))

    if tsy.get("date") and tsy["yields"].get("2Y") is not None:
        m2 = treasury_metric("US 2-yr", "2Y")
        fut = safe(yahoo_metric, "2YY=F", "US 2-yr", "yield")
        if fut.get("ok") and (dt.datetime.now(ET).timestamp() - fut["as_of_epoch"]) < 4 * 3600:
            m2["delta"] += f" · 2YY=F live {fut['raw']['last']:.2f}% ({fut['as_of']})"
            m2["live_future"] = {"last": fut["raw"]["last"], "as_of": fut["as_of"], "source": fut["source"]}
    else:
        m2 = safe(yahoo_metric, "2YY=F", "US 2-yr", "yield")
        if m2.get("ok"):
            m2["fallback"] = "Treasury feed unavailable; CBOT 2-yr yield future used"
    metrics.insert(3, dict(key="US2Y", **m2))

    metrics.append(dict(key="WTI", **safe(yahoo_metric, "CL=F", "WTI crude", "oil")))
    metrics.append(dict(key="FG", **safe(fear_greed)))

    promoted = [{"key": m["key"], "label": m["label"], "value": m["value"], **m["promotion"]}
                for m in metrics if m.get("ok") and m.get("promotion", {}).get("flag")]
    out = {"generated_et": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "treasury": tsy, "metrics": metrics,
           "promotion_candidates": promoted,
           "promotion_note": "Each candidate needs a cause search (Tier 1/2). A promoted extreme is printed even if the driver is contested/unidentified (never cut for lacking a cause). Max ONE promoted-variable Heads-up card per run; others ride the Conditions tone line."}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    bad = [m["key"] for m in metrics if not m.get("ok")]
    for m in metrics:
        if m.get("ok"):
            p = m.get("promotion") or {}
            ptxt = f"  PROMOTION-CANDIDATE z1={p.get('z1')} z5={p.get('z5')}" if p.get("flag") else ""
            print(f"{m['key']:6} {m['value']:>10}  {m['delta']}  [{m.get('session_state','')} {m['as_of']}]{ptxt}")
        else:
            print(f"{m['key']:6} UNAVAILABLE  {m.get('error')}")
    print(f"-> wrote {out_path}" + (f"  (unavailable: {', '.join(bad)})" if bad else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
