#!/usr/bin/env python3
"""가상(합성) 조기경보 연습 데이터 만들기 — 시연 저장소 전용.

만드는 파일(workbench/day4/data/):
  d4_open_inv.csv      미결 인보이스 300건 — 과정 파일 data/checkpoints/d4_open_inv.csv 와 열 구조가 같다
  d4_start_scored.csv  바이어 150곳 — 연체 확률(pd_30d)·신용사건 표시(bankruptcy_flag) 등 경보에 쓰는 열만

모든 값은 이 스크립트가 새로 만든 가상 값이다(과정 실제 파일의 행·금액·날짜를 쓰지 않는다).
같은 시드면 같은 파일이 나온다:  uv run python labs/day4/make_demo_ledger.py

수업 당일(10/19 08:30) 실제 파일이 공개되면 `uv run python tools/get_day_files.py 4` 로 받아 이 두 파일을 덮어쓴다.
"""
from __future__ import annotations

import argparse
import calendar
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 4410
ASOF = date(2026, 9, 30)
T = 0.1698  # 연체 확률 임계값 t(3일차에서 정한 값)

COUNTRIES = ["USA", "VNM", "DEU", "JPN", "IND", "CHN", "TWN", "IDN", "MEX", "ARE", "THA", "POL", "TUR", "NLD", "GBR", "BRA", "SAU", "NGA", "EGY"]
COUNTRY_W = [8, 7, 7, 7, 6, 6, 5, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2]
CCY_OF = {"DEU": "EUR", "NLD": "EUR", "POL": "EUR", "JPN": "JPY", "CHN": "CNY"}
USD_PER = {"USD": 1.0, "EUR": 1.17, "JPY": 0.0067, "CNY": 0.141}
METHODS = ["OA", "DA", "LC_USANCE", "TT_SPLIT_30_70", "DP", "LC_SIGHT"]
METHOD_W = [64, 17, 8, 6, 3, 2]
TERMS = {"OA": (45, 90), "DA": (60, 90), "LC_USANCE": (90, 90), "TT_SPLIT_30_70": (60, 60), "DP": (7, 30), "LC_SIGHT": (7, 14)}


