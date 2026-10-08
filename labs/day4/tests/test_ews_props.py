"""조기경보 엔진(scripts/ews.py)의 속성 테스트 - 데이터가 바뀌어도 항상 맞아야 하는 성질만 검사한다.

    uv run pytest labs/day4/tests/test_ews_props.py

- 경계값: dpd 30은 선적 보류에 들고 29는 들지 않는다 / 통지 기한까지 10일은 임박, 0일도 임박, -1일은 경과
- 면제: 신용장(LC_*)은 선적 보류에서 빠진다 / 보험에 안 든 건은 통지 규칙에서 빠진다
- 멱등: 같은 기준일로 다시 돌리면 결과 파일 3종이 글자까지 같고, 중복 키(기준일 + 규칙 + 인보이스)가 없다
- 일관: 단계 건수는 다시 센 값과 같다 / 선적 보류 바이어 = D+30 바이어 + 신용사건 바이어
- 권고: 문장은 모두 '권고(사람 승인 전)' 또는 '요청' - 이미 했다고 말하지 않는다
"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / "labs/day4/alert_rules.yml"
WORK_DATA = ROOT / "workbench/day4/data"
ASOF = "2026-09-30"

spec = importlib.util.spec_from_file_location("ews", ROOT / "scripts/ews.py")
ews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ews)

INV_COLS = ["invoice_id", "buyer_id", "country_code", "payment_method", "currency", "ksure_insured", "ship_date", "due_date",
            "amount_ccy", "amount_usd", "paid", "insurance_type", "terms_change_date", "bank_change_request"]
BUYER_COLS = ["buyer_id", "ref_date", "pd_30d", "pred_late", "threshold_used", "grade", "country_code", "currency",
              "payment_method", "ksure_insured", "bankruptcy_flag"]


def due_for(dpd: int) -> str:
    return (pd.Timestamp(ASOF) - pd.Timedelta(days=dpd)).strftime("%Y-%m-%d")


def invoice(n: int, buyer: str = "B001", dpd: int = 0, method: str = "OA", insured: str = "N", usd: float = 1000.0, **kw) -> dict:
    row = dict(invoice_id=f"INV-T-{n:04d}", buyer_id=buyer, country_code="USA", payment_method=method, currency="USD",
               ksure_insured=insured, ship_date="2026-06-01", due_date=due_for(dpd), amount_ccy=usd, amount_usd=usd, paid="N",
               insurance_type="개별" if insured == "Y" else "", terms_change_date="", bank_change_request="N")
    row.update(kw)
    return row


def buyer(b: str = "B001", pd30: float = 0.01, bankrupt: int = 0, method: str = "OA", insured: str = "N") -> dict:
    return dict(buyer_id=b, ref_date=ASOF, pd_30d=pd30, pred_late=int(pd30 >= 0.1698), threshold_used=0.1698, grade="S",
                country_code="USA", currency="USD", payment_method=method, ksure_insured=insured, bankruptcy_flag=bankrupt)


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def run(tmp: Path, invoices: list[dict], buyers: list[dict], asof: str = ASOF, out: str = "out") -> dict:
    data = tmp / "data"
    data.mkdir(exist_ok=True)
    write_csv(data / "d4_open_inv.csv", invoices, INV_COLS)
    write_csv(data / "d4_start_scored.csv", buyers, BUYER_COLS)
    assert ews.main(["--asof", asof, "--rules", str(RULES), "--data", str(data), "--out", str(tmp / out)]) == 0
    return json.loads((tmp / out / "alert_summary.json").read_text(encoding="utf-8"))


def alerts_of(tmp: Path, out: str = "out") -> pd.DataFrame:
    return pd.read_csv(tmp / out / "alerts.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str)


def invoices_hit(df: pd.DataFrame, rule: str) -> set[str]:
    return set(df[df["rule_id"] == rule]["invoice_id"])


# ------------------------------------------------------------------ 경계값 · 면제
def test_d30_boundary_is_inclusive(tmp_path):
    inv = [invoice(1, dpd=29), invoice(2, dpd=30), invoice(3, dpd=31)]
    run(tmp_path, inv, [buyer()])
    assert invoices_hit(alerts_of(tmp_path), "R-D30-HOLD") == {"INV-T-0002", "INV-T-0003"}  # '>=' 그대로: 30 포함, 29 제외


def test_letters_of_credit_are_exempt_from_hold(tmp_path):
    inv = [invoice(1, dpd=40, method="LC_SIGHT"), invoice(2, dpd=40, method="LC_USANCE"), invoice(3, dpd=40, method="DA")]
    run(tmp_path, inv, [buyer(method="DA")])
    assert invoices_hit(alerts_of(tmp_path), "R-D30-HOLD") == {"INV-T-0003"}


@pytest.mark.parametrize("dpd,left,expected", [(20, 10, "SOON"), (19, 11, None), (31, 0, "SOON"), (32, -1, "OVERDUE"), (33, -2, "OVERDUE")])
def test_notice_window_edges(tmp_path, dpd, left, expected):
    """통지 기한 = 결제기일 + 1개월. 기한까지 0~10일은 '임박', 지났으면 '경과'. 보험에 든 건만."""
    run(tmp_path, [invoice(1, dpd=dpd, insured="Y"), invoice(2, dpd=dpd, insured="N")], [buyer()])
    got = alerts_of(tmp_path)
    soon, over = invoices_hit(got, "R-KSURE-NOTICE-SOON"), invoices_hit(got, "R-KSURE-NOTICE-OVERDUE")
    assert soon == ({"INV-T-0001"} if expected == "SOON" else set())
    assert over == ({"INV-T-0001"} if expected == "OVERDUE" else set())


def test_not_yet_due_never_triggers_notice(tmp_path):
    run(tmp_path, [invoice(1, dpd=0, insured="Y"), invoice(2, dpd=-5, insured="Y")], [buyer()])
    got = alerts_of(tmp_path)
    assert not invoices_hit(got, "R-KSURE-NOTICE-SOON") and not invoices_hit(got, "R-KSURE-NOTICE-OVERDUE")


def test_paid_invoices_are_ignored(tmp_path):
    run(tmp_path, [invoice(1, dpd=60, paid="Y"), invoice(2, dpd=60)], [buyer()])
    assert invoices_hit(alerts_of(tmp_path), "R-D30-HOLD") == {"INV-T-0002"}


def test_credit_event_buyer_without_open_invoice_is_still_listed(tmp_path):
    s = run(tmp_path, [invoice(1, buyer="B001", dpd=-10)], [buyer("B001"), buyer("B002", bankrupt=1)])
    assert s["ship_hold"]["buyers"] == ["B002"] and s["ship_hold"]["reasons"]["B002"] == ["R-CREDIT-EVENT"]


def test_pd_watch_uses_the_threshold_with_greater_or_equal(tmp_path):
    s = run(tmp_path, [invoice(1)], [buyer("B001", pd30=0.1698), buyer("B002", pd30=0.1697)])
    got = alerts_of(tmp_path)
    assert set(got[got["rule_id"] == "R-PD-WATCH"]["buyer_id"]) == {"B001"} and s["pd_watch_buyers"] == 1


# ------------------------------------------------------------------ 멱등
def test_same_asof_twice_gives_identical_files(tmp_path):
    inv = [invoice(1, dpd=45, insured="Y"), invoice(2, dpd=8), invoice(3, dpd=-2)]
    run(tmp_path, inv, [buyer(bankrupt=1)])
    first = {n: (tmp_path / "out" / n).read_bytes() for n in ("alerts.csv", "alert_summary.json", "alert_digest.md")}
    run(tmp_path, inv, [buyer(bankrupt=1)])
    second = {n: (tmp_path / "out" / n).read_bytes() for n in first}
    assert first == second
    assert len((tmp_path / "out" / "run_log.jsonl").read_text(encoding="utf-8").strip().splitlines()) == 2  # 기록만 한 줄 늘어난다


def test_other_asof_rows_accumulate_without_duplicates(tmp_path):
    inv = [invoice(1, dpd=45)]
    run(tmp_path, inv, [buyer()], asof="2026-09-30")
    run(tmp_path, inv, [buyer()], asof="2026-10-01")
    run(tmp_path, inv, [buyer()], asof="2026-09-30")
    got = alerts_of(tmp_path)
    assert sorted(got["asof"].unique()) == ["2026-09-30", "2026-10-01"]
    assert not got.duplicated(["asof", "rule_id", "buyer_id", "invoice_id"]).any()


# ------------------------------------------------------------------ 작업 사본 데이터로
@pytest.fixture(scope="module")
def working_copy(tmp_path_factory):
    if not (WORK_DATA / "d4_open_inv.csv").exists():
        pytest.skip("workbench/day4/data/ 에 d4_open_inv.csv 가 없습니다")
    tmp = tmp_path_factory.mktemp("work")
    assert ews.main(["--asof", ASOF, "--rules", str(RULES), "--data", str(WORK_DATA), "--out", str(tmp)]) == 0
    return dict(alerts=pd.read_csv(tmp / "alerts.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str),
                summary=json.loads((tmp / "alert_summary.json").read_text(encoding="utf-8")),
                digest=(tmp / "alert_digest.md").read_text(encoding="utf-8"))


def test_no_duplicate_keys_in_working_copy(working_copy):
    assert not working_copy["alerts"].duplicated(["asof", "rule_id", "buyer_id", "invoice_id"]).any()


def test_stage_counts_match_an_independent_count(working_copy):
    inv = pd.read_csv(WORK_DATA / "d4_open_inv.csv", encoding="utf-8-sig", keep_default_na=False)
    inv = inv[inv["paid"] == "N"]
    dpd = (pd.Timestamp(ASOF) - pd.to_datetime(inv["due_date"])).dt.days
    ranges = {"D-3": (-3, -1), "D+7": (7, 14), "D+15": (15, 29), "D+30": (30, 10**6)}
    for name, (lo, hi) in ranges.items():
        sel = (dpd >= lo) & (dpd <= hi)
        got = working_copy["summary"]["stages"][name]
        assert got["count"] == int(sel.sum())
        assert got["amount_usd"] == pytest.approx(float(inv.loc[sel, "amount_usd"].sum()), abs=0.01)


def test_ship_hold_is_d30_buyers_plus_credit_event_buyers(working_copy):
    a = working_copy["alerts"]
    expect = set(a[a["rule_id"] == "R-D30-HOLD"]["buyer_id"]) | set(a[a["rule_id"] == "R-CREDIT-EVENT"]["buyer_id"])
    assert set(working_copy["summary"]["ship_hold"]["buyers"]) == expect
    assert working_copy["summary"]["ship_hold"]["count"] == len(expect)


def test_hold_never_includes_letters_of_credit(working_copy):
    a = working_copy["alerts"]
    inv = pd.read_csv(WORK_DATA / "d4_open_inv.csv", encoding="utf-8-sig", keep_default_na=False)
    lc = set(inv[inv["payment_method"].isin(["LC_SIGHT", "LC_USANCE"])]["invoice_id"])
    assert not (set(a[a["rule_id"] == "R-D30-HOLD"]["invoice_id"]) & lc)


def test_every_sentence_is_a_recommendation(working_copy):
    digest, a = working_copy["digest"], working_copy["alerts"]
    assert "권고(사람 승인 전)" in digest
    for done in ("발송했", "차단했", "송금했", "중단했", "보류했"):  # 이미 했다는 말은 없다
        assert done not in digest
    hold_actions = set(a[a["rule_id"].isin(["R-D30-HOLD", "R-CREDIT-EVENT", "R-FRAUD-ACCOUNT"])]["action"])
    assert hold_actions and all("권고" in x for x in hold_actions)


def test_summary_counts_add_up(working_copy):
    s = working_copy["summary"]
    assert sum(v["alerts"] for v in s["rules"].values()) == len(working_copy["alerts"])
    assert sum(v["alerts"] for v in s["tiers"].values()) == len(working_copy["alerts"])
