#!/usr/bin/env python3
"""연체 위험(late_30d) 예측 — 시간 분할 LightGBM 학습과 지표 계산.

    uv run python src/train.py --params params.yaml --out reports/metrics.json

- 학습 = split_suggested가 'train'인 행, 시험 = 'test'인 행(시간 순서대로 나눈 것).
- 설정은 params.yaml에서만 읽는다(코드에 숫자를 박지 않는다). random_state와 스레드 1개로 고정해
  같은 입력이면 같은 결과가 나온다(내 PC와 GitHub 서버가 같은 숫자를 낸다).
- 비용: 임계값 t = 1/6에서 5 × 놓친 연체(FN) + 1 × 잘못 울린 경보(FP).
"""
import argparse
import hashlib
import json
from pathlib import Path

import lightgbm as lgb
import pandas as pd
import yaml
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

NOT_FEATURES = ["buyer_id", "ref_date", "split_suggested", "late_30d"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--params", default="params.yaml")
    ap.add_argument("--out", default="reports/metrics.json")
    ap.add_argument("--model-out", default="models/demo_lgbm.txt")
    args = ap.parse_args()

    params = yaml.safe_load(Path(args.params).read_text(encoding="utf-8"))
    data_path = Path(params["data"]["path"])
    label, split_col = params["data"]["label"], params["data"]["split_col"]

    df = pd.read_csv(data_path)
    features = [c for c in df.columns if c not in NOT_FEATURES]
    train, test = df[df[split_col] == "train"], df[df[split_col] == "test"]

    clf = lgb.LGBMClassifier(
        objective="binary",
        random_state=params["random_state"],
        n_jobs=1,                  # 스레드 1개 — 스레드 수에 따라 숫자가 달라지는 일을 막는다
        deterministic=True,
        force_row_wise=True,
        subsample_freq=1,          # 이게 있어야 subsample이 실제로 적용된다
        verbose=-1,
        **params["model"],
    )
    clf.fit(train[features], train[label])

    p = clf.predict_proba(test[features])[:, 1]
    y = test[label].to_numpy()
    cost = params["cost"]
    flagged = p >= cost["threshold"]
    fn = int(((~flagged) & (y == 1)).sum())
    fp = int((flagged & (y == 0)).sum())

    metrics = {
        "roc_auc": roc_auc_score(y, p),
        "pr_auc": average_precision_score(y, p),
        "brier": brier_score_loss(y, p),
        "log_loss": log_loss(y, p),
        "cost": cost["fn"] * fn + cost["fp"] * fp,
        "fn": fn,
        "fp": fp,
    }
    result = {
        "metrics": {k: (round(float(v), 6) if isinstance(v, float) else int(v)) for k, v in metrics.items()},
        "sizes": {"train_rows": len(train), "test_rows": len(test), "test_late": int(y.sum())},
        "params": params["model"],
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest()[:12],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    model_out = Path(args.model_out)
    model_out.parent.mkdir(parents=True, exist_ok=True)
    clf.booster_.save_model(str(model_out))

    m = result["metrics"]
    print(f"ROC-AUC {m['roc_auc']:.4f} · PR-AUC {m['pr_auc']:.4f} · Brier {m['brier']:.4f} · 비용 {m['cost']} (놓침 {fn} · 오경보 {fp})")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
