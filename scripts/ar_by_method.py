"""결제방식별 매출채권 현황표 — `uv run python scripts/ar_by_method.py` 로 실행합니다.

입력: data/day1/d1_invoices.csv (읽기만 함)
출력: workbench/day1/outputs/ar_by_method.csv, workbench/day1/outputs/charts/ar_by_method.png
연체일 = 결제일(settled_date) − 만기일(due_date). 결제일이 없으면 AS_OF − 만기일.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

AS_OF = pd.Timestamp("2026-09-30")
LATE_DAYS = 60

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/day1/d1_invoices.csv"
OUT_CSV = ROOT / "workbench/day1/outputs/ar_by_method.csv"
OUT_PNG = ROOT / "workbench/day1/outputs/charts/ar_by_method.png"
FONT = ROOT / "tools/fonts/NanumGothic-Regular.ttf"

COL_METHOD = "결제방식"
COL_COUNT = "인보이스 수"
COL_TOTAL = "금액 합계(USD)"
COL_OPEN = "미결(status=open) 금액(USD)"
COL_LATE = f"{LATE_DAYS}일 초과 연체 비율"


def load() -> pd.DataFrame:
    return pd.read_csv(SRC, parse_dates=["due_date", "settled_date"])


def add_overdue_days(df: pd.DataFrame) -> pd.DataFrame:
    end = df["settled_date"].fillna(AS_OF)
    return df.assign(overdue_days=(end - df["due_date"]).dt.days)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    g = df.assign(
        open_usd=df["amount_usd"].where(df["status"] == "open", 0.0),
        late=df["overdue_days"] > LATE_DAYS,
    ).groupby("payment_method")
    out = pd.DataFrame(
        {
            COL_COUNT: g.size(),
            COL_TOTAL: g["amount_usd"].sum(),
            COL_OPEN: g["open_usd"].sum(),
            COL_LATE: g["late"].sum() / g.size(),
        }
    )
    out.index.name = COL_METHOD
    return out.sort_values(COL_TOTAL, ascending=False).reset_index()


def save_csv(tbl: pd.DataFrame) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    tbl.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")


def save_chart(tbl: pd.DataFrame) -> None:
    font_manager.fontManager.addfont(str(FONT))
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(FONT)).get_name()

    d = tbl.sort_values(COL_LATE)  # 가로 막대: 위쪽이 큰 값
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(d[COL_METHOD], d[COL_LATE] * 100, color="#3b6ea5")
    ax.bar_label(bars, labels=[f"{v:.1%}" for v in d[COL_LATE]], padding=3)
    ax.set_xlabel(f"연체일 {LATE_DAYS}일 초과 인보이스 비율 (%)")
    ax.set_title(f"결제방식별 {LATE_DAYS}일 초과 연체 비율 (기준일 {AS_OF:%Y-%m-%d})")
    ax.set_xlim(0, max(d[COL_LATE].max() * 100 * 1.15, 1))
    ax.spines[["top", "right"]].set_visible(False)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    tbl = summarize(add_overdue_days(load()))
    save_csv(tbl)
    save_chart(tbl)
    print(tbl.to_string(index=False))
    print(f"\n저장: {OUT_CSV.relative_to(ROOT)}\n저장: {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
