"""저장소 위생 검사 — PR마다 GitHub Actions(validate)가 돌립니다.

1. 내 작업 폴더(workbench/ · scripts/)의 추적 파일에 키 모양 문자열이 없다
2. 통화 매핑표(workbench/day2/rules/ccy_map.csv)가 있으면 형식이 맞다 — 머리글 raw,clean · clean은 4종 + UNKNOWN
3. 정제 규칙 문서에 '9. 변경 기록' 절이 있다
"""
import csv
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / "workbench" / "day2" / "rules"
CLEAN_OK = {"USD", "EUR", "JPY", "CNY", "UNKNOWN"}
# 키 모양 — 이 파일 자신이 걸리지 않게 글자를 나눠 적었다
KEY_SHAPES = re.compile(
    "sk-" "ant-|sk-" "proj-|AK" "IA[0-9A-Z]{12,}|-----" "BEGIN [A-Z ]*PRIVATE KEY-----"
)


def test_no_key_shaped_strings():
    names = subprocess.run(
        ["git", "ls-files", "workbench", "scripts"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    hits = []
    for name in names:
        path = ROOT / name
        if path.suffix.lower() in {".png", ".jpg", ".xlsx", ".pdf"} or not path.is_file():
            continue
        if KEY_SHAPES.search(path.read_text(encoding="utf-8", errors="ignore")):
            hits.append(name)
    assert not hits, f"키 모양 문자열이 있는 파일: {hits}"


def test_ccy_map_format():
    path = RULES / "ccy_map.csv"
    if not path.exists():
        pytest.skip("rules/ccy_map.csv 없음 — 아직 만들기 전")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["raw", "clean"], f"머리글은 raw,clean 이어야 한다: {rows[0]}"
    bad = [r for r in rows[1:] if len(r) != 2 or r[1] not in CLEAN_OK]
    assert not bad, f"clean 값이 4종 + UNKNOWN 밖이거나 칸 수가 다른 줄: {bad}"


def test_ccy_map_blank_is_unknown_and_covers_raw():
    path = RULES / "ccy_map.csv"
    if not path.exists():
        pytest.skip("rules/ccy_map.csv 없음 — 아직 만들기 전")
    with path.open(encoding="utf-8", newline="") as f:
        mapping = {r["raw"]: r["clean"] for r in csv.DictReader(f)}
    assert mapping.get("") == "UNKNOWN", "빈 통화는 UNKNOWN으로 매핑해야 한다"
    raw_path = ROOT / "data" / "day1" / "d1_buyers_raw.csv"
    with raw_path.open(encoding="utf-8-sig", newline="") as f:
        used = {(r["ar_currency"] or "") for r in csv.DictReader(f)}
    assert not used - mapping.keys(), f"매핑표에 없는 표기: {used - mapping.keys()}"


def test_rules_doc_has_change_log():
    text = (RULES / "정제규칙.md").read_text(encoding="utf-8")
    assert "## 9. 변경 기록" in text
