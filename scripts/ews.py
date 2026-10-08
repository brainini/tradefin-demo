#!/usr/bin/env python3
"""조기경보 엔진 - 규칙 파일(labs/day4/alert_rules.yml)대로 미결 인보이스를 점검해 경보 4종을 만든다.

    uv run python scripts/ews.py                    # 기준일 2026-09-30
    uv run python scripts/ews.py --asof 2026-10-01

입력  workbench/day4/data/d4_open_inv.csv · d4_start_scored.csv   (작업 사본)
출력  workbench/day4/outputs/alerts.csv · alert_summary.json · alert_digest.md · run_log.jsonl

- dpd = 기준일 - 결제기일 (양수 = 연체일수),  notice_days_left = (결제기일 + 1개월) - 기준일
- 경계값(>=, >)은 규칙 파일(YAML)에 적힌 그대로 쓴다. 이 코드는 아무것도 보내거나 막지 않는다 - 문장은 모두 '권고(사람 승인 전)'.
- 같은 기준일로 다시 돌려도 alerts.csv · alert_summary.json · alert_digest.md 는 글자까지 같다
  (중복 키 = 기준일 + 규칙 + 인보이스). run_log.jsonl 만 실행마다 한 줄씩 늘어난다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
KST = timezone(timedelta(hours=9))
RECO = "권고(사람 승인 전)"
ALERT_COLS = ["rule_id", "tier", "buyer_id", "invoice_id", "dpd", "amount_usd", "action", "stage", "asof"]
KEY_COLS = ["asof", "rule_id", "buyer_id", "invoice_id"]
REASON = {"R-D30-HOLD": "D+30 연체", "R-CREDIT-EVENT": "신용사건"}  # 선적 보류 목록의 사유 낱말
BUYER_COLS = ["pd_30d", "threshold_used", "grade", "bankruptcy_flag"]  # 바이어 점수 파일에서 인보이스 쪽으로 가져오는 열


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def money(x: float) -> str:
    return f"{x:,.0f}"


# --------------------------------------------------------------------------- 입력
def load_rules(path: Path) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    cfg["stage_ranges"] = {name: (lo, hi) for name, (lo, hi) in cfg["stages"].items()}
    ids = [r["id"] for r in cfg["rules"]]
    if len(ids) != len(set(ids)):
        sys.exit(f"규칙 id가 겹칩니다: {ids}")
    return cfg


def load_data(data_dir: Path, asof: pd.Timestamp, notice_months: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    inv = pd.read_csv(data_dir / "d4_open_inv.csv", encoding="utf-8-sig", keep_default_na=False)
    scored = pd.read_csv(data_dir / "d4_start_scored.csv", encoding="utf-8-sig", keep_default_na=False)
    inv = inv[inv["paid"] == "N"].copy()  # 아직 받지 못한 인보이스만 판정한다
    due = pd.to_datetime(inv["due_date"])
    inv["dpd"] = (asof - due).dt.days
    inv["notice_days_left"] = ((due + pd.DateOffset(months=notice_months)) - asof).dt.days
    extra = ["buyer_id"] + [c for c in BUYER_COLS if c in scored.columns and c not in inv.columns]
    inv = inv.merge(scored[extra], on="buyer_id", how="left")
    # 바이어 쪽 표(규칙의 scope: buyer) - 미결 건수 · 금액 · 가장 오래된 연체일수를 붙인다
    agg = inv.groupby("buyer_id").agg(open_invoices=("invoice_id", "count"), open_amount_usd=("amount_usd", "sum"),
                                      max_dpd=("dpd", "max")).reset_index()
    buyers = scored.merge(agg, on="buyer_id", how="left")
    buyers["open_invoices"] = buyers["open_invoices"].fillna(0).astype(int)
    buyers["open_amount_usd"] = buyers["open_amount_usd"].fillna(0.0)
    return inv, buyers


def stage_of(dpd: int, ranges: dict) -> str:
    for name, (lo, hi) in ranges.items():
        if dpd >= lo and (hi is None or dpd <= hi):
            return name
    return ""


# --------------------------------------------------------------------------- 점검
def evaluate(rules: dict, inv: pd.DataFrame, buyers: pd.DataFrame, asof_str: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """규칙마다 해당 인보이스(또는 바이어)를 골라 경보 표를 만든다. 열은 모두 글자로 둔다(CSV에 쓴 그대로)."""
    inv = inv.assign(stage=[stage_of(d, rules["stage_ranges"]) for d in inv["dpd"]])
    rows = []
    for r in rules["rules"]:
        if r.get("scope") == "buyer":  # 바이어 단위 규칙 - 인보이스 번호 · 연체일수는 비워 두고, 금액은 그 바이어의 미결 합계
            hit = buyers[buyers.eval(r["when"], engine="python")]
            for _, b in hit.iterrows():
                rows.append((r["id"], r["tier"], b["buyer_id"], "", "", f"{b['open_amount_usd']:.2f}", r["action"], "", asof_str))
        else:
            hit = inv[inv.eval(r["when"], engine="python")]
            for _, i in hit.iterrows():
                rows.append((r["id"], r["tier"], i["buyer_id"], i["invoice_id"], str(int(i["dpd"])), f"{i['amount_usd']:.2f}",
                             r["action"], i["stage"], asof_str))
    alerts = pd.DataFrame(rows, columns=ALERT_COLS, dtype=str)
    return alerts, inv


def summarize(rules: dict, alerts: pd.DataFrame, inv: pd.DataFrame, buyers: pd.DataFrame, asof_str: str, hashes: dict) -> dict:
    stages = {}
    for name in rules["stage_ranges"]:
        sel = inv[inv["stage"] == name]
        stages[name] = {"count": int(len(sel)), "amount_usd": round(float(sel["amount_usd"].sum()), 2)}
    per_rule = {}
    for r in rules["rules"]:
        sel = alerts[alerts["rule_id"] == r["id"]]
        per_rule[r["id"]] = {"tier": r["tier"], "scope": r.get("scope", "invoice"), "alerts": int(len(sel)),
                             "buyers": int(sel["buyer_id"].nunique())}
    tiers = {}
    for t in rules["tiers"]:
        sel = alerts[alerts["tier"] == t]
        tiers[t] = {"meaning": rules["tiers"][t], "alerts": int(len(sel)), "buyers": int(sel["buyer_id"].nunique())}
    hold_rules = rules["ship_hold_rules"]
    hold_sel = alerts[alerts["rule_id"].isin(hold_rules)]
    reasons = {b: sorted(g["rule_id"].unique().tolist()) for b, g in hold_sel.groupby("buyer_id")}
    hold_buyers = sorted(reasons)
    soon = alerts[alerts["rule_id"] == "R-KSURE-NOTICE-SOON"]
    over = alerts[alerts["rule_id"] == "R-KSURE-NOTICE-OVERDUE"]
    return {
        "asof": asof_str,
        "open_invoices": int(len(inv)),
        "open_amount_usd": round(float(inv["amount_usd"].sum()), 2),
        "buyers": int(len(buyers)),
        "stages": stages,
        "tiers": tiers,
        "rules": per_rule,
        "ship_hold": {"rules": hold_rules, "count": len(hold_buyers), "buyers": hold_buyers, "reasons": reasons},
        "notice": {"soon_invoices": int(len(soon)), "overdue_invoices": int(len(over))},
        "pd_watch_buyers": per_rule.get("R-PD-WATCH", {}).get("buyers", 0),
        "fraud_account_alerts": per_rule.get("R-FRAUD-ACCOUNT", {}).get("alerts", 0),
        "terms_change_alerts": per_rule.get("R-TERMS-CHANGE", {}).get("alerts", 0),
        "input_sha256": hashes,
    }


# --------------------------------------------------------------------------- 문서
def digest(rules: dict, s: dict, alerts: pd.DataFrame, buyers: pd.DataFrame) -> str:
    L = [f"# 조기경보 요약 - 기준일 {s['asof']}", "",
         f"미결 인보이스 {s['open_invoices']}건({money(s['open_amount_usd'])} USD) · 바이어 {s['buyers']}곳. "
         f"아래 문장은 모두 **{RECO}** 입니다. 결정과 실행은 담당자가 합니다.", "",
         "## 등급별 건수", "", "| 등급 | 뜻 | 규칙 | 경보 | 바이어 |", "|---|---|---|---:|---:|"]
    for r in sorted(rules["rules"], key=lambda r: r["tier"]):  # 같은 등급 안에서는 규칙 파일의 순서
        p = s["rules"][r["id"]]
        L.append(f"| {r['tier']} | {rules['tiers'][r['tier']]} | {r['id']} | {p['alerts']} | {p['buyers']} |")
    L += ["", "## 연체 단계 (dpd)", "", "| 단계 | 구간 | 건수 | 금액(USD) |", "|---|---|---:|---:|"]
    for name, (lo, hi) in rules["stage_ranges"].items():
        rng = f"{lo} 이상" if hi is None else f"{lo} ~ {hi}"
        L.append(f"| {name} | {rng} | {s['stages'][name]['count']} | {money(s['stages'][name]['amount_usd'])} |")
    L += ["", "## 사람이 결정할 목록", ""]
    hold = s["ship_hold"]
    L += [f"### 1. 선적 보류 {RECO} - {hold['count']}곳", "", "| 바이어 | 사유 | 미결 금액(USD) | 최장 연체(일) |", "|---|---|---:|---:|"]
    by = buyers.set_index("buyer_id")
    for b in hold["buyers"]:
        why = " · ".join(REASON.get(x, x) for x in hold["reasons"][b])
        mx = by.loc[b, "max_dpd"]
        L.append(f"| {b} | {why} | {money(by.loc[b, 'open_amount_usd'])} | {int(mx) if pd.notna(mx) and mx > 0 else '-'} |")
    for rid, title in (("R-KSURE-NOTICE-SOON", "사고발생통지 임박 (기한까지 0~10일) - 통지 여부 결정 요청"),
                       ("R-KSURE-NOTICE-OVERDUE", "사고발생통지 기한 경과 - 보험사 확인 요청")):
        sel = alerts[alerts["rule_id"] == rid]
        L += ["", f"### {'2' if rid.endswith('SOON') else '3'}. {title} - {len(sel)}건", ""]
        if len(sel):
            L += ["| 인보이스 | 바이어 | 연체(일) | 금액(USD) |", "|---|---|---:|---:|"]
            L += [f"| {a.invoice_id} | {a.buyer_id} | {a.dpd} | {money(float(a.amount_usd))} |" for a in sel.itertuples()]
        else:
            L.append("해당 없음")
    w = alerts[alerts["rule_id"] == "R-PD-WATCH"]
    L += ["", f"### 4. 모니터링 강화 {RECO} - 연체 확률 pd_30d >= t {len(w)}곳", "",
          (" · ".join(w["buyer_id"]) if len(w) else "해당 없음"), "",
          f"계좌 변경 요청 {s['fraud_account_alerts']}건 · 결제조건 변경 {s['terms_change_alerts']}건.", ""]
    return "\n".join(L)


def merge_alerts(path: Path, new: pd.DataFrame, asof_str: str) -> pd.DataFrame:
    """기존 alerts.csv 에서 같은 기준일 줄만 새 결과로 바꾼다(다른 기준일 줄은 쌓인다) -> 같은 기준일 재실행은 항상 같은 파일"""
    if path.exists():
        old = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False, dtype=str)
        old = old[old["asof"] != asof_str]
        new = pd.concat([old, new], ignore_index=True)
    return new.sort_values(["asof", "tier", "rule_id", "buyer_id", "invoice_id"], kind="stable").reset_index(drop=True)


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asof", default="2026-09-30", help="기준일 YYYY-MM-DD (기본 2026-09-30)")
    ap.add_argument("--rules", default=str(ROOT / "labs/day4/alert_rules.yml"))
    ap.add_argument("--data", default=str(ROOT / "workbench/day4/data"))
    ap.add_argument("--out", default=str(ROOT / "workbench/day4/outputs"))
    a = ap.parse_args(argv)

    started = datetime.now(KST)
    asof = pd.Timestamp(a.asof)
    asof_str = asof.strftime("%Y-%m-%d")
    rules_path, data_dir, out = Path(a.rules), Path(a.data), Path(a.out)
    rules = load_rules(rules_path)
    inv, buyers = load_data(data_dir, asof, int(rules.get("notice_months", 1)))
    alerts, inv = evaluate(rules, inv, buyers, asof_str)
    hashes = {"alert_rules.yml": sha256(rules_path), "d4_open_inv.csv": sha256(data_dir / "d4_open_inv.csv"),
              "d4_start_scored.csv": sha256(data_dir / "d4_start_scored.csv")}
    s = summarize(rules, alerts, inv, buyers, asof_str, hashes)

    out.mkdir(parents=True, exist_ok=True)
    merged = merge_alerts(out / "alerts.csv", alerts, asof_str)
    merged.to_csv(out / "alerts.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    (out / "alert_summary.json").write_text(json.dumps(s, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "alert_digest.md").write_text(digest(rules, s, alerts, buyers) + "\n", encoding="utf-8")
    log = {"run_at": started.isoformat(timespec="seconds"), "asof": asof_str, "inputs_sha256": hashes,
           "alerts_by_rule": {k: v["alerts"] for k, v in s["rules"].items()},
           "summary_sha256": hashlib.sha256((out / "alert_summary.json").read_bytes()).hexdigest()}
    with (out / "run_log.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    st = s["stages"]
    print(f"조기경보 기준일 {asof_str} - 미결 {s['open_invoices']}건 · 바이어 {s['buyers']}곳")
    print("  단계  " + " · ".join(f"{k} {v['count']}건 {money(v['amount_usd'])}" for k, v in st.items()) + " (USD)")
    print(f"  선적 보류 {RECO} {s['ship_hold']['count']}곳 · 통지 임박 {s['notice']['soon_invoices']}건 · 경과 {s['notice']['overdue_invoices']}건"
          f" · 연체 확률 높음 {s['pd_watch_buyers']}곳 · 계좌 변경 {s['fraud_account_alerts']}건 · 결제조건 변경 {s['terms_change_alerts']}건")
    print(f"  -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}/ (alerts.csv · alert_summary.json · alert_digest.md · run_log.jsonl)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
