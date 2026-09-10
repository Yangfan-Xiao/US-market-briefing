#!/usr/bin/env python3
"""
session_window.py — deterministic time/calendar facts for one briefing run.

Writes run/window.json and prints a short human summary.

Coverage rule (from the trading-desk spec):
  coverage_end = the earliest regular-session OPEN (09:30 ET on an NYSE trading day)
                 that is at least 24 hours after run_start.
  Examples: run Wed 08:00 ET -> Thu 09:30 ET;  run Wed 11:00 ET -> Fri 09:30 ET;
            run Fri 21:00 ET -> Mon 09:30 ET.

Focus session (the single timeline axis):
  today's session if its close is still ahead of run_start, else the next trading day.

Usage:
  python3 scripts/session_window.py                  # now
  python3 scripts/session_window.py --at "2026-09-09T11:00"   # simulate an ET run time
  python3 scripts/session_window.py --selftest       # check the three spec examples
"""
import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
CN = ZoneInfo("Asia/Shanghai")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL_PATH = os.path.join(ROOT, "config", "nyse_calendar.json")
HOLD_WINDOW_SESSIONS = 10   # hold-window calendar length in trading days (incl. focus day)


def load_cal():
    with open(CAL_PATH, encoding="utf-8") as f:
        return json.load(f)


def hhmm(s):
    h, m = s.split(":")
    return int(h), int(m)


class Calendar:
    def __init__(self, cal):
        self.hol = {dt.date.fromisoformat(k): v for k, v in cal["holidays"].items()}
        self.early = {dt.date.fromisoformat(k): v for k, v in cal["early_closes"].items()}
        self.open_hm = hhmm(cal["regular_open"])
        self.close_hm = hhmm(cal["regular_close"])
        self.early_hm = hhmm(cal["early_close"])
        self.ah_hm = hhmm(cal["after_hours_end"])
        self.pm_hm = hhmm(cal["premarket_start"])
        self.max_known = max(self.hol) if self.hol else None

    def is_trading_day(self, d):
        return d.weekday() < 5 and d not in self.hol

    def next_trading_day(self, d, inclusive=False):
        x = d if inclusive else d + dt.timedelta(days=1)
        for _ in range(60):
            if self.is_trading_day(x):
                return x
            x += dt.timedelta(days=1)
        raise RuntimeError("no trading day found")

    def open_dt(self, d):
        return dt.datetime(d.year, d.month, d.day, *self.open_hm, tzinfo=ET)

    def close_dt(self, d):
        hm = self.early_hm if d in self.early else self.close_hm
        return dt.datetime(d.year, d.month, d.day, *hm, tzinfo=ET)

    def ah_end_dt(self, d):
        return dt.datetime(d.year, d.month, d.day, *self.ah_hm, tzinfo=ET)

    def session(self, d):
        return {
            "date": d.isoformat(),
            "weekday": d.strftime("%a"),
            "open_et": self.open_dt(d).strftime("%H:%M"),
            "close_et": self.close_dt(d).strftime("%H:%M"),
            "early_close": d in self.early,
            "early_close_reason": self.early.get(d),
        }


def compute(run_start, cal):
    """run_start: aware datetime (any tz). Returns the window dict."""
    now = run_start.astimezone(ET)
    today = now.date()

    # coverage end: earliest open >= now + 24h
    cand = cal.next_trading_day(today, inclusive=True)
    while cal.open_dt(cand) - now < dt.timedelta(hours=24):
        cand = cal.next_trading_day(cand)
    coverage_end = cal.open_dt(cand)

    # focus session
    if cal.is_trading_day(today) and now < cal.close_dt(today):
        focus = today
    else:
        focus = cal.next_trading_day(today)
    focus_state = ("pre-open" if now < cal.open_dt(focus)
                   else "in-progress" if now < cal.close_dt(focus) else "closed")

    # sessions whose regular hours intersect [now, coverage_end)
    sessions_in_window = []
    d = cal.next_trading_day(today, inclusive=True)
    while cal.open_dt(d) < coverage_end:
        if cal.close_dt(d) > now:
            s = cal.session(d)
            s["status"] = "in-progress" if now > cal.open_dt(d) else "full"
            sessions_in_window.append(s)
        d = cal.next_trading_day(d)

    # calendar days spanned by coverage (for dated timeline list)
    days = []
    d = today
    while d <= coverage_end.date():
        entry = {"date": d.isoformat(), "weekday": d.strftime("%a"),
                 "trading_day": cal.is_trading_day(d),
                 "holiday": cal.hol.get(d)}
        if cal.is_trading_day(d):
            entry.update({"open_et": cal.open_dt(d).strftime("%H:%M"),
                          "close_et": cal.close_dt(d).strftime("%H:%M"),
                          "early_close": d in cal.early})
        days.append(entry)
        d += dt.timedelta(days=1)

    # hold-window calendar: from focus day, HOLD_WINDOW_SESSIONS trading days,
    # weekdays listed (holidays included as closed cards), weekends skipped
    hold_days, cnt, d = [], 0, focus
    while cnt < HOLD_WINDOW_SESSIONS:
        if d.weekday() < 5:
            if cal.is_trading_day(d):
                cnt += 1
                hold_days.append({"date": d.isoformat(), "weekday": d.strftime("%a"), "closed": False,
                                  "early_close": d in cal.early,
                                  "is_focus": d == focus,
                                  "in_coverage": cal.open_dt(d) < coverage_end or d == coverage_end.date()})
            else:
                hold_days.append({"date": d.isoformat(), "weekday": d.strftime("%a"), "closed": True,
                                  "reason": cal.hol.get(d), "is_focus": False, "in_coverage": False})
        d += dt.timedelta(days=1)
    hold_last = dt.date.fromisoformat(hold_days[-1]["date"])
    # edge: the 3 trading days just past the hold window
    edge, d = [], cal.next_trading_day(hold_last)
    for _ in range(3):
        edge.append({"date": d.isoformat(), "weekday": d.strftime("%a")})
        d = cal.next_trading_day(d)

    utc_off = now.utcoffset().total_seconds() / 3600
    out = {
        "run_start_et": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "run_start_et_human": now.strftime("%a %b %d, %Y %H:%M ET"),
        "run_start_cn_human": now.astimezone(CN).strftime("%a %b %d, %Y %H:%M GMT+8"),
        "et_utc_offset_hours": utc_off,
        "et_label": "EDT" if utc_off == -4 else "EST",
        "cn_minus_et_hours": 12 if utc_off == -4 else 13,
        "coverage": {
            "start_et": now.strftime("%Y-%m-%dT%H:%M"),
            "end_et": coverage_end.strftime("%Y-%m-%dT%H:%M"),
            "end_human_et": coverage_end.strftime("%a %b %d, %H:%M ET"),
            "end_human_cn": coverage_end.astimezone(CN).strftime("%a %b %d, %H:%M GMT+8"),
            "hours": round((coverage_end - now).total_seconds() / 3600, 1),
            "end_session_date": coverage_end.date().isoformat(),
            "sessions_in_window": sessions_in_window,
            "calendar_days": days,
        },
        "focus_session": dict(cal.session(focus), state=focus_state,
                              open_iso=cal.open_dt(focus).strftime("%Y-%m-%dT%H:%M:%S%z"),
                              close_iso=cal.close_dt(focus).strftime("%Y-%m-%dT%H:%M:%S%z"),
                              ah_end_iso=cal.ah_end_dt(focus).strftime("%Y-%m-%dT%H:%M:%S%z")),
        "hold_window": {"sessions": HOLD_WINDOW_SESSIONS,
                        "first": hold_days[0]["date"], "last": hold_days[-1]["date"],
                        "days": hold_days, "edge_days": edge},
        "calendar_source": "config/nyse_calendar.json",
        "calendar_known_through": cal.max_known.isoformat() if cal.max_known else None,
    }
    return out


