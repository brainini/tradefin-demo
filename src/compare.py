#!/usr/bin/env python3
"""기준(main)의 지표와 이 PR의 지표를 비교해 요약표(Markdown)를 쓰고, 게이트를 못 넘으면 종료 코드 1.

    uv run python src/compare.py --base reports/metrics_main.json --new reports/metrics.json >> "$GITHUB_STEP_SUMMARY"

게이트(모두 기준 모델 대비):
  PR-AUC ≥ 기준 − 0.01 · Brier ≤ 기준 + 0.003 · 비용 ≤ 기준 × 1.10
"""
import argparse
import json
import sys
from pathlib import Path

PR_AUC_DROP = 0.01
BRIER_RISE = 0.003
COST_RATIO = 1.10


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))["metrics"]


def delta(new: float, base: float, digits: int = 4) -> str:
    d = round(new - base, digits)
    return f"{d:+.{digits}f}" if d else f"{0:.{digits}f}"      # -0.0000 대신 0.0000


def annotate(level: str, title: str, message: str) -> None:
    """GitHub Actions 워크플로 명령. 표준 오류로 내보내면 Annotations 칸에 줄이 생긴다(줄바꿈은 %0A)."""
    msg = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::{level} title={title}::{msg}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, help="기준 지표 JSON (main의 reports/metrics_main.json)")
    ap.add_argument("--new", required=True, help="이 PR로 다시 학습한 지표 JSON")
    args = ap.parse_args()
    base, new = load(args.base), load(args.new)

    limit = {
        "pr_auc": base["pr_auc"] - PR_AUC_DROP,
        "brier": base["brier"] + BRIER_RISE,
        "cost": base["cost"] * COST_RATIO,
    }
    ok = {
        "pr_auc": new["pr_auc"] >= limit["pr_auc"],
        "brier": new["brier"] <= limit["brier"],
        "cost": new["cost"] <= limit["cost"],
    }
    passed = all(ok.values())
    mark = {True: "✅ 통과", False: "❌ 실패"}

    lines = [
        f"## 품질 게이트 — {'통과 ✅' if passed else '실패 ❌'}",
        "",
        "같은 데이터·같은 시드로 다시 학습한 지표를 기준 모델(main)과 견줍니다.",
        "",
        "| 지표 | 기준(main) | 이 PR | 변화 | 게이트 |",
        "|---|---:|---:|---:|---|",
        f"| ROC-AUC | {base['roc_auc']:.4f} | {new['roc_auc']:.4f} | {delta(new['roc_auc'], base['roc_auc'])} | 참고 |",
        f"| PR-AUC | {base['pr_auc']:.4f} | {new['pr_auc']:.4f} | {delta(new['pr_auc'], base['pr_auc'])} | {mark[ok['pr_auc']]} (≥ {limit['pr_auc']:.4f}) |",
        f"| Brier | {base['brier']:.4f} | {new['brier']:.4f} | {delta(new['brier'], base['brier'])} | {mark[ok['brier']]} (≤ {limit['brier']:.4f}) |",
        f"| 비용 (5×놓침 + 오경보) | {base['cost']} | {new['cost']} | {new['cost'] - base['cost']:+d} | {mark[ok['cost']]} (≤ {limit['cost']:.1f}) |",
        "",
    ]
    reasons = []
    if not ok["pr_auc"]:
        reasons.append(f"PR-AUC {base['pr_auc']:.4f} → {new['pr_auc']:.4f}: 허용 하한 {limit['pr_auc']:.4f} 미만")
    if not ok["brier"]:
        reasons.append(f"Brier {base['brier']:.4f} → {new['brier']:.4f}: 허용 상한 {limit['brier']:.4f} 초과(확률이 부정확해짐)")
    if not ok["cost"]:
        reasons.append(f"비용 {base['cost']} → {new['cost']}: 허용 상한 {limit['cost']:.1f} 초과")
    if reasons:
        lines += ["**실패 이유**", ""] + [f"- {r}" for r in reasons] + [""]
    else:
        lines += ["세 게이트를 모두 넘었습니다. 병합해도 됩니다 — 병합 버튼은 사람이 누릅니다.", ""]
    print("\n".join(lines))

    # Actions 화면의 Annotations 칸(로그인 없이도 보인다)에 결과를 남긴다: 실패한 게이트마다 한 줄, 그리고 기준 → 이 PR 네 지표
    for r in reasons:
        annotate("error", "품질 게이트 실패", r)
    table = [
        f"ROC-AUC {base['roc_auc']:.4f} → {new['roc_auc']:.4f} (참고)",
        f"PR-AUC {base['pr_auc']:.4f} → {new['pr_auc']:.4f} ({'통과' if ok['pr_auc'] else '실패'})",
        f"Brier {base['brier']:.4f} → {new['brier']:.4f} ({'통과' if ok['brier'] else '실패'})",
        f"비용 {base['cost']} → {new['cost']} ({'통과' if ok['cost'] else '실패'})",
    ]
    annotate("notice", "기준(main) → 이 PR", "\n".join(table))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