def add_months(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def build_buyers(rng: np.random.Generator) -> pd.DataFrame:
    ids = [f"B{i:03d}" for i in range(1, 151)]
    country = rng.choice(COUNTRIES, size=150, p=np.array(COUNTRY_W) / sum(COUNTRY_W))
    method = rng.choice(METHODS, size=150, p=np.array(METHOD_W) / sum(METHOD_W))
    insured = np.where(rng.random(150) < 0.5, "Y", "N")
    insured[np.isin(method, ["LC_SIGHT", "LC_USANCE"])] = "N"  # 신용장 거래는 은행 신용 — 단체보험 대상 아님(가상 설정)
    df = pd.DataFrame({"buyer_id": ids, "country_code": country, "payment_method": method, "ksure_insured": insured})
    df["currency"] = df["country_code"].map(CCY_OF).fillna("USD")
    return df


def build_scored(rng: np.random.Generator, buyers: pd.DataFrame, bankrupt: list[str], watch: list[str], edge: str) -> pd.DataFrame:
    n = len(buyers)
    pd30 = np.round(np.exp(rng.normal(np.log(0.0018), 0.9, size=n)), 5).clip(0.0003, 0.12)
    for b in watch:  # t 이상 — 연체 가능성이 높은 바이어(경계값 바이어 1곳 포함)
        pd30[buyers.index[buyers.buyer_id == b][0]] = round(float(rng.uniform(0.19, 0.88)), 5)
    pd30[buyers.index[buyers.buyer_id == edge][0]] = T  # 정확히 t — '≥'와 '>'가 갈리는 바이어
    grade = np.select([pd30 >= T, pd30 >= T / 2, pd30 >= T / 4], ["C", "B", "A"], "S")
    out = pd.DataFrame({
        "buyer_id": buyers["buyer_id"],
        "ref_date": ASOF.isoformat(),
        "pd_30d": pd30,
        "pred_late": (pd30 >= T).astype(int),
        "threshold_used": T,
        "grade": grade,
        "country_code": buyers["country_code"],
        "currency": buyers["currency"],
        "payment_method": buyers["payment_method"],
        "ksure_insured": buyers["ksure_insured"],
        "bankruptcy_flag": buyers["buyer_id"].isin(bankrupt).astype(int),
    })
    return out


def make_invoices(rng: np.random.Generator, buyers: pd.DataFrame, bankrupt: list[str]) -> pd.DataFrame:
    """인보이스 300건. 연체일수(dpd) 구간별 건수를 먼저 정하고 구간에 맞는 바이어를 골라 붙인다."""
    by = buyers.set_index("buyer_id")
    oa = [b for b in buyers.buyer_id if by.loc[b, "payment_method"] in ("OA", "DA", "TT_SPLIT_30_70", "DP") and b not in bankrupt]
    ins = [b for b in oa if by.loc[b, "ksure_insured"] == "Y"]
    non = [b for b in oa if by.loc[b, "ksure_insured"] == "N"]
    lc = [b for b in buyers.buyer_id if by.loc[b, "payment_method"] in ("LC_SIGHT", "LC_USANCE")]
    rows: list[tuple[str, int]] = []  # (buyer_id, dpd)

    def pick(pool: list[str], k: int, exclude: set[str] | None = None) -> list[str]:
        pool = [b for b in pool if not exclude or b not in exclude]
        return [str(b) for b in rng.choice(pool, size=k, replace=False)]

    # D+30 이상 — 선적 보류 대상 15건(바이어 12곳; 3곳은 2건씩) + 신용장 2건(규칙 제외 대상)
    hold_ins = pick(ins, 8)                 # 보험 가입 8곳: 통지 기한 경과 구간
    hold_non = pick(non, 4)                 # 보험 없음 4곳
    d30_dpd_ins = [31, 33, 38, 52, 61, 75, 120, 214]       # 통지 기한(+1개월)이 이미 지난 건: dpd ≥ 32 (31은 마지막 날 = 임박 경계)
    d30_dpd_non = [30, 44, 90, 163]                         # 30은 경계값 — '≥'면 보류, '>'면 빠진다
    rows += list(zip(hold_ins, d30_dpd_ins)) + list(zip(hold_non, d30_dpd_non))
    extra = pick(hold_ins[2:5], 3)          # 같은 바이어에 두 번째 연체 인보이스 3건
    rows += list(zip(extra, [36, 69, 98]))
    lc_two = pick(lc, 2)
    rows += list(zip(lc_two, [35, 48]))
    used_hold = set(hold_ins + hold_non)

    # D+15 구간 11건(dpd 15–29) — 그중 보험 가입 5건은 통지 임박 구간(dpd 21–31)
    d15_ins = pick(ins, 5, exclude=used_hold)
    rows += list(zip(d15_ins, [21, 24, 26, 28, 29]))
    d15_non = pick(non, 6, exclude=used_hold)
    rows += list(zip(d15_non, [15, 17, 18, 20, 22, 27]))
    # D+7 구간 8건(7–14), 그 아래 0–6일 연체 5건
    d7 = pick(oa, 8, exclude=used_hold | set(d15_ins) | set(d15_non))
    rows += list(zip(d7, [7, 8, 9, 10, 11, 12, 13, 14]))
    late = pick(oa, 5, exclude=used_hold)
    rows += list(zip(late, [1, 2, 3, 5, 6]))
    # D-3 구간 14건(결제기일 1–3일 전)
    d3 = pick(oa, 14)
    rows += list(zip(d3, [-1, -1, -1, -2, -2, -2, -2, -3, -3, -3, -1, -2, -3, -1]))
    # 신용사건 바이어 중 1곳은 아직 결제기일 전 미결이 있다(선적 보류 목록에 '신용사건'으로만 들어간다)
    cre_open = [b for b in bankrupt if by.loc[b, "payment_method"] in ("OA", "DA")][:1]
    rows += [(b, int(rng.integers(-60, -8))) for b in cre_open for _ in range(2)]
    # 나머지: 결제기일이 아직 먼 건(−89 … −4일) — 모니터링
    need = 300 - len(rows)
    rest_pool = [b for b in oa if b not in bankrupt] + lc
    rest_b = [str(b) for b in rng.choice(rest_pool, size=need, replace=True)]
    rest_dpd = [int(x) for x in rng.integers(-89, -3, size=need)]
    rows += list(zip(rest_b, rest_dpd))
    assert len(rows) == 300

    recs = []
    for b, dpd in rows:
        due = ASOF - timedelta(days=dpd)
        lo, hi = TERMS[by.loc[b, "payment_method"]]
        ship = due - timedelta(days=int(rng.integers(lo, hi + 1)))
        ccy = by.loc[b, "currency"]
        usd = float(np.clip(np.round(np.exp(rng.normal(np.log(7600), 0.9)), -1), 900, 62000))
        amount_ccy = float(np.round(usd / USD_PER[ccy], -1)) if ccy != "USD" else usd
        amount_usd = round(amount_ccy * USD_PER[ccy], 2)
        ins_y = by.loc[b, "ksure_insured"] == "Y"
        recs.append(dict(buyer_id=b, country_code=by.loc[b, "country_code"], payment_method=by.loc[b, "payment_method"], currency=ccy,
                         ksure_insured=by.loc[b, "ksure_insured"], ship_date=ship, due_date=due, amount_ccy=amount_ccy, amount_usd=amount_usd,
                         paid="N", insurance_type="개별" if ins_y else "", terms_change_date="", bank_change_request="N"))
    df = pd.DataFrame(recs).sort_values(["buyer_id", "ship_date", "due_date"], kind="stable").reset_index(drop=True)
    # 인보이스 번호: INV-YYMM(선적월)-일련번호(월별로 늘어나되 건너뛰며 증가)
    seq: dict[str, int] = {}
    ids = []
    for d in df["ship_date"]:
        key = f"{d:%y%m}"
        seq[key] = seq.get(key, 0) + int(rng.integers(1, 14))
        ids.append(f"INV-{key}-{seq[key]:04d}")
    df.insert(0, "invoice_id", ids)
    df["ship_date"] = df["ship_date"].map(lambda d: d.isoformat())
    df["due_date"] = df["due_date"].map(lambda d: d.isoformat())
    cols = ["invoice_id", "buyer_id", "country_code", "payment_method", "currency", "ksure_insured", "ship_date", "due_date",
            "amount_ccy", "amount_usd", "paid", "insurance_type", "terms_change_date", "bank_change_request"]
    return df[cols]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "workbench" / "day4" / "data"))
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    buyers = build_buyers(rng)
    bankrupt_pool = [b for b in buyers.buyer_id if buyers.set_index("buyer_id").loc[b, "payment_method"] in ("OA", "DA")]
    bankrupt = sorted(str(b) for b in rng.choice(bankrupt_pool, size=4, replace=False))
    watch_pool = [b for b in buyers.buyer_id if b not in bankrupt]
    watch = sorted(str(b) for b in rng.choice(watch_pool, size=13, replace=False))
    edge = [b for b in watch_pool if b not in watch][0]
    inv = make_invoices(rng, buyers, bankrupt)
    scored = build_scored(rng, buyers, bankrupt, watch, edge)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    inv.to_csv(out / "d4_open_inv.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    scored.to_csv(out / "d4_start_scored.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    print(f"{out}/d4_open_inv.csv {len(inv)}행 · d4_start_scored.csv {len(scored)}행 (시드 {SEED}, 기준일 {ASOF})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
