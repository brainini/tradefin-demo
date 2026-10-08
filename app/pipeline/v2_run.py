#!/usr/bin/env python
"""V2 카드 파이프라인(가상 데이터) — 위기 카드를 반영해 등급 · 한도 · 기대손실(EL)을 다시 계산한다.

입력
  data/input/v2_buyers.csv          가상 바이어 12곳(저장소에 있음)
  data/input/v2_demo_open_inv.csv   가상 미결 인보이스(비공개 — 저장소에 없음)
  cards/V2_card.md                  가상 위기 카드(비공개)
  local/terms_demo.md               가상 약관 발췌(비공개, 없어도 실행은 된다)
출력  out/v2/change_log.csv · grade_changes.csv · limits_diff.csv · el_table.md
실행  uv run python app/pipeline/v2_run.py

모두 교육용 가상 데이터이며, 같은 입력이면 같은 결과가 나온다(시각 · 난수 없음).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BUYERS = ROOT / "data/input/v2_buyers.csv"
OPEN_INV = ROOT / "data/input/v2_demo_open_inv.csv"
CARD = ROOT / "cards/V2_card.md"
TERMS = ROOT / "local/terms_demo.md"
OUT = ROOT / "out/v2"

LGD = 0.6                                                   # 손실률(가정)
CUT_APPROVAL = 0.30                                         # 한도 30% 이상 감액 = "승인 필요"
BOUNDS = [(0.0425, "S"), (0.0849, "A"), (0.1698, "B")]      # PD가 이 값 미만이면 해당 등급, 모두 넘으면 C
CAPS = {"S": 120_000, "A": 90_000, "B": 60_000, "C": 30_000}  # 등급별 한도 상한(USD)


def grade_of(pd_value: float) -> str:
    for bound, g in BOUNDS:
        if pd_value < bound:
            return g
    return "C"


def read_card(path: Path) -> list[tuple[str, str, str]]:
    """카드의 | 대상 | 항목 | 값 | 표 줄을 읽는다."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] == "대상" or set(cells[0]) <= set("-: "):
            continue
        rows.append((cells[0], cells[1], cells[2]))
    return rows


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in (OPEN_INV, CARD) if not p.exists()]
    if missing:
        print("필요한 비공개 입력이 없습니다: " + " · ".join(missing))
        print("README '3. 실행 방법'의 안내대로 같은 이름 · 같은 자리에 두고 다시 실행하세요.")
        return 2

    buyers = pd.read_csv(BUYERS, dtype={"buyer_id": str})
    inv = pd.read_csv(OPEN_INV, dtype={"buyer_id": str})
    changes = read_card(CARD)

    buyers["pd_after"] = buyers["pd_30d"]
    buyers["bankrupt"] = 0
    log: list[tuple] = []

    for target, item, value in changes:                      # 1) PD 배수(나라 단위)
        if item == "pd_multiplier":
            for i in buyers.index[buyers["country"] == target]:
                before = buyers.at[i, "pd_after"]
                buyers.at[i, "pd_after"] = min(1.0, before * float(value))
                log.append((buyers.at[i, "buyer_id"], "pd_30d", f"{before:.4f}", f"{buyers.at[i, 'pd_after']:.4f}", f"카드 V2: {target} PD x {value}"))
    for target, item, value in changes:                      # 2) 신용사건(바이어 단위) — PD 1.0
        if item == "bankruptcy_flag":
            for i in buyers.index[buyers["buyer_id"] == target]:
                before = buyers.at[i, "pd_after"]
                buyers.at[i, "bankrupt"] = int(value)
                buyers.at[i, "pd_after"] = 1.0 if int(value) else before
                log.append((target, "bankruptcy_flag", 0, int(value), "카드 V2: 회생 신청 공시"))

    buyers["grade_after"] = [("C" if b else grade_of(p)) for b, p in zip(buyers["bankrupt"], buyers["pd_after"])]
    buyers["limit_after_usd"] = [0 if b else min(l, CAPS[g]) for b, l, g in
                                 zip(buyers["bankrupt"], buyers["limit_before_usd"], buyers["grade_after"])]

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(log, columns=["target", "column", "before", "after", "reason"]).to_csv(
        OUT / "change_log.csv", index=False, lineterminator="\n")

    g = buyers[buyers["grade_before"] != buyers["grade_after"]]
    g[["buyer_id", "grade_before", "grade_after", "pd_30d", "pd_after"]].rename(
        columns={"pd_30d": "pd_before"}).to_csv(OUT / "grade_changes.csv", index=False,
                                                 float_format="%.4f", lineterminator="\n")

    d = buyers[buyers["limit_before_usd"] != buyers["limit_after_usd"]].copy()
    d["change_usd"] = d["limit_after_usd"] - d["limit_before_usd"]
    d["cut_pct"] = [f"{-c / b * 100:.1f}" for c, b in zip(d["change_usd"], d["limit_before_usd"])]
    d["approval"] = ["승인 필요" if float(p) >= CUT_APPROVAL * 100 else "" for p in d["cut_pct"]]
    d[["buyer_id", "limit_before_usd", "limit_after_usd", "change_usd", "cut_pct", "approval"]].to_csv(
        OUT / "limits_diff.csv", index=False, lineterminator="\n")

    open_usd = inv.groupby("buyer_id")["amount_usd"].sum()
    rows, el_b_total, el_a_total = [], 0, 0
    for _, b in buyers.iterrows():
        if b["buyer_id"] not in open_usd.index:
            continue
        ead = int(open_usd[b["buyer_id"]])
        el_b, el_a = round(b["pd_30d"] * LGD * ead), round(b["pd_after"] * LGD * ead)
        el_b_total += el_b
        el_a_total += el_a
        rows.append(f"| {b['buyer_id']} | {ead:,} | {b['pd_30d']:.4f} | {b['pd_after']:.4f} | {el_b:,} | {el_a:,} |")
    lines = ["# V2 시나리오 EL 표 (가상 데이터)", "",
             f"EL = PD × LGD({LGD}) × 미결 인보이스 합계. 보험 반영 전. 감액 30% 이상은 limits_diff.csv에 '승인 필요'.", "",
             "| 바이어 | 미결(USD) | PD 전 | PD 후 | EL 전(USD) | EL 후(USD) |", "|---|---:|---:|---:|---:|---:|", *rows,
             f"| 합계 | {int(open_usd.sum()):,} | | | {el_b_total:,} | {el_a_total:,} |"]
    if TERMS.exists():
        note = next((l for l in TERMS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")), "")
        lines += ["", f"참고(가상 약관): {note}"]
    (OUT / "el_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"검산 1: 바이어 {len(buyers)}곳 중 등급이 바뀐 곳 {len(g)} · 한도가 바뀐 곳 {len(d)} · 승인 필요 {sum(1 for a in d['approval'] if a)}")
    print(f"검산 2: 한도 합계 {int(buyers['limit_before_usd'].sum()):,} → {int(buyers['limit_after_usd'].sum()):,} USD")
    print(f"검산 3: EL 합계 {el_b_total:,} → {el_a_total:,} USD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
