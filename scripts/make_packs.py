#!/usr/bin/env python3
"""
make_packs.py — write the per-gatherer pack files and the orchestrator summary from run/*.json.

Packs (run/pack_<name>.md) give each subagent the resolved dates, its slice of the watchlist and the
API facts it must not re-search. run/summary.md is the compact overview the orchestrator reads.
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "run")


def load(n, required=True):
    p = os.path.join(RUN, n)
    if not os.path.exists(p):
        if required:
            raise SystemExit(f"missing {p}")
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def window_block(w):
    fs = w["focus_session"]
    sess = ", ".join(f"{s['weekday']} {s['date']} ({s['status']}{', early close 13:00' if s['early_close'] else ''})"
                     for s in w["coverage"]["sessions_in_window"]) or "none (weekend/holiday gap)"
    hold = ", ".join(f"{d['weekday']} {d['date'][5:]}" + (" CLOSED" if d["closed"] else "") + (" early-close" if d.get("early_close") else "")
                     for d in w["hold_window"]["days"])
    edge = ", ".join(f"{e['weekday']} {e['date']}" for e in w["hold_window"]["edge_days"])
    return "\n".join([
        "## Resolved dates (ground truth — do not re-derive)",
        f"- Run start: {w['run_start_et_human']} ({w['run_start_cn_human']}); ET is {w['et_label']} (UTC{int(w['et_utc_offset_hours']):+d}); GMT+8 = ET +{w['cn_minus_et_hours']}h",
        f"- COVERAGE WINDOW: now → {w['coverage']['end_human_et']} open ({w['coverage']['hours']}h). Sessions inside: {sess}",
        f"- Timeline axis day: {fs['weekday']} {fs['date']} {fs['open_et']}–{fs['close_et']} ET ({fs['state']})",
        f"- HOLD WINDOW ({w['hold_window']['sessions']} sessions): {hold}",
        f"- Just past the edge: {edge}",
    ])


def events_block(ev, tickers=None):
    if not ev:
        return "## Scheduled corporate events (API)\n- events.json missing — treat earnings/ex-div as unknown and say so"
    lines = ["## Scheduled corporate events (API — confirmed facts, do not re-search)",
             f"- Consensus basis: {ev['consensus_basis']}"]
    def keep(t):
        return tickers is None or t in tickers
    e_cov = [r for r in ev["earnings_in_coverage"] if keep(r["ticker"])]
    e_hold = [r for r in ev["earnings_in_hold_window"] if keep(r["ticker"]) and r not in e_cov]
    e_edge = [r for r in ev["earnings_just_past_edge"] if keep(r["ticker"])]
    x_hold = [r for r in ev["exdiv_in_hold_window"] if keep(r["ticker"])]
    def erow(r):
        s = f"{r['ticker']} {r['date']} {r.get('report_time', '')} — {r['confirmation']}"
        if r.get("eps_consensus_yahoo") is not None:
            s += f"; EPS cons {r['eps_consensus_yahoo']:.2f} adj. (Yahoo)"
        if r.get("rev_consensus_yahoo"):
            s += f"; rev cons {r['rev_consensus_yahoo']/1e9:.2f}B"
        return s
    lines.append("- Earnings inside COVERAGE: " + ("; ".join(erow(r) for r in e_cov) or "none"))
    lines.append("- Earnings later in HOLD WINDOW: " + ("; ".join(erow(r) for r in e_hold) or "none"))
    lines.append("- Earnings just past the edge: " + ("; ".join(erow(r) for r in e_edge) or "none"))
    lines.append("- Stock ex-div dates in hold window (amount not from API): " + ("; ".join(f"{r['ticker']} {r['ex_date']}" for r in x_hold) or "none"))
    if ev.get("date_conflicts"):
        lines.append("- DATE CONFLICTS to resolve: " + "; ".join(f"{r['ticker']} {r['date']} ({r['confirmation']})" for r in ev["date_conflicts"]))
    if tickers is None:
        nxt = []
        for t, i in ev["symbols"].items():
            if i.get("earnings_dates"):
                nxt.append(f"{t} {i['earnings_dates'][0]}{'(est)' if i.get('earnings_is_estimate') else ''}")
        lines.append("- Next earnings, all names (for blackout derivation): " + ", ".join(nxt))
    return "\n".join(lines)


def market_block(m):
    if not m:
        return "## Market conditions (API)\n- market.json missing"
    lines = ["## Market conditions snapshot (API — for context only; never re-search these levels)"]
    for x in m["metrics"]:
        if x.get("ok"):
            lines.append(f"- {x['label']}: {x['value']} · {x['delta']} ({x['as_of']})")
        else:
            lines.append(f"- {x.get('label') or x['key']}: unavailable")
    pc = m.get("promotion_candidates") or []
    lines.append("- PROMOTION CANDIDATES (state variables at a fresh 6-mo extreme or ≥2σ move — need a cause search): "
                 + ("; ".join(f"{p['label']} {p['value']} [{p.get('extreme') or ''} z1={p.get('z1')} z5={p.get('z5')}]" for p in pc) or "none"))
    return "\n".join(lines)


def price_line(t, i):
    s = f"- {t}: last {i.get('last_price')} · regular-session day change {i.get('day_change_pct')}%"
    st = (i.get("market_state") or "").upper()
    if st == "PRE" and i.get("pre_market_pct") is not None:
        s += f" · pre-market now {i['pre_market_pct']:+.2f}%"
    elif st.startswith("POST") and i.get("post_market_pct") is not None:
        s += f" · after-hours now {i['post_market_pct']:+.2f}%"
    return s


def etf_check_needed(w):
    for d in w["hold_window"]["days"]:
        dd = dt.date.fromisoformat(d["date"])
        if dd.month in (3, 6, 9, 12) and 14 <= dd.day <= 26:
            return True
    return False


def main():
    w, m, ev = load("window.json"), load("market.json", False), load("events.json", False)
    with open(os.path.join(ROOT, "config", "watchlist.json"), encoding="utf-8") as f:
        wl = json.load(f)
    os.makedirs(os.path.join(RUN, "gather"), exist_ok=True)
    os.makedirs(os.path.join(RUN, "deep_dive"), exist_ok=True)
    all_tickers = ", ".join(s["ticker"] for s in wl["symbols"])
    wb, mb = window_block(w), market_block(m)

    # macro
    with open(os.path.join(RUN, "pack_macro.md"), "w", encoding="utf-8") as f:
        f.write("# PACK: macro\n\n" + wb + "\n\n" + mb + "\n\n" + events_block(ev) + "\n\n"
                f"## Watchlist (for reach judgements)\n{all_tickers}\n\n"
                "## Your calendar-days list for the top-tier sweep\n"
                + ", ".join(d["date"] for d in w["hold_window"]["days"] if not d["closed"]) + "\n"
                + ("## Holidays / early closes inside the hold window\n" + "; ".join(f"{d['date']} {d.get('reason') or 'early close 13:00'}" for d in w["hold_window"]["days"] if d["closed"] or d.get("early_close")) + "\n" if any(d["closed"] or d.get("early_close") for d in w["hold_window"]["days"]) else ""))
    # flows
    with open(os.path.join(RUN, "pack_flows.md"), "w", encoding="utf-8") as f:
        f.write("# PACK: flows\n\n" + wb + "\n\n" + events_block(ev) + "\n\n"
                f"## Watchlist\n{all_tickers}\n\n"
                f"## etf_exdiv_check_needed: {'yes' if etf_check_needed(w) else 'no (still check USO monthly)'}\n"
                "Stock names known to pay: MSFT, GOOGL, META, AVGO, ORCL, WMT (NVDA token $0.01; INTC suspended).\n")
    # headlines
    with open(os.path.join(RUN, "pack_headlines.md"), "w", encoding="utf-8") as f:
        f.write("# PACK: headlines\n\n" + wb + "\n\n" + mb + "\n\n"
                f"## Watchlist (name the exposed tickers and the channel)\n{all_tickers}\n\n"
                "## Earnings inside coverage (context only)\n" + ("; ".join(f"{r['ticker']} {r['date']} {r.get('report_time','')}" for r in (ev or {}).get("earnings_in_coverage", [])) or "none") + "\n")
    # symbol groups
    by_t = {s["ticker"]: s for s in wl["symbols"]}
    for g, members in wl["gather_groups"].items():
        names = "\n".join(f"- {t}: search as {' / '.join(by_t[t]['search_names'])} ({by_t[t]['type']})" for t in members)
        with open(os.path.join(RUN, f"pack_{g}.md"), "w", encoding="utf-8") as f:
            f.write(f"# PACK: {g}\n\n" + wb + "\n\n" + f"## Your names\n{names}\n\n" + events_block(ev, set(members)) + "\n\n"
                    "## Price context (API, for the 'trailing parenthesis' only)\n"
                    + "\n".join(price_line(t, (ev or {}).get("symbols", {}).get(t, {})) for t in members if (ev or {}).get("symbols", {}).get(t, {}).get("last_price") is not None) + "\n")
    # orchestrator summary
    with open(os.path.join(RUN, "summary.md"), "w", encoding="utf-8") as f:
        f.write("# RUN SUMMARY (orchestrator)\n\n" + wb + "\n\n" + mb + "\n\n" + events_block(ev) + "\n\n"
                "## Gatherer packs written\n" + ", ".join(sorted(x for x in os.listdir(RUN) if x.startswith("pack_"))) + "\n"
                + (f"\nWARNING: {w['WARNING']}\n" if w.get("WARNING") else ""))
    print("packs:", ", ".join(sorted(x for x in os.listdir(RUN) if x.startswith("pack_"))))
    print("-> run/summary.md")


if __name__ == "__main__":
    main()
