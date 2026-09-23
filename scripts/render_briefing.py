#!/usr/bin/env python3
"""
render_briefing.py — validate run/content.json and render the briefing HTML.

Inputs (all in run/): window.json (session_window.py), market.json (market_data.py),
events.json (watchlist_events.py, optional but recommended), content.json (written by the model).
Template: template/briefing_template.html (format only — the model never edits or reads it).

Outputs:
  run/briefing-<YYYY-MM-DD>-<HHMM>.html   full standalone document (for files / downloads)
  run/artifact.html                        same page as an Artifact-tool fragment (no doctype/html/head/body)
  run/render_report.json                   validation errors / warnings

Exit code 1 on validation ERRORS (nothing is rendered). Warnings render but are listed.

Usage: python3 scripts/render_briefing.py [--content run/content.json] [--check-only]
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys

# The ✗ / ⚠ glyphs printed below are not encodable in every console codepage
# (cp936 raises UnicodeEncodeError mid-report). Force UTF-8; a no-op where it already is.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "run")

try:
    import jinja2
    import jsonschema
except ImportError:
    print("Missing dependency. Run: pip install jinja2 jsonschema --break-system-packages", file=sys.stderr)
    sys.exit(2)

PILL_CLASS = {"⚠ binary": "p-bin", "ex-div": "p-exdiv", "flow": "p-flow", "capital return": "p-pos",
              "overhang": "p-filed", "[FILED]": "p-filed", "[REPORTED]": "p-filed", "rumor · unconfirmed": "p-filed"}
BANNED = [r"\bwhether\b", r"\bwatch (if|for whether)\b", r"\beyes on\b", r"\bkeep an eye\b", r"\bremains to be seen\b"]
CONTINUITY = [r"\bUPDATE\s*[—–-]\s*day\b", r"\bday\s+\d+\s*[·:]", r"^\s*NEW[.·]", r"\bRESOLVED[.·]", r"\bUNCHANGED\b", r"\bcarry-over\b", r"\bcarried over\b", r"\bprevious briefing\b", r"\byesterday's briefing\b"]
LABEL_ORDER = {"overnight": 0, "pre-open": 60, "pre-market": 60, "before the open": 60, "bmo": 60,
               "all session": 9 * 60 + 31, "intraday": 9 * 60 + 31, "amc": 16 * 60 + 5, "after close": 16 * 60 + 5,
               "after the close": 16 * 60 + 5, "after-hours": 16 * 60 + 5, "tbd": 23 * 60, "weekend": 12 * 60}


# ---------- text filters ----------
def inline(s):
    """escape everything, then allow **bold** only."""
    if s is None:
        return ""
    t = html.escape(str(s), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return jinja2.Markup(t) if hasattr(jinja2, "Markup") else __import__("markupsafe").Markup(t)


def plain(s):
    return html.escape(re.sub(r"\*\*", "", str(s or "")), quote=True)


def isofix(s):
    # "2026-09-10T09:30:00-0400" -> "2026-09-10T09:30:00-04:00"
    return re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", s)


def human(d):
    o = dt.date.fromisoformat(d)
    return f"{o.strftime('%b')} {o.day}"   # not %-d: glibc-only, ValueError on Windows


def load(name, required=True):
    p = os.path.join(RUN, name)
    if not os.path.exists(p):
        if required:
            raise SystemExit(f"missing {p}")
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ---------- validation ----------
def validate(c, w, ev, wl):
    errors, warnings = [], []
    with open(os.path.join(ROOT, "schema", "content.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    v = jsonschema.Draft202012Validator(schema)
    for e in sorted(v.iter_errors(c), key=lambda e: list(e.path)):
        errors.append(f"schema: {'/'.join(str(p) for p in e.path) or '<root>'}: {e.message[:200]}")
    if errors:
        return errors, warnings  # structural problems first

    cov_days = {d["date"] for d in w["coverage"]["calendar_days"]}
    focus = w["focus_session"]["date"]
    hold_days = {d["date"] for d in w["hold_window"]["days"] if not d["closed"]}
    closed_days = {d["date"] for d in w["hold_window"]["days"] if d["closed"]}
    tickers = {s["ticker"] for s in wl["symbols"]} | {s["ticker"].lstrip("$") for s in wl["symbols"]}

    # earnings dates known from the API
    api_earn = {}
    if ev:
        for t, info in ev.get("symbols", {}).items():
            for d in (info.get("earnings_dates") or []):
                api_earn.setdefault(t, set()).add(d)
        confirmed = {r["ticker"]: r["date"] for r in ev.get("earnings_in_hold_window", []) + ev.get("earnings_just_past_edge", [])
                     if "agree" in (r.get("confirmation") or "")}
    else:
        confirmed = {}

    def check_text(path, s):
        if not s:
            return
        for pat in BANNED:
            if re.search(pat, s, flags=re.I):
                errors.append(f"{path}: banned construction /{pat}/ — write a declarative thesis, not a question")
        for pat in CONTINUITY:
            if re.search(pat, s, flags=re.I | re.M):
                errors.append(f"{path}: continuity token /{pat}/ — briefings are stateless; describe the event, not its history in prior briefings")

    check_text("toplead", c["toplead"])
    check_text("bottom_line", c["bottom_line"])
    for i, h in enumerate(c["heads_up"]):
        check_text(f"heads_up[{i}].title", h["title"])
        check_text(f"heads_up[{i}].desc", h["desc"])
    for i, n in enumerate(c["news"]):
        check_text(f"news[{i}].text", n["text"])
    for i, s in enumerate(c["symbols"]):
        check_text(f"symbols[{i}].summary", s["summary"])
        for j, b in enumerate(s["bullets"]):
            check_text(f"symbols[{i}].bullets[{j}]", b)
    for i, t in enumerate(c["timeline"]):
        check_text(f"timeline[{i}].why", t["why"])

    def earnings_guard(path, ticker, date):
        t = (ticker or "").lstrip("$").upper()
        if not t:
            return
        if t in confirmed and confirmed[t] != date:
            errors.append(f"{path}: {t} earnings dated {date} but the API-confirmed date is {confirmed[t]}")
        elif t in api_earn and date not in api_earn[t]:
            errors.append(f"{path}: {t} earnings dated {date}; API shows {sorted(api_earn[t])} — verify with company IR and fix the date or the item")

    # timeline
    for i, t in enumerate(c["timeline"]):
        p = f"timeline[{i}]"
        if t["date"] not in cov_days:
            errors.append(f"{p}: date {t['date']} is outside the coverage window {sorted(cov_days)[0]}..{sorted(cov_days)[-1]}")
        if t.get("event_type") == "earnings":
            earnings_guard(p, t.get("ticker"), t["date"])
        elif re.search(r"\bearnings\b|\bresults\b|\breports?\b (after|before)", t["label"], flags=re.I):
            m = re.search(r"\b([A-Z]{2,5})\b", t["label"])
            if m and m.group(1) in tickers:
                earnings_guard(p, m.group(1), t["date"])
        if t["time_et"] is None and t["time_label"].strip().lower() not in LABEL_ORDER and not re.match(r"^~?\d", t["time_label"]):
            warnings.append(f"{p}: no time_et and unusual time_label '{t['time_label']}' — it will sort mid-day")
        if t["kind"] in ("open", "close") and t["date"] not in {s["date"] for s in w["coverage"]["sessions_in_window"]}:
            errors.append(f"{p}: open/close row on {t['date']} which is not a session in the coverage window")

    # heads-up
    for i, h in enumerate(c["heads_up"]):
        if h.get("event_type") == "earnings" and h.get("date"):
            earnings_guard(f"heads_up[{i}]", h.get("ticker"), h["date"])
        if h["kind"] == "bin" and h["badge_class"] not in ("b-bin", "b-name"):
            warnings.append(f"heads_up[{i}]: kind=bin usually pairs with badge_class b-bin (macro) or b-name (single name)")
    # symbols
    seen = set()
    for i, s in enumerate(c["symbols"]):
        t = s["ticker"].lstrip("$").upper()
        if t not in tickers and s["ticker"] != "EX-DIV":
            errors.append(f"symbols[{i}]: {s['ticker']} is not on the watchlist")
        if t in seen:
            errors.append(f"symbols[{i}]: duplicate card for {t}")
        seen.add(t)
        for e in s.get("events", []) or []:
            if e["event_type"] == "earnings":
                earnings_guard(f"symbols[{i}].events", t, e["date"])
    # calendar
    for d, chips in c["calendar"].items():
        if d in closed_days:
            errors.append(f"calendar[{d}]: market is closed that day — chips not allowed (the card is auto-rendered as CLOSED)")
        elif d not in hold_days:
            errors.append(f"calendar[{d}]: not a hold-window trading day ({w['hold_window']['first']}..{w['hold_window']['last']})")
        for ch in chips:
            if ch.get("event_type") == "earnings":
                earnings_guard(f"calendar[{d}]", ch.get("ticker"), d)
            elif re.search(r"\bearnings\b|\bAMC\b|\bBMO\b", ch["text"]):
                m = re.search(r"\b([A-Z]{2,5})\b", ch["text"])
                if m and m.group(1) in tickers:
                    earnings_guard(f"calendar[{d}] '{ch['text']}'", m.group(1), d)
    # API events that must appear somewhere
    if ev:
        for r in ev.get("earnings_in_hold_window", []):
            if "agree" in (r.get("confirmation") or "") or "confirmed" in (r.get("confirmation") or ""):
                if not any(r["ticker"] in ch["text"] for ch in c["calendar"].get(r["date"], [])):
                    warnings.append(f"API-confirmed earnings {r['ticker']} {r['date']} has no calendar chip on that day")
    # gated mechanical items from scheduled.json must be a chip on their day — or an explicit cut
    sc = load("scheduled.json", required=False)
    if sc:
        cut_text = " ".join((x["item"] + " " + x["reason"]).lower() for x in c["cut_for_cause"])
        def has_chip(date, keys):
            chips = " ".join(ch["text"].lower() for ch in c["calendar"].get(date, []))
            rows = " ".join(t["label"].lower() for t in c["timeline"] if t["date"] == date)
            return any(k in chips or k in rows for k in keys)
        def is_cut(keys):
            return any(k in cut_text for k in keys)
        def label_keys(lbl):
            # "10-yr" → 10-yr / 10-year / 10y / 10 yr — never the bare word "auction", which would let a cut line
            # about the 2/5/7-yr auctions silently excuse a missing 10-yr/30-yr chip
            lbl = lbl.lower()
            return [lbl, lbl.replace("-yr", "-year"), lbl.replace("-yr", "y"), lbl.replace("-yr", " yr")]
        run_day = w["run_start_et"][:10]
        run_hm = w["run_start_et"][11:16]
        for a in sc.get("treasury_auctions", []):
            if not a["gated"] or not a["in_hold_window"]:
                continue
            if a["date"] == run_day and a["time_et"] <= run_hm:
                continue  # already elapsed at run start
            keys = label_keys(a["label"]) + ["auction"]
            if not has_chip(a["date"], keys) and not is_cut(label_keys(a["label"])):
                msg = f"scheduled: {a['date']} {a['label']} Treasury auction (${a['size_bn']}B, {a['time_et']} ET) has no calendar chip/timeline row and is not in cut_for_cause"
                if a["type"] == "TIPS" or a["label"].startswith("20"):
                    warnings.append(msg + " — 20-yr/TIPS are gated only when duration is the day's story; add a chip or cut with reason")
                else:
                    errors.append(msg + " — 10-yr/30-yr auctions always earn a chip (CATEGORY GATES)")
        for x in sc.get("fomc", []):
            if not x["gated"] or not x["in_hold_window"]:
                continue
            if not has_chip(x["date"], ["fomc", "fed decision", "minutes"]) and not is_cut(["fomc"]):
                errors.append(f"scheduled: {x['date']} {x['what']} has no calendar chip — add it")
        for x in sc.get("structure", []):
            if not x["gated"] or not x["in_hold_window"]:
                continue
            if not has_chip(x["date"], ["opex", "witching", "quarter-end", "quarter end"]) and not is_cut(["opex", "witching", "quarter-end"]):
                warnings.append(f"scheduled: {x['date']} {x['what']} has no calendar chip")
        for x in sc.get("etf_exdiv", []):
            if not x["in_hold_window"]:
                continue
            t = x["ticker"].lower()
            if not has_chip(x["ex_date"], [t]) and not is_cut([t + " ex-div", t + " ex div", t + " ex-dividend"]):
                warnings.append(f"scheduled: {x['ticker']} ex-div {x['ex_date']} ({x['status'][:9]}) has no calendar chip — confirm on the issuer page and add it, or cut with reason")
    if len(c["heads_up"]) > 5:
        errors.append("heads_up: more than 5 cards")

    # exposure chips must name watchlist tickers
    for sect in ("heads_up", "news"):
        for i, it in enumerate(c[sect]):
            for x in it.get("exposed", []) or []:
                if x["ticker"].lstrip("$").upper() not in tickers:
                    errors.append(f"{sect}[{i}].exposed: {x['ticker']} is not on the watchlist (name the watchlist ticker the item transmits to)")

    # length budget — a short toplead and tight cards are the point of the page
    if words(c["toplead"]) > TOPLEAD_WORDS:
        warnings.append(f"toplead: {words(c['toplead'])} words (budget {TOPLEAD_WORDS}) — cut to driver + mechanism + resolver")
    for i, h in enumerate(c["heads_up"]):
        if words(h["desc"]) > HU_DESC_WORDS:
            warnings.append(f"heads_up[{i}].desc: {words(h['desc'])} words (budget {HU_DESC_WORDS}) — move tickers to 'exposed' and the resolver to 'resolves'")

    # CATEGORY GATE: 2/3/5/7-yr coupons are routine plumbing — no chip or timeline row unless explicitly justified
    kept_short = any(re.search(r"short-coupon auction kept", a, flags=re.I) for a in c["assumptions"])
    if not kept_short:
        for d, chips in c["calendar"].items():
            for ch in chips:
                if SHORT_COUPON.search(ch["text"]):
                    errors.append(f"calendar[{d}] '{ch['text']}': 2/3/5/7-yr auctions fail the CATEGORY GATE — drop the chip, or add an assumption starting 'Short-coupon auction kept:' with the tail + rates-driver reason")
        for i, t in enumerate(c["timeline"]):
            if SHORT_COUPON.search(t["label"]):
                errors.append(f"timeline[{i}] '{t['label']}': 2/3/5/7-yr auctions fail the CATEGORY GATE (see calendar rule)")

    # an item cut for cause must not reappear as a chip
    cut_items = [x["item"].lower() for x in c["cut_for_cause"]]
    for d, chips in c["calendar"].items():
        for ch in chips:
            toks = [t for t in re.findall(r"[a-z]{3,}", ch["text"].lower()) if t not in STOP]
            if len(toks) < 2:
                continue
            for ci in cut_items:
                if sum(t in ci for t in toks) >= max(2, round(len(toks) * 0.67)):
                    warnings.append(f"calendar[{d}] '{ch['text']}' looks like cut item '{ci[:60]}' — an item in Cut for cause gets no chip")
                    break

    # freshness: a News line about an event more than 3 sessions old needs a dated forward pivot in the hold window
    run_day = dt.date.fromisoformat(w["run_start_et"][:10])
    for i, n in enumerate(c["news"]):
        if not n.get("event_date"):
            continue
        age = sessions_between(dt.date.fromisoformat(n["event_date"]), run_day)
        if age > 3 and n.get("gates_date") not in hold_days:
            warnings.append(f"news[{i}]: event dated {n['event_date']} is {age} sessions old with no gates_date inside the hold window — fails Freshness (A.4); cut it or name the forward pivot")

    # read-through earnings inside the coverage window should be judged, not missed
    if ev:
        page_text = json.dumps(c, ensure_ascii=False)
        for r in ev.get("read_through_earnings", []):
            if r["window"] == "coverage" and r["why_listed"] == "exposure map" and not re.search(rf"\b{re.escape(r['ticker'])}\b", page_text):
                warnings.append(f"read-through: {r['ticker']} ({r['name']}) reports {r['date']} {r['report_time']} inside the coverage window "
                                f"→ {', '.join(x['ticker'] for x in r['exposed'])} — add a timeline row / chip, or cut with reason")
    return errors, warnings


TOPLEAD_WORDS, HU_DESC_WORDS = 45, 55
SHORT_COUPON = re.compile(r"\b(2|3|5|7)[- ]?(yr|year|y)\b[^,;]*\b(auction|reopen)|\b(auction|reopen)\w*\b[^,;]*\b(2|3|5|7)[- ]?(yr|year|y)\b", re.I)
EVENT_WORD = {"earnings": "earnings", "exdiv": "ex-div", "lockup": "lockup", "index": "index event", "fed": "Fed",
              "macro": "macro", "auction": "auction", "opex": "OpEx", "other": "event"}
STOP = {"the", "and", "for", "with", "est", "prelim", "final", "day", "amc", "bmo", "tbd", "sep", "oct", "nov", "dec", "jan"}


def words(s):
    return len(re.findall(r"\S+", re.sub(r"\*\*", "", s or "")))


def sessions_between(a, b):
    """weekdays after a up to and including b (holidays ignored — a freshness heuristic, not a calendar)."""
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        n += d.weekday() < 5
    return n


# ---------- watchlist exposure strip ----------
def build_exposure(c, ev, wl, sc):
    """Highest grade touching each watchlist name, with short reasons — computed from content + API facts."""
    order = [s["ticker"] for s in wl["symbols"]]
    key = {t.lstrip("$").upper(): t for t in order}
    cells = {t: {"ticker": t, "grade": 0, "reasons": []} for t in order}

    def hit(tk, grade, reason):
        t = key.get((tk or "").lstrip("$").upper())
        if not t:
            return
        cell = cells[t]
        cell["grade"] = max(cell["grade"], grade)
        cell["reasons"].append((grade, reason))

    for s in c["symbols"]:
        hit(s["ticker"], s["grade"], s["pills"][0] if s["pills"] else "catalyst")
    for h in c["heads_up"]:
        if h.get("ticker"):
            hit(h["ticker"], h["grade"], EVENT_WORD.get(h.get("event_type"), "heads-up") + (f" {human(h['date'])}" if h.get("date") else ""))
        for x in h.get("exposed", []) or []:
            hit(x["ticker"], h["grade"], x["channel"])
    for n in c["news"]:
        for x in n.get("exposed", []) or []:
            hit(x["ticker"], n["grade"], x["channel"])
    if ev:
        cov = {r["ticker"] for r in ev.get("earnings_in_coverage", [])}
        for r in ev.get("earnings_in_hold_window", []):
            hit(r["ticker"], 3 if r["ticker"] in cov else 2, f"earnings {human(r['date'])}")
        for r in ev.get("exdiv_in_hold_window", []):
            hit(r["ticker"], 1, f"ex-div {human(r['ex_date'])}")
        for r in ev.get("read_through_earnings", []):
            if r["window"] != "edge" and r["why_listed"] == "exposure map":
                for x in r["exposed"]:
                    hit(x["ticker"], 1, f"{r['ticker']} earns {human(r['date'])}")
    for x in (sc or {}).get("etf_exdiv", []):
        if x.get("in_hold_window"):
            hit(x["ticker"], 1, f"ex-div {human(x['ex_date'])}")
    out = []
    for t in order:
        cell = cells[t]
        rs = sorted(cell["reasons"], key=lambda r: -r[0])
        seen, uniq = set(), []
        for g, r in rs:
            if r not in seen:
                seen.add(r)
                uniq.append(r)
        cell["top"] = uniq[0] if uniq else "clear"
        cell["title"] = " · ".join(uniq) if uniq else "no catalyst in the hold window"
        out.append(cell)
    return out


# ---------- timeline assembly ----------
def cn_time(hhmm, offset_h, date_iso):
    h, m = map(int, hhmm.split(":"))
    base = dt.datetime.fromisoformat(date_iso) + dt.timedelta(hours=h + offset_h, minutes=m)
    roll = (base.date() - dt.date.fromisoformat(date_iso)).days
    return base.strftime("%H:%M") + " GMT+8" + (f" ({base.strftime('%a')})" if roll else "")


def build_timeline(c, w):
    off = w["cn_minus_et_hours"]
    focus = w["focus_session"]["date"]
    sessions = {s["date"]: s for s in w["coverage"]["sessions_in_window"]}
    by_day = {}
    provided_oc = {(t["date"], t["kind"]) for t in c["timeline"] if t["kind"] in ("open", "close")}
    # auto open/close rows for every session in the window
    for d, s in sessions.items():
        if (d, "open") not in provided_oc:
            by_day.setdefault(d, []).append({"date": d, "time_et": s["open_et"], "time_label": f"{s['open_et']} ET", "kind": "open",
                                             "label": "Cash open", "why": "Opening auction — start of your trading window." if d == focus else "Opening auction.", "consensus": None, "grade": None})
        if (d, "close") not in provided_oc:
            by_day.setdefault(d, []).append({"date": d, "time_et": s["close_et"], "time_label": f"{s['close_et']} ET", "kind": "close",
                                             "label": "Cash close" + (" (early close)" if s["early_close"] else ""), "why": "Regular session ends; after-hours to 20:00 ET.", "consensus": None, "grade": None})
    for t in c["timeline"]:
        by_day.setdefault(t["date"], []).append(dict(t))
    days = []
    for dd in w["coverage"]["calendar_days"]:
        d = dd["date"]
        evs = by_day.get(d, [])
        if not evs and dd["trading_day"] and d != w["coverage"]["end_session_date"]:
            continue
        note = None
        if not dd["trading_day"]:
            note = f"market closed — {dd['holiday']}" if dd.get("holiday") else "no session"
        elif d == w["coverage"]["end_session_date"] and d not in sessions:
            note = "coverage ends at the open"
        if not evs and not dd["trading_day"]:
            continue
        for e in evs:
            if e["time_et"]:
                e["sort"] = int(e["time_et"][:2]) * 60 + int(e["time_et"][3:])
                e["gmt8_label"] = cn_time(e["time_et"], off, d)
            else:
                key = e["time_label"].strip().lower()
                e["sort"] = LABEL_ORDER.get(key, 12 * 60)
                e["gmt8_label"] = {"amc": f"after {cn_time('16:00', off, d)}", "after close": f"after {cn_time('16:00', off, d)}",
                                   "after the close": f"after {cn_time('16:00', off, d)}", "pre-open": f"before {cn_time('09:30', off, d)}",
                                   "pre-market": f"before {cn_time('09:30', off, d)}", "all session": "—"}.get(key, "—")
        evs.sort(key=lambda e: (e["sort"], e["kind"] != "open"))
        days.append({"date": d, "weekday": dd["weekday"], "human": human(d), "note": note, "events": evs})
    axis_events = [e for e in by_day.get(focus, []) if e["time_et"] and e["kind"] not in ("open", "close")]
    return days, axis_events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", default=os.path.join(RUN, "content.json"))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    w = load("window.json")
    m = load("market.json")
    ev = load("events.json", required=False)
    with open(a.content, encoding="utf-8") as f:
        c = json.load(f)
    with open(os.path.join(ROOT, "config", "watchlist.json"), encoding="utf-8") as f:
        wl = json.load(f)

    errors, warnings = validate(c, w, ev, wl)
    report = {"errors": errors, "warnings": warnings}
    with open(os.path.join(RUN, "render_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    if errors:
        print("VALIDATION ERRORS — nothing rendered:")
        for e in errors:
            print("  ✗", e)
        return 1
    for x in warnings:
        print("  ⚠", x)
    if a.check_only:
        print("content.json OK")
        return 0

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(ROOT, "template")),
                             autoescape=True, trim_blocks=True, lstrip_blocks=True)
    env.filters["inline"] = inline
    env.filters["plain"] = plain
    env.filters["isofix"] = isofix
    tpl = env.get_template("briefing_template.html")

    off = w["cn_minus_et_hours"]
    timeline_days, axis_events = build_timeline(c, w)
    cal_days = []
    for d in w["hold_window"]["days"]:
        row = dict(d, human=human(d["date"]), chips=c["calendar"].get(d["date"], []))
        cal_days.append(row)
    edge_human = " · ".join(f"{e['weekday']} {human(e['date'])}" for e in w["hold_window"]["edge_days"])
    ev_summary = ", ".join(f"{r['ticker']} {r['date']} {r.get('report_time', '')} [{r['confirmation']}]" for r in (ev or {}).get("earnings_in_coverage", [])) or "none"
    exdiv_summary = ", ".join(f"{r['ticker']} {r['ex_date']}" for r in (ev or {}).get("exdiv_in_hold_window", [])) or "none from API (ETF ex-divs need issuer check)"
    unavailable = [x["key"] for x in m["metrics"] if not x.get("ok")]
    exposure = build_exposure(c, ev, wl, load("scheduled.json", required=False))

    page = tpl.render(
        w=w, m=m, c=c,
        focus_human=human(w["focus_session"]["date"]),
        hold_first_human=human(w["hold_window"]["first"]), hold_last_human=human(w["hold_window"]["last"]),
        edge_human=edge_human, cal_days=cal_days, timeline_days=timeline_days, axis_events=axis_events,
        coverage_end_iso=dt.datetime.fromisoformat(w["coverage"]["end_et"]).strftime("%Y-%m-%dT%H:%M:%S") + ("-0400" if w["et_label"] == "EDT" else "-0500"),
        cn=lambda h, mi: f"{(h + off) % 24:02d}:{mi:02d}",
        pill_class=lambda p: PILL_CLASS.get(p, "p-filed"),
        ev_summary=ev_summary, exdiv_summary=exdiv_summary, unavailable=unavailable, exposure=exposure,
    )

    # artifact fragment (Artifact tool adds doctype/html/head/body itself)
    art_path = os.path.join(RUN, "artifact.html")
    with open(art_path, "w", encoding="utf-8") as f:
        f.write(page)
    # full standalone document
    i = page.find('<div class="wrap">')
    head, body = page[:i], page[i:]
    full = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + head + '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    stamp = dt.datetime.strptime(w["run_start_et"][:16], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d-%H%M")
    full_path = os.path.join(RUN, f"briefing-{stamp}.html")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(full)
    print(f"rendered {full_path} ({len(full)//1024} KB) and {art_path}")
    print(f"heads-up {len(c['heads_up'])} · news {len(c['news'])} · symbol cards {len(c['symbols'])} · timeline rows {sum(len(d['events']) for d in timeline_days)} · axis markers {len(axis_events)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