def summary(w):
    fs = w["focus_session"]
    lines = [
        f"Run start : {w['run_start_et_human']}  ({w['run_start_cn_human']})  [{w['et_label']}, GMT+8 = ET+{w['cn_minus_et_hours']}h]",
        f"Coverage  : now -> {w['coverage']['end_human_et']} open  ({w['coverage']['hours']}h; {w['coverage']['end_human_cn']})",
        f"Sessions in coverage: " + (", ".join(f"{s['weekday']} {s['date']} ({s['status']}{', early close' if s['early_close'] else ''})" for s in w['coverage']['sessions_in_window']) or "none (weekend/holiday gap)"),
        f"Focus axis: {fs['weekday']} {fs['date']} {fs['open_et']}-{fs['close_et']} ET, state={fs['state']}",
        f"Hold window: {w['hold_window']['first']} -> {w['hold_window']['last']} ({w['hold_window']['sessions']} sessions); edge: " + ", ".join(e['date'] for e in w['hold_window']['edge_days']),
    ]
    closed = [d for d in w["hold_window"]["days"] if d["closed"]]
    early = [d for d in w["hold_window"]["days"] if not d["closed"] and d["early_close"]]
    if closed:
        lines.append("Closed in hold window: " + ", ".join(f"{d['date']} ({d['reason']})" for d in closed))
    if early:
        lines.append("Early close (13:00) in hold window: " + ", ".join(d["date"] for d in early))
    return "\n".join(lines)


def selftest(cal):
    cases = [
        ("2026-09-09T08:00", "2026-09-10T09:30"),   # Wed 8am -> Thu open
        ("2026-09-09T11:00", "2026-09-11T09:30"),   # Wed 11am -> Fri open
        ("2026-09-11T21:00", "2026-09-14T09:30"),   # Fri 9pm -> Mon open
        ("2026-09-04T11:00", "2026-09-08T09:30"),   # Fri before Labor Day -> Tue open
        ("2026-11-25T08:00", "2026-11-27T09:30"),   # Wed before Thanksgiving -> Fri open (early close day)
        ("2026-09-10T09:29", "2026-09-11T09:30"),   # 09:29 -> next day's open (24h01m)
        ("2026-09-10T09:31", "2026-09-14T09:30"),   # 09:31 Thu -> Mon open (Fri open is only 23h59m away)
    ]
    ok = True
    for at, exp in cases:
        w = compute(dt.datetime.fromisoformat(at).replace(tzinfo=ET), cal)
        got = w["coverage"]["end_et"]
        flag = "OK " if got == exp else "FAIL"
        ok &= got == exp
        print(f"{flag} run {at} -> coverage end {got} (expected {exp}); focus {w['focus_session']['date']} {w['focus_session']['state']}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="simulate run start, ET, e.g. 2026-09-09T11:00")
    ap.add_argument("--out", default=os.path.join(ROOT, "run", "window.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    cal = Calendar(load_cal())
    if a.selftest:
        sys.exit(0 if selftest(cal) else 1)
    run_start = (dt.datetime.fromisoformat(a.at).replace(tzinfo=ET) if a.at
                 else dt.datetime.now(dt.timezone.utc))
    w = compute(run_start, cal)
    if cal.max_known and w["hold_window"]["last"] > cal.max_known.isoformat():
        w["WARNING"] = "hold window extends past the last year in config/nyse_calendar.json — extend the calendar"
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(w, f, indent=2)
    print(summary(w))
    if "WARNING" in w:
        print("WARNING:", w["WARNING"])
    print(f"-> wrote {a.out}")


if __name__ == "__main__":
    main()
