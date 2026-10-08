#!/usr/bin/env python3
"""가상(합성) 바이어-월 패널 만들기 — 3일차 '실험 기록과 PR 자동 검증' 시연용.

    uv run python scripts/make_synthetic_panel.py            # data/panel_synthetic.csv 를 새로 쓴다

* 실데이터가 아니다. 한빛정밀(주) 과정 데이터와 무관하게, 난수로 만든 150개 가상 바이어의 월별 기록이다.
* 바이어마다 '연체 에피소드'(연체가 한동안 이어지는 상태)가 시작·지속·종료하고, 그 징후(지연 일수 · 한도 사용률 · 재무 비율)가
  특성으로 보인다. 정답 late_30d = 다음 달에 에피소드 상태인가.
* 행 수는 과정 패널과 같은 모양이다: 연습 구간(2024-01~02) 210 · 학습(2024-03~2025-12) 2,723 · 시험(2026-01~08) 1,084.
* 같은 시드면 같은 파일이 나온다(SEED). 값을 바꾸면 시연 숫자도 바뀐다.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 57
KNOBS = {'base': -7.564, 'gamma': 0.8, 'zq': 1.4, 'kappa': 3.5, 'kappa2': 3.5, 'stay_a': 0.8, 'stay_b': 1.0, 'warn_base': 0.04, 'warn_p': 0.9, 'noise': 1.2, 'n_noise_feats': 2}

N_BUYERS = 150
WARMUP_ROWS = [105, 105]                    # 2024-01, 2024-02
TRAIN_ROWS, TEST_ROWS = 2723, 1084          # 2024-03~2025-12 (22개월) · 2026-01~08 (8개월)


def month_counts() -> np.ndarray:
    """월별 행 수 — 시간이 갈수록 거래하는 바이어가 늘어난다."""
    train = np.round(np.linspace(108, 138, 22)).astype(int)
    diff, k = TRAIN_ROWS - train.sum(), 0
    while diff != 0:                         # 합계를 2,723에 맞춘다
        i = len(train) - 1 - (k % len(train))
        train[i] += 1 if diff > 0 else -1
        diff += -1 if diff > 0 else 1
        k += 1
    test = np.round(np.linspace(128, 143, 8)).astype(int)
    assert test.sum() == TEST_ROWS
    return np.array(WARMUP_ROWS + list(train) + list(test))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def make_panel(seed: int = SEED, **kn) -> pd.DataFrame:
    k = {**KNOBS, **kn}
    rng = np.random.default_rng(seed)
    months = pd.period_range("2024-01", "2026-09", freq="M")      # 2026-09는 2026-08 행의 정답을 위해서만 쓴다
    T, N = len(months), N_BUYERS
    counts = month_counts()
    jan26 = months.get_loc(pd.Period("2026-01"))

    # --- 바이어 고정 속성 -------------------------------------------------------------
    z = rng.normal(size=N)                                         # 연체 성향(바이어마다 다르고 오래 간다)
    country = rng.integers(0, 20, size=N)                          # 바이어가 속한 나라(20개국)
    risk = np.linspace(0.05, 0.9, 20)[rng.permutation(20)][country]                       # 국가 위험(0~1)
    terms = rng.choice([30, 60, 90, 120], size=N, p=[.3, .4, .2, .1])                     # 결제 조건(일)
    fin_cr = rng.normal(1.5 - 0.25 * z, 0.5)                       # 유동비율
    ar_log = rng.normal(15.0 + 0.15 * z, 0.8)                      # 미수금 규모(로그)
    pers = rng.gumbel(size=N)                                      # 거래가 꾸준한 정도
    mkt = np.zeros(T)                                              # 시장 전체의 스트레스(2026년부터 조금 올라간다)
    for t in range(1, T):
        mkt[t] = 0.85 * mkt[t - 1] + rng.normal(0, 0.2) + (0.03 if t >= jan26 else 0)

    # --- 월별 시뮬레이션 ----------------------------------------------------------------
    s = np.zeros((N, T)); e = np.zeros((N, T), int); d = np.zeros((N, T))
    names = ["country_risk", "limit_usage", "open_ar_log", "dpd_max_now", "bal_31p_flag", "dpd_trend_3m",
             "avg_delay_6m", "late_cnt_12m", "inv_cnt_12m", "amt_cv_6m", "fx_vol_30d", "fin_current_ratio"]
    F = {n: np.zeros((N, T)) for n in names}
    e[:, 0] = (rng.random(N) < 0.04).astype(int)
    for t in range(T):
        s[:, t] = (0.75 * (s[:, t - 1] if t else 0) + 0.35 * z + rng.normal(0, 0.45, N) + 0.5 * mkt[t])   # 스트레스
        in_ep = e[:, t] == 1
        d_ep = np.minimum(150, 10 + rng.exponential(32, N))                                               # 에피소드 중 지연 일수
        warn = (~in_ep) & (rng.random(N) < k["warn_base"] + k["warn_p"] * sigmoid(k["gamma"] * s[:, t] + k["zq"] * z - 2.0))
        d[:, t] = np.round(np.where(in_ep, d_ep, np.where(warn, rng.integers(1, 21, N), 0)))              # 징후: 짧은 지연
        lo3, lo5, lo11 = max(0, t - 3), max(0, t - 5), max(0, t - 11)
        prev3 = d[:, lo3:t].mean(axis=1) if t > 0 else np.zeros(N)
        F["country_risk"][:, t] = np.round(risk + rng.normal(0, 0.03, N) + 0.02 * mkt[t], 3)
        F["limit_usage"][:, t] = np.round(np.clip(0.35 + 0.22 * s[:, t] + 0.3 * e[:, t] + rng.normal(0, 0.14 * k["noise"], N), 0, 1.3), 3)
        F["open_ar_log"][:, t] = np.round(ar_log + rng.normal(0, 0.15 * k["noise"], N), 3)
        F["dpd_max_now"][:, t] = d[:, t]
        F["bal_31p_flag"][:, t] = (d[:, t] > 30).astype(int)
        F["dpd_trend_3m"][:, t] = np.round(d[:, t] - prev3, 2)
        F["avg_delay_6m"][:, t] = np.round(d[:, lo5:t + 1].mean(axis=1), 2)
        F["late_cnt_12m"][:, t] = (d[:, lo11:t + 1] > 0).sum(axis=1)
        F["inv_cnt_12m"][:, t] = rng.poisson(18 + 2 * np.clip(z, -2, 2))
        F["amt_cv_6m"][:, t] = np.round(np.abs(rng.normal(0.35 + 0.05 * s[:, t], 0.12 * k["noise"], N)), 3)
        F["fx_vol_30d"][:, t] = np.round(np.abs(rng.normal(0.10 + 0.02 * mkt[t], 0.03 * k["noise"], N)), 4)
        F["fin_current_ratio"][:, t] = np.round(fin_cr + rng.normal(0, 0.1 * k["noise"], N), 3)
        if t < T - 1:                                              # 다음 달 에피소드 상태 = 정답
            trig1 = (F["limit_usage"][:, t] > 0.7) & (F["dpd_trend_3m"][:, t] > 6.0) & (terms >= 90)
            trig2 = (fin_cr < 1.1) & (risk > 0.55) & (F["avg_delay_6m"][:, t] > 4)
            q = sigmoid(k["base"] + k["gamma"] * s[:, t] + k["zq"] * z + k["kappa"] * trig1 + k["kappa2"] * trig2)
            if t + 1 >= jan26:
                q = np.minimum(q * 1.15, 0.7)                      # 2026년: 새 연체가 조금 더 잦다
            stay = sigmoid(k["stay_a"] + k["stay_b"] * np.minimum(d[:, t], 60) / 30.0)
            u1, u2 = rng.random(N), rng.random(N)
            e[:, t + 1] = np.where(in_ep, (u1 < stay).astype(int), (u2 < q).astype(int))

    # --- 월별로 거래가 있는 바이어만 행이 된다 ---------------------------------------------
    blocks = []
    for t in range(T - 1):
        idx = np.sort(np.argsort(-(0.6 * pers + rng.gumbel(size=N)))[: counts[t]])
        blk = {n: F[n][idx, t] for n in names}
        blk["terms_days"] = terms[idx]
        blk["late_30d"] = e[idx, t + 1]
        blk["buyer_id"] = [f"B{b + 1:03d}" for b in idx]
        blk["ref_date"] = months[t].to_timestamp(how="end").strftime("%Y-%m-%d")
        blocks.append(pd.DataFrame(blk))
    df = pd.concat(blocks, ignore_index=True)
    for j in range(k["n_noise_feats"]):                            # 정답과 무관한 열(과적합을 시험한다)
        df[f"noise_{j}"] = np.round(rng.normal(size=len(df)), 3)
    dt = pd.to_datetime(df["ref_date"])
    df["split_suggested"] = np.where(dt < "2024-03-01", "warmup", np.where(dt < "2026-01-01", "train", "test"))
    for c in ("dpd_max_now", "bal_31p_flag", "late_cnt_12m", "inv_cnt_12m"):
        df[c] = df[c].astype(int)
    front = ["buyer_id", "ref_date", "split_suggested"]
    return df[front + [c for c in df.columns if c not in front + ["late_30d"]] + ["late_30d"]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/panel_synthetic.csv")
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    df = make_panel(a.seed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    by = df.groupby("split_suggested")["late_30d"].agg(["size", "sum"])
    print(f"{a.out}: {len(df):,}행 × {df.shape[1]}열\n{by.to_string()}")


if __name__ == "__main__":
    main()
