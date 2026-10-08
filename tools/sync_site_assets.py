#!/usr/bin/env python
"""수강생용 파일을 과정 사이트(docs/downloads/day1/ … day6/)로 복사하고, 페이지에 끼워 넣을 '파일 받기' 표를 만든다.

사용 (저장소 루트에서, 표준 라이브러리 + git만 사용):
    python tools/sync_site_assets.py                      # 복사 + 표 갱신. 빠진 파일은 경고만 하고 계속한다
    python tools/sync_site_assets.py --check              # 아무것도 바꾸지 않고 상태만 출력(필수 파일이 빠졌으면 종료코드 1)
    python tools/sync_site_assets.py --strict             # 복사하되, 필수 파일이 하나라도 빠졌으면 종료코드 1
    python tools/sync_site_assets.py --strict --require-day 2   # 2일차 시작 파일까지 필수로(그날 08:30 공개 뒤에)
    python tools/sync_site_assets.py --preview            # 강사 PC 미리 보기 전용: 아직 공개(커밋)하지 않은 파일도 복사

'필수 파일'
- 1일차 허용 목록 전부 — 예전 `--strict`·`--check`와 같다(1일차 파일은 첫 공개에 모두 들어 있다).
- `--require-day N`으로 지정한 날의 시작 파일(phase = start). 정한 시각에 여는 파일(phase = answer, 예: 15:35
  `d2_news_answer.csv`)은 필수에 넣지 않는다.
- 아직 공개하지 않은 날(2–6일차)의 파일은 없는 것이 정상이다. 표에는 '공개 예정 · 시각'으로 나오고 링크를 걸지
  않으므로 `mkdocs build --strict`가 깨지지 않는다. 파일이 공개된 뒤 이 스크립트를 다시 돌리면 링크가 생긴다.

원칙
- 일차별 허용 목록(allowlist, 아래 build_day1() … build_day6())에 있는 '수강생용' 파일만 복사한다.
  강사 정답(instructor/…, answers), data/raw/(정답 컬럼), 그날 정답본(dN_end*), 강사용 키(golden·충돌 정답),
  다른 날의 체크포인트, 시각을 정해 종이로 나누는 인젝트·변형 카드는 넣을 수 없다(섞이면 즉시 중단 — guard()).
- 공개 게이트(2일차부터): git이 추적하는 파일(= 공개 시각에 커밋·push한 파일)만 복사한다.
  강사 PC에 미리 만들어 둔 다음 날 파일·정답본·위기 카드가 로컬 빌드나 USB 오프라인판(site_offline/)에 섞이지 않게
  하는 장치다. CI(GitHub Actions)에는 커밋된 파일만 있으므로 결과가 같다. git을 쓸 수 없으면 정답 위험 경로
  (data/checkpoints/d2_~d6_, *_answer*, *_golden*)만 건너뛴다. 1일차는 예전처럼 파일이 있으면 복사한다.
- docs/downloads/dayN/ 안에서 허용 목록 밖의 파일(또는 공개 전으로 돌아간 파일)은 지운다.
- 그날 공개된 파일을 묶은 dayN_files.zip(압축 안 폴더 이름 DN/)도 만든다 — 수강생이 한 번에 받을 수 있게.

결과물
    docs/downloads/dayN/...              배포용 사본(.gitignore 대상 — 원본은 data/·labs/·rag/·agents/·templates/에 있다)
    docs/_snippets/dayN/files_*.md       dayN 페이지에 끼워 넣는 표(mkdocs.yml에서 사이트 빌드 제외)
        files_all.md (docs/dayN/*.md 용) · files_all_root.md (docs/*.md 용) · files_{구역}.md (실습 A·B, 6일차 구역별)

허용 목록에 새 파일을 넣을 때는 '수강생에게 그대로 나가도 되는 파일인가'를 먼저 확인한다(정답·실명·키·회사 자료 없음).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
DL_ROOT = DOCS / "downloads"
SNIP_ROOT = DOCS / "_snippets"

# 경로에 이 조각이 들어 있으면 수강생용이 아니다 — 허용 목록 실수 방지용 안전장치
FORBIDDEN_PARTS = (
    "instructor/",
    "answers",
    "data/raw/",
    "expected",
    "_clean",
    "dirt_log",
    "dirty_log",
    "code_table",
    "golden",                  # 강사 채점본(d2_news_scored_golden 등)
    "conflicts_answer_key",    # RAG 규정 충돌 정답(강사용)
    "ksure_terms_articles",    # 약관 조문 정리본 — 수업 안에서만 쓰고 재배포하지 않는다
    "scorecard",               # 6일차 심사표 원본(비공개)
    "feedback_template",       # 1:1 서면 피드백 양식(강사가 쓴다)
    "labs/day6/injects/",      # 인젝트 카드 — 정한 시각에 종이로 나눈다
    "labs/day6/variants/",     # 변형·예비 카드 — 강사 시연·해당 팀용
)
# 여러 날이 같이 쓰는 체크포인트(이름이 dN_으로 시작하지 않는 것)
SHARED_CHECKPOINTS = {"fx_krw_daily.csv", "scenarios.csv"}
# git을 쓸 수 없을 때 건너뛸 '정답 위험' 경로(.gitignore 2절과 같은 뜻)
SENSITIVE = re.compile(r"^data/checkpoints/d[2-6]_|_answer|_golden")
# CI(GitHub Actions)에는 커밋된(= 공개된) 파일만 있다 — 거기서 git을 못 쓰면 '있으면 공개'로 본다
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"


@dataclass
class Item:
    src: str  # 저장소 루트 기준 원본 경로
    dest: str  # docs/downloads/dayN/ 기준 경로
    title: str  # 표에 쓰는 짧은 이름
    desc: str  # 무엇인가(한 줄)
    labs: tuple[str, ...]  # 쓰는 곳(구역 키) — 1–5일차: lab-a / lab-b (+ 1일차 data), 6일차: hack / cards / kit
    track: str  # 🟢 / 🔵 / 🟣 / 확장
    phase: str = "start"  # start = 그날 시작 파일과 함께 공개 / answer = 정한 시각에 공개(필수 아님)
    when: str = ""  # 공개 예정 시각(비우면 그날 기본 공개 시각)
    alts: tuple[str, ...] = ()  # 이름이 아직 정해지지 않은 파일의 다른 후보 경로 — 먼저 있는 것을 쓴다
    exists: bool = field(default=False, init=False)  # 원본이 있다
    held: bool = field(default=False, init=False)  # 원본은 있지만 아직 공개 전(커밋 안 됨)
    size: int = field(default=0, init=False)

    @property
    def ready(self) -> bool:
        return self.exists and not self.held


@dataclass
class Day:
    n: int
    date: str  # 표시용 날짜 "10/15(목)"
    release: str  # 기본 공개 시각(시작 파일)
    zip_date: tuple[int, int, int, int, int, int]  # zip 안 파일 날짜(같은 내용이면 같은 zip)
    labels: dict[str, str]  # 구역 키 → '쓰는 곳' 칸에 쓰는 이름
    sections: tuple[str, ...]  # files_{키}.md 표를 따로 만드는 구역
    items: list[Item]

    @property
    def dest_dir(self) -> Path:
        return DL_ROOT / f"day{self.n}"

    @property
    def snip_dir(self) -> Path:
        return SNIP_ROOT / f"day{self.n}"

    @property
    def zip_name(self) -> str:
        return f"day{self.n}_files.zip"

    @property
    def zip_root(self) -> str:
        return f"D{self.n}"

    def when(self, it: Item) -> str:
        return it.when or self.release


# ---------------------------------------------------------------- 1일차 (v3: 실습 A = 블록 A Step 1–4 · 실습 B = 블록 B Step 5–8)
# 구역 키는 2–5일차와 같은 lab-a / lab-b(DAY1_SPEC_v3 부록 B). 옛 Lab1–3 구역 표(files_lab1–3.md)는 다음 실행 때 지워진다.
# 보고서 폴더(data/day1/reports/*.md)는 폴더째 허용한다. 알려진 파일은 아래 설명을 쓰고,
# 새로 생긴 .md는 기본 설명으로 표에 들어간다.
REPORT_INFO = {
    "halden_fictional_annual_report.md": (
        "Halden(가상) 연차보고서 발췌",
        "가상 영국 유통 바이어의 연차보고서(FY2026). Step 2–3에서 AI에 올린다",
        ("lab-a",),
        "🟢",
    ),
    "irobot.md": (
        "iRobot 10-K FY2024 발췌",
        "실제 SEC 공시 발췌(영어 원문 그대로). Step 3 ④에서 같은 계산을 반복한다",
        ("lab-a",),
        "🟢",
    ),
    "plug_power.md": (
        "Plug Power 공시 3건 발췌",
        "PART A 10-Q 2023년 3분기 · PART B 10-K FY2023 · PART C 10-K FY2024. Step 2 Standard",
        ("lab-a",),
        "🔵",
    ),
    "wolfspeed.md": (
        "Wolfspeed 10-Q 발췌",
        "2025-03-30 분기 보고서 발췌. 다 했으면(확장)",
        ("lab-a",),
        "확장",
    ),
    "big_lots.md": (
        "Big Lots 10-Q 발췌",
        "2024-05-04 분기 보고서 발췌. 다 했으면(확장)",
        ("lab-a",),
        "확장",
    ),
    "gorman_note.md": (
        "D&B 샘플(Gorman) 안내",
        "D&B 샘플 신용보고서 링크와 읽기 안내만 있다(PDF는 링크에서 직접 받는다). 확장",
        ("lab-a",),
        "확장",
    ),
    "README.md": (
        "보고서 폴더 안내",
        "파일 목록·인용 찾는 요령·단위 주의·이용 조건",
        ("lab-a",),
        "🟢",
    ),
}
REPORT_ORDER = [
    "halden_fictional_annual_report.md",
    "irobot.md",
    "plug_power.md",
    "wolfspeed.md",
    "big_lots.md",
    "gorman_note.md",
    "README.md",
]


def build_day1() -> list[Item]:
    items = [
        Item("labs/day1/d1_end_eda_template.xlsx", "d1_end_eda_template.xlsx", "실습 템플릿",
             "시트 00_코드표 ~ 07_내AX프로젝트. 오늘 결과를 모두 여기에 모아 제출한다(05_변수정의서 포함)",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/day1/d1_encoding_test.csv", "d1_encoding_test.csv", "깨진 CSV 연습 파일",
             "한글 열 이름·바이어명이 든 8행 가상 표. UTF-8(BOM 없음)이라 더블클릭하면 한글이 깨진다 → Step 1 ④에서 UTF-8로 다시 연다",
             ("lab-a",), "🟢"),
        Item("data/day1/d1_encoding_test_utf8bom.csv", "d1_encoding_test_utf8bom.csv", "깨진 CSV 연습 파일(비교용)",
             "같은 내용을 UTF-8(BOM 포함)로 저장한 짝 파일. 더블클릭해도 바로 열린다 — 정상 화면과 비교할 때만 쓴다",
             ("lab-a",), "🟢"),
    ]
    report_dir = REPO / "data" / "day1" / "reports"
    names = list(REPORT_ORDER)
    if report_dir.is_dir():
        names += sorted(p.name for p in report_dir.glob("*.md") if p.name not in REPORT_INFO)
    for name in names:
        title, desc, labs, track = REPORT_INFO.get(
            name, (name, "Day1 보고서 발췌(추가 자료)", ("lab-a",), "확장")
        )
        items.append(Item(f"data/day1/reports/{name}", f"reports/{name}", title, desc, labs, track))
    items += [
        Item("data/day1/real_buyers_ratios.csv", "real_buyers_ratios.csv", "SEC 추출 비율표(CSV)",
             "SEC companyfacts API에서 뽑은 4개사 원값과 4대 비율(9행). Step 3 ④에서 AI 숫자를 대조한다",
             ("lab-a",), "🟢"),
        Item("data/day1/real_buyers_ratios.xlsx", "real_buyers_ratios.xlsx", "SEC 추출 비율표(엑셀)",
             "같은 내용 + 열 설명(dictionary)·출처(source) 시트", ("lab-a",), "🟢"),
        Item("data/day1/d1_buyers_raw.xlsx", "d1_buyers_raw.xlsx", "바이어 스냅샷(엑셀)",
             "(가상) 한빛정밀 해외 바이어 현황 153행 · 시트 buyers · 기준일 2026-09-30 · 원천 입력 오류 포함. Step 4(AI 진단) → Step 5(피벗)",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/day1/d1_buyers_raw.csv", "d1_buyers_raw.csv", "바이어 스냅샷(CSV)",
             "같은 내용 CSV(UTF-8 BOM). 엑셀 파일이 안 올라가는 AI 도구와 Colab(Challenge B-8)에서 쓴다",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/data_dictionary.xlsx", "data_dictionary.xlsx", "데이터 사전",
             "컬럼 뜻·단위(columns), 코드표(codes), 결제조건 표기 → 코드(payment_terms_map)",
             ("lab-a", "data"), "🟢"),
        Item("labs/day1/ax_canvas_template.md", "ax_canvas_template.md", "AX 캔버스 양식",
             "AX 캔버스 7칸 + 과업 선정 3기준(Step 8 · 8교시). 메모장·워드에 붙여 써도 된다",
             ("lab-b",), "🟢"),
        Item("labs/day1/d1_challenge.ipynb", "d1_challenge.ipynb", "Challenge 노트북",
             "Colab용. A: SEC API로 비율 계산(Step 2–3) · B: 인보이스 원장 분석(DPD·코호트·롤레이트·DSO, Step 4–6)",
             ("lab-a", "lab-b"), "🟣"),
        Item("data/day1/d1_invoices.xlsx", "d1_invoices.xlsx", "인보이스 원장(엑셀)",
             "인보이스 5,033건(36개월) · 시트 invoices. Challenge B", ("lab-a", "lab-b"), "🟣"),
        Item("data/day1/d1_invoices.csv", "d1_invoices.csv", "인보이스 원장(CSV)",
             "같은 내용 CSV(UTF-8 BOM). Colab에 올릴 때 쓴다", ("lab-a", "lab-b"), "🟣"),
    ]
    return items


# ---------------------------------------------------------------- 2–6일차 (20_강의계획안_v3 §3.2–3.5 '파일', §4.13)
def build_day2() -> list[Item]:
    return [
        Item("data/checkpoints/d2_start.xlsx", "d2_start.xlsx", "2일차 시작 파일",
             "1일차 강사 정답본에서 이어지는 파일. 시트 buyers · buyer_features_raw · fx_at_ref · invoices_raw(🟣) · "
             "dirty_list · map_ccy · map_country · dictionary",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/checkpoints/fx_krw_daily.csv", "fx_krw_daily.csv", "원화 환율(일별)",
             "최근 영업일 원화 환율. 기준일 이전 영업일(as-of) 환율로 USD 환산할 때 쓴다(엔화는 100엔 단위 → ÷100)",
             ("lab-a",), "🟢"),
        Item("labs/day2/rules_template.md", "rules_template.md", "정제 규칙 양식",
             "정제규칙.md 틀 — 0 메타 · 1–8 규칙마다 '규칙 / 왜' 두 줄 · 9 변경 기록. 사이트 Step 2의 복사 상자와 같다. 메모장에 붙여 정제규칙.md로 저장한다",
             ("lab-a",), "🟢"),
        Item("data/checkpoints/d2_news.csv", "d2_news.csv", "바이어 뉴스",
             "바이어별 짧은 뉴스 문장(합성 300행). 블록 B 위험지수(0–10) 점수화 입력",
             ("lab-b",), "🟢"),
        Item("labs/day2/news_warmup_10.txt", "news_warmup_10.txt", "워밍업 뉴스 10건",
             "Step 6 워밍업용 텍스트(한국어 4 · 영어 6, 점수 없음). P2-2 맨 아래에 그대로 붙여 넣는다(탭 구분)",
             ("lab-b",), "🟢"),
        Item("data/checkpoints/d2_news_answer.csv", "d2_news_answer.csv", "뉴스 점수 골든셋",
             "Step 7 일치도(MAE · ±2 이내 비율) 계산용 기준 점수. 정한 시각에 공개한다",
             ("lab-b",), "🟢", phase="answer", when="10/15(목) 15:35"),
        Item("labs/day2/d2_orange_preprocess.ows", "d2_orange_preprocess.ows", "Orange 전처리 워크플로",
             "막혔을 때 비교용 완성본: File(d2_step1.xlsx · features) → Column Statistics · Impute(재무비율 4종 = 내 중앙값, "
             "1-NN 비교) · Continuize · Preprocess(보기만) · Save Data · (선택) 뉴스 Group by · Merge. Orange 3.40 File → Open",
             ("lab-a", "lab-b"), "🟢"),
        Item("labs/day2/byod_anonymize_template.xlsx", "byod_anonymize_template.xlsx", "BYOD 익명화 템플릿",
             "자사 엑셀을 쓰기 전 점검표(규칙 7 + 마지막 확인 4) · 가상 예시 변환 수식. 원본은 내 PC에서만, 익명화본도 "
             "저장소에는 올리지 않는다(AI에는 익명화본만 · 학습 설정 끔)",
             ("lab-a",), "🔵", alts=("templates/byod_anonymize_template.xlsx",)),
        Item("labs/day2/d2_challenge.ipynb", "d2_challenge.ipynb", "Challenge 노트북",
             "Colab: 통화·금액 · 기준일 환율(merge_asof) · 결측 대체(중앙값 vs KNN) · 파이프라인 안 스케일링 · 특성 공학 · "
             "LLM 없는 사전 기준선 뉴스 점수와 골든셋 일치도",
             ("lab-a", "lab-b"), "🟣"),
    ]


def build_day3() -> list[Item]:
    return [
        Item("data/checkpoints/d3_start_features.csv", "d3_start_features.csv", "학습용 특성(300행)",
             "150개사 × 기준일 2개, 레이블 late_30d(정상 0 / 연체 1). Orange File 위젯: buyer_id = meta, late_30d = target",
             ("lab-a",), "🟢"),
        Item("data/checkpoints/d3_start_scoring.csv", "d3_start_scoring.csv", "예측 대상(150행)",
             "같은 특성, 기준일 2026-09-30, 레이블 없음. Predictions 위젯 입력 → 바이어별 연체 확률",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/checkpoints/d3_features_panel.csv", "d3_features_panel.csv", "바이어 × 월 패널",
             "같은 특성의 월별 패널(4,017행, 2024-01~2026-08). 🔵 시간 분할 비교 · 🟣 SMOTE 실습",
             ("lab-a",), "🔵"),
        Item("labs/day3/d3_orange_model.ows", "d3_orange_model.ows", "Orange 모델 워크플로",
             "완성 워크플로: 70/30 층화 분할 · 학습셋 복제 오버샘플 · Gradient Boosting(xgboost) · Test and Score · Confusion Matrix · "
             "ROC(FP 1 : FN 5) · Calibration Plot · Predictions · Save Data · Explain Model/Prediction. CSV와 같은 D3 폴더에서 File → Open",
             ("lab-a", "lab-b"), "🟢"),
        Item("labs/day3/d3_grade_banding.xlsx", "d3_grade_banding.xlsx", "등급 매칭 시트",
             "pred 시트에 buyer_id · 확률을 붙이고 이름 t(빈칸)에 내 임계값 → IFS 등급 · 경계 · 분포 · 단조성(시험셋) · 6열 CSV 시트",
             ("lab-b",), "🟢"),
        Item("labs/day3/d3_shap_report_template.docx", "d3_shap_report_template.docx", "SHAP 해석서 양식",
             "P3-1 출력 5칸(결론 · 위험↑ 3 · 위험↓ 2 · 확인할 것 3 · 한계 3) + 캡처 2칸 — A4 1장",
             ("lab-b",), "🟢", alts=("labs/day3/d3_shap_report_template.md",)),
        Item("labs/day3/fx_forecast_inputs.csv", "fx_forecast_inputs.csv", "환율 예측 입력",
             "원/달러 일별 종가(FRED DEXKOUS, 2023-09~2026-09)와 학습(train)·확인(valid) 구간 표시. Step 8 환율 위험 구간",
             ("lab-b",), "🟢"),
        Item("data/external/uci_taiwan_bankruptcy.csv", "uci_taiwan_bankruptcy.csv", "UCI 대만 기업 부도 데이터",
             "외부 공개 벤치마크(CC BY 4.0, 출처 표기). 🔵 부도가 드문 데이터에서 지표 비교",
             ("lab-a",), "🔵"),
        Item("data/external/fred_dexkous.csv", "fred_dexkous.csv", "FRED 원/달러 원본",
             "미국 연준 FRED DEXKOUS 원본 시계열(퍼블릭 도메인, 출처 표기 요청). 🟣 Prophet 입력",
             ("lab-b",), "🟣"),
        # D6(DECISIONS_v3): Challenge 노트북은 labs/day3/d3_challenge.ipynb 하나(LightGBM · SMOTE · SHAP + Prophet 섹션).
        Item("labs/day3/d3_challenge.ipynb", "d3_challenge.ipynb", "Challenge 노트북",
             "Colab: LightGBM · SMOTE(학습셋만) · SHAP + Prophet 환율 예측 구간. '런타임 다시 시작 후 모두 실행'으로 재현을 확인한다",
             ("lab-a", "lab-b"), "🟣"),
    ]


def build_day4() -> list[Item]:
    # D13(DECISIONS_v3): 디스크의 실제 파일명이 정본 — d4_challenge.ipynb · d4_params.csv(P1–P40) · d4_scenarios.csv · d4_open_inv.csv ·
    # 빈 틀 labs/day4/d4_limit_model.xlsx + 채운 판 data/checkpoints/d4_limit_model.xlsx. 옛 후보 이름(alts)은 쓰지 않는다.
    # d4_risk_report_template.docx/.md · fraud_signals.md는 2026-10-07 제작(tools/build_day4_templates.py, DAY4_SPEC §4 입력).
    return [
        Item("data/checkpoints/d4_start_scored.csv", "d4_start_scored.csv", "4일차 시작 파일(150행)",
             "3일차 점수(연체 확률·등급·상위 사유)에 한도 계산 열을 더한 파일. 워크북 02_Buyers 시트에 붙여 넣는다",
             ("lab-a", "lab-b"), "🟢"),
        Item("labs/day4/d4_limit_model.xlsx", "d4_limit_model.xlsx", "한도 산정 워크북(빈 틀)",
             "시트 00–16: 할인율·NPV · 한도 LP(해 찾기) · 시나리오·몬테카를로 · 충당금 · 조기 경보 · 리포트 입력. "
             "02_Buyers는 빈 틀 — d4_start_scored.csv를 붙여 넣는다. 색 규칙: 파랑 공시값 · 노랑 가정 · 회색 수식",
             ("lab-a", "lab-b"), "🟢"),
        Item("data/checkpoints/d4_params.csv", "d4_params.csv", "파라미터 표",
             "금리·요율·정책 파라미터 P1–P40(65행, 값은 소수: 0.04 = 4%) — 워크북 01_Params와 같은 값 · 상태(확인/계산/가정) · 출처",
             ("lab-a",), "🟢"),
        Item("data/checkpoints/d4_scenarios.csv", "d4_scenarios.csv", "거시 쇼크 시나리오 S0–S4",
             "기준 S0 + 경미·중간·심각·극단 S1–S4 + 2026년 실제 원/달러 경로(참고 행). 11_Scenario 입력, PD 배수는 [교육용 가정]",
             ("lab-a",), "🟢"),
        Item("data/checkpoints/d4_open_inv.csv", "d4_open_inv.csv", "미결 인보이스(조기 경보용)",
             "기준일 미결 인보이스(선수금 제외, 300행). 13_EarlyWarning 입력과 같은 열",
             ("lab-b",), "🟢"),
        Item("data/checkpoints/d4_limit_model.xlsx", "catchup/d4_limit_model.xlsx", "워크북 합류용(채운 판)",
             "02_Buyers 등을 미리 채운 같은 워크북 — 붙여넣기가 막혔을 때만 쓴다(받은 뒤 이름이 같으니 폴더를 나눠 둔다)",
             ("lab-a",), "🟢"),
        Item("labs/day4/d4_risk_report_template.docx", "d4_risk_report_template.docx", "신용 리스크 리포트 양식",
             "경영진 보고용 요약 리포트 틀. 숫자는 워크북에서, 해석은 P4-1 초안을 사람이 고친다",
             ("lab-b",), "🟢"),
        Item("labs/day4/d4_risk_report_template.md", "d4_risk_report_template.md", "신용 리스크 리포트 양식(텍스트판)",
             "워드 양식과 같은 내용의 마크다운판 — 워드가 없거나 구글 문서에 붙여 쓸 때. 설계도 6칸 · 본문 소제목 8개 · 레드팀 지적 · 12항목",
             ("lab-b",), "🟢"),
        Item("labs/day4/fraud_signals.md", "fraud_signals.md", "사기 신호 목록",
             "조기 경보의 사기 경보에 쓰는 무역 사기 신호 정리",
             ("lab-b",), "🟢"),
        Item("labs/day4/d4_challenge.ipynb", "d4_challenge.ipynb", "Challenge 노트북",
             "Colab: PuLP · linprog로 한도 LP 교차검증, 제약 바꿔 보기, 몬테카를로",
             ("lab-a",), "🟣"),
    ]


def build_day5() -> list[Item]:
    # D13: 디스크의 실제 경로·이름이 정본 — rag/corpus/*(README · hanbit_credit_policy.md) · rag/goldset_20.csv · rag/eval_sheet_template.xlsx ·
    # agents/dify|n8n/* · d5_start.csv(29열 = 03P1 §4.9의 27열 + 미결 잔액 2열) · d5_rag_eval.ipynb.
    # 받는 폴더도 디스크와 같은 구조(rag/corpus · rag/ · agents/dify · agents/n8n)로 둔다 — rag/corpus/README.md의 상대 링크(../goldset_20.csv)가 그대로 열린다.
    # 도입 기획서 양식은 6일차 제작분(labs/day6/ax_proposal_template.md)을 5일차 저녁 초안에도 쓴다(옛 이름 templates/proposal_template.docx는 쓰지 않는다).
    return [
        Item("data/checkpoints/d5_start.csv", "d5_start.csv", "5일차 시작 파일(미결 인보이스)",
             "2026-09-30 기준 미결 인보이스(300행 이하) · 29열(등급·한도·독촉 단계·통지 기한·미결 잔액 포함). 대시보드 업로드 · n8n 원장 공용(메일 주소는 가상)",
             ("lab-b",), "🟢"),
        Item("rag/corpus/README.md", "rag/corpus/README.md", "RAG 문서 안내·공식 링크",
             "무엇을 어디서 받나: K-SURE 약관·법령은 공식 사이트 링크에서 각자 받는다(재배포 금지) + 조항 단위로 자르는 법",
             ("lab-a",), "🟢"),
        Item("rag/corpus/hanbit_credit_policy.md", "rag/corpus/hanbit_credit_policy.md", "(가상) 한빛정밀 여신관리규정",
             "가상 사내 규정(12장 35조 + 별표 4개, 조·항 구조의 텍스트판). Gemini Notebook · Dify 지식베이스에 올린다",
             ("lab-a",), "🟢"),
        Item("rag/goldset_20.csv", "rag/goldset_20.csv", "골든셋 20문항",
             "질문 · 기대 답 · 근거 조항 · 유형(기권 문항 포함). 짝과 10문항씩 나눠 기록한다",
             ("lab-a",), "🟢"),
        Item("rag/eval_sheet_template.xlsx", "rag/eval_sheet_template.xlsx", "검색 평가 시트",
             "골든셋으로 검색 품질(P@K·R@K·F1@K, K = 1·3·5 → Top-K 선택 · 보조 Hit@3·MRR)과 답 품질(정답·인용·기권)을 기록·계산한다. Google Sheets로 가져가 쓴다",
             ("lab-a",), "🟢"),
        Item("agents/dify/hanbit_policy_rag_v1.yml", "agents/dify/hanbit_policy_rag_v1.yml", "Dify 앱 DSL",
             "막혔을 때 가져오기(Import DSL)로 같은 규정 챗봇을 바로 만든다",
             ("lab-a",), "🟢"),
        Item("app/sample_data/upload_sample.csv", "upload_sample.csv", "대시보드 업로드 연습 파일",
             "앱 업로드 → 자동 전처리 화면을 시험해 보는 작은 샘플(입력 오류 포함, 100행 + 중복 1행, 가상 데이터)",
             ("lab-b",), "🟢"),
        Item("labs/day5/TF_AR_Ledger_template.xlsx", "TF_AR_Ledger_template.xlsx", "독촉 원장 양식",
             "n8n 워크플로·앱이 읽는 미결 인보이스 원장(시트 AR_Ledger 34열 = d5_start 29열 + 작업 5열 · Config · Audit_Log). Google Sheets로 가져가 쓴다",
             ("lab-b",), "🔵"),
        Item("agents/n8n/dunning_workflow_v1.json", "agents/n8n/dunning_workflow_v1.json", "n8n 독촉 워크플로",
             "가져오기용. 승인 메일(승인자 = 본인) → Gmail 초안 → Audit_Log. 실제 발송 없음(DRY RUN)",
             ("lab-b",), "🔵"),
        Item("labs/day6/ax_proposal_template.md", "ax_proposal_template.md", "AI 도입 기획서 양식(11장)",
             "오늘 21:00까지 1–6장 초안 plan_draft__T{조}-{번호}.docx(비공개 폼) → 6일차에 7–11장. Word·Google Docs로 옮겨 .docx로 낸다",
             ("lab-b",), "🟢"),
        Item("labs/day5/d5_rag_eval.ipynb", "d5_rag_eval.ipynb", "Challenge 노트북",
             "Colab: 골든셋으로 P@K·R@K·F1@K·Hit@3·MRR을 코드로 평가(조 단위 vs 고정 길이 청킹, TF-IDF vs BM25)",
             ("lab-a",), "🟣"),
    ]


def _card_src(i: int, stage: str = "") -> str:
    """위기 카드 원본의 저장소 상대 경로 — labs/day6/crisis_cards/card{i}_*.md(2단계: card{i}_{stage}*.md). 없으면 중립 이름."""
    folder = REPO / "labs" / "day6" / "crisis_cards"
    pat = f"card{i}_{stage}*.md" if stage else f"card{i}_*.md"
    hits = sorted(q for q in folder.glob(pat) if stage or "stage" not in q.name)
    rel = hits[0].relative_to(REPO).as_posix() if hits else f"labs/day6/crisis_cards/card{i}{('_' + stage) if stage else ''}.md"
    return rel


def build_day6() -> list[Item]:
    # D13·D4: 디스크의 실제 이름이 정본 — tools/build_day6_pack.py·build_day6_templates.py가 만드는 labs/day6/*(judging_rubric · roi_kpi_template · crisis_cards)와
    # data/checkpoints/d6_*(팩 · 시트별 CSV · d6_teams/ · 2단계). 그 밖의 양식(규칙 · 역할 카드 · SOP · 기획서 …)은 6일차 팩의 templates 시트(T01–T12)가 정한 이름이고,
    # v3 §4.13의 옛 이름(templates/*.docx · demo_script_template.md)은 쓰지 않는다. 파일이 디스크에 없으면 '공개 예정'으로 나온다.
    # 공개 시각: 규칙·양식은 전날 18:00(DAY6_SPEC §4), 위기 카드·데이터 팩은 09:28(d6-start, D4), 카드 ⑤ 2단계는 11:15.
    # 위기 카드는 받는 이름을 card1.md처럼 바꿔 표에 주제가 미리 드러나지 않게 한다. 인젝트(i1·i2)·변형 카드(variants/)는 여기 넣지 않는다(guard — 정한 시각에 따로 push).
    eve = "10/20(화) 18:00"
    # D19: 카드 원본 파일 이름에는 주제가 들어 있으므로 이 공개 코드에는 적지 않고 glob으로 찾는다(없으면 중립 이름 → '공개 예정').
    cards = [
        Item(_card_src(i), f"cards/card{i}.md", f"위기 카드 {mark}",
             "주카드 원문(종이 카드와 같다). 강사가 배정한 카드를 09:28에 연다",
             ("cards",), "🟢")
        for i, mark in enumerate(["①", "②", "③", "④", "⑤"], start=1)
    ]
    teams = [
        Item(f"data/checkpoints/d6_teams/team_{t:02d}.xlsx", f"teams/team_{t:02d}.xlsx", f"팀 {t} 데이터 팩",
             f"팀 {t}의 데이터 팩 — 배정 카드의 변경분 · 대상 바이어 지금 값 · 미결 인보이스 · 기한 행 · 질문 5개. 카드 배정(08:30) 뒤 우리 팀 번호의 파일만 받는다",
             ("cards",), "🟢")
        for t in range(1, 6)
    ]
    pack_csv = {  # 시트별 CSV(UTF-8 BOM) — d6_crisis_pack.xlsx의 같은 이름 시트
        "cards": "카드 5종 + 변형 V1 요약(대상 바이어 · 시나리오 · 바뀌는 값 · 기대 산출 · 최소 완료 기준)",
        "injects": "공통 인젝트 2장의 시각과 쓰는 파일(내용은 투입 시각에 카드로 공개)",
        "buyer_changes": "바이어 단위 변경 — 카드 × 바이어 1행(빈칸 = 그대로). 역할 ①(데이터)이 한 줄씩 반영한다",
        "invoice_changes": "인보이스 단위 변경(해당 카드의 인보이스 결제기일 재설정). 13_EarlyWarning에 붙여 넣기 전에 바꾼다",
        "scenarios": "카드별 시나리오 값 — 고른 행을 11_Scenario에 값으로 붙여 넣는다",
        "new_buyer": "해당 카드의 신규 바이어 속성(3개월 전 · 지금)",
        "new_buyer_features": "신규 바이어 특성 2행 — 앱 ② 업로드용(d3_start_scoring.csv와 같은 열)",
        "limit_realloc": "D6-C4 한도 재배정 표 — 현행 한도 · 4일차 한도 + 팀이 채울 빈칸",
        "budget": "연간 채권관리 · 대외자문 예산 표(가상) — ROI 템플릿 입력",
        "templates": "양식 파일 위치 목록(labs/day6/)",
    }
    csvs = [
        Item(f"data/checkpoints/d6_crisis_pack_{k}.csv", f"csv/d6_crisis_pack_{k}.csv", f"위기 데이터 팩 — {k} 시트(CSV)",
             f"{k} 시트와 같은 내용(UTF-8 BOM) — {d}. Colab · 앱 업로드 · 코딩 에이전트용",
             ("cards",), "🟣")
        for k, d in pack_csv.items()
    ]
    return [
        Item("labs/day6/hackathon_rules.md", "hackathon_rules.md", "해커톤 규칙 한 장",
             "규칙 6가지 · 하루 흐름 · 사람이 결정하는 것 4종 · 하지 말 것 · 인젝트가 오면 · 막히면(감점 없음) · 1:1 코칭·발표. 팀마다 A4 2장 인쇄", ("hack",), "🟢", when=eve),
        Item("labs/day6/role_cards.md", "role_cards.md", "역할 카드 5종",
             "데이터 · 모델·등급 · 한도·시나리오·ROI · 규정·RAG·거버넌스 · SOP·커뮤니케이션·발표 + 저장소 관리자 — 넘기는 것 · 완료 체크. 09:25 역할 이슈에 쓴다", ("hack",), "🟢", when=eve),
        Item("labs/day6/judging_rubric.xlsx", "judging_rubric.xlsx", "심사 루브릭(엑셀)",
             "기준 6개 × 1–4점 앵커 · 산식 · 시상(점수 칸 없는 공개본)", ("hack",), "🟢", when=eve),
        Item("labs/day6/judging_rubric.md", "judging_rubric.md", "심사 루브릭(텍스트)",
             "엑셀판과 같은 앵커 문구를 마크다운으로 — 브라우저·AI에서 바로 읽는다", ("hack",), "🟢", when=eve),
        Item("labs/day6/standup_board.md", "standup_board.md", "CP2 스탠드업 양식",
             "끝낸 것 · 막힌 것 · 오후 첫 작업", ("hack",), "🟢", when=eve),
        Item("labs/day6/presentation_template.md", "presentation_template.md", "7분 데모 대본 틀",
             "위기 요약 → 라이브 데모 → SOP → ROI·KPI → 솔루션 킷 → 첫 30일 + 예상 질문", ("hack", "kit"), "🟢", when=eve),
        Item("labs/day6/kit_checklist.md", "kit_checklist.md", "솔루션 킷 체크리스트",
             "README 5항목 · 폴더 6개 · 보안 점검(3검색 0건) · v1.0 릴리스 절차 · GitHub이 막힐 때 · 제3자 재현 테스트", ("kit",), "🟢", when=eve),
        Item("labs/day6/sop_template.md", "sop_template.md", "SOP 양식",
             "0–10장 + 부록: 발동 조건 · RACI · T+0/24h/72h/1주 조치 · 종료 조건(팀 저장소 sop/SOP_template.md와 같다)", ("kit",), "🟢", when=eve),
        Item("labs/day6/roi_kpi_template.xlsx", "roi_kpi_template.xlsx", "ROI·KPI 템플릿",
             "팀 ROI 3안(보수·기준·낙관) · 도구비 S0–S3 · BCR · ROI · 회수기간 · 개인 '나만의 KPI'", ("kit",), "🟢", when=eve),
        Item("labs/day6/ax_proposal_template.md", "ax_proposal_template.md", "AI 도입 기획서 양식(11장)",
             "개인 제출: 7–11장을 채워 17:50 마감(비공개 폼, 저장소에 올리지 않는다). Word·Google Docs로 옮겨 .docx로 낸다", ("kit",), "🟢", when=eve),
        Item("data/checkpoints/d6_crisis_pack.xlsx", "d6_crisis_pack.xlsx", "위기 데이터 팩",
             "카드별 트리거 데이터(시트 cards · injects · buyer_changes · invoice_changes · scenarios · new_buyer · limit_realloc · budget · templates). "
             "역할 ①(데이터)이 받아 바이어 데이터에 반영한다",
             ("cards",), "🟢"),
        *teams,
        Item("data/checkpoints/d6_card5_stage2.xlsx", "d6_card5_stage2.xlsx", "카드 ⑤ 2단계 데이터",
             "11:15 카드 ⑤ 팀에 2단계 카드와 함께 공개한다(다른 팀은 쓰지 않는다)",
             ("cards",), "🟢", phase="answer", when="10/21(수) 11:15"),
        Item(_card_src(5, "stage2"), "cards/card5_stage2.md", "위기 카드 ⑤ 2단계 카드",
             "11:15 카드 ⑤ 팀에 종이 카드와 같은 내용으로 공개한다(다른 팀은 쓰지 않는다)",
             ("cards",), "🟢", phase="answer", when="10/21(수) 11:15"),
        *cards,
        *csvs,
    ]


LAB_AB = {"lab-a": "실습 A", "lab-b": "실습 B", "data": "참고용"}

HANDOUT_DATES = {1: "10/14(수)", 2: "10/15(목)", 3: "10/16(금)", 4: "10/19(월)", 5: "10/20(화)", 6: "10/21(수)"}


def handout(n: int) -> Item:
    """그날 강의 슬라이드의 수강생판 PDF(D18·D28) — instructor/deck_tools/deck_handout.py가 만든 handouts/dayN_slides.pdf.
    .gitignore 대상이라 당일 18:00에 `git add -f handouts/dayN_slides.pdf`로 공개한다(그 전에는 '공개 예정')."""
    return Item(f"handouts/day{n}_slides.pdf", f"day{n}_slides.pdf", "강의 슬라이드(PDF)",
                "그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개",
                ("hack",) if n == 6 else ("lab-a", "lab-b"), "🟢", phase="answer", when=f"{HANDOUT_DATES[n]} 18:00")


def build_days() -> list[Day]:
    return [
        Day(1, "10/14(수)", "10/13(화)", (2026, 10, 14, 9, 0, 0), LAB_AB, ("lab-a", "lab-b"), build_day1() + [handout(1)]),
        Day(2, "10/15(목)", "10/15(목) 08:30", (2026, 10, 15, 8, 30, 0), LAB_AB, ("lab-a", "lab-b"), build_day2() + [handout(2)]),
        Day(3, "10/16(금)", "10/16(금) 08:30", (2026, 10, 16, 8, 30, 0), LAB_AB, ("lab-a", "lab-b"), build_day3() + [handout(3)]),
        Day(4, "10/19(월)", "10/19(월) 08:30", (2026, 10, 19, 8, 30, 0), LAB_AB, ("lab-a", "lab-b"), build_day4() + [handout(4)]),
        Day(5, "10/20(화)", "10/20(화) 08:30", (2026, 10, 20, 8, 30, 0), LAB_AB, ("lab-a", "lab-b"), build_day5() + [handout(5)]),
        Day(6, "10/21(수)", "10/21(수) 09:28", (2026, 10, 21, 9, 28, 0),
            {"hack": "해커톤 안내", "cards": "위기 카드", "kit": "솔루션 킷"}, ("hack", "cards", "kit"), build_day6() + [handout(6)]),
    ]


# ---------------------------------------------------------------- 안전장치
def resolve(it: Item) -> None:
    """후보 경로(alts) 가운데 실제로 있는 첫 파일을 쓴다. 받는 이름도 그 파일 이름으로 바꾼다."""
    for cand in (it.src, *it.alts):
        if (REPO / cand).is_file():
            if cand != it.src:
                parent = Path(it.dest).parent.as_posix()
                it.dest = Path(cand).name if parent == "." else f"{parent}/{Path(cand).name}"
                it.src = cand
            return


def guard(day: Day) -> None:
    for it in day.items:
        for alt in it.alts:
            if any(p in alt.lower() for p in FORBIDDEN_PARTS):
                sys.exit(f"[중단] 수강생용이 아닌 후보 경로가 허용 목록에 있습니다: {alt}")
        low = it.src.lower()
        bad = [p for p in FORBIDDEN_PARTS if p in low]
        if bad or ".." in Path(it.dest).parts or Path(it.dest).is_absolute():
            sys.exit(f"[중단] 수강생용이 아닌 경로가 허용 목록에 있습니다: {it.src} (금지 조각: {bad})")
        if it.labs and any(k not in day.labels for k in it.labs):
            sys.exit(f"[중단] Day{day.n} 허용 목록의 '쓰는 곳' 키가 잘못됐습니다: {it.src} {it.labs}")
        if it.phase not in ("start", "answer"):
            sys.exit(f"[중단] phase는 start 또는 answer만 됩니다: {it.src}")
        if low.startswith("data/checkpoints/"):
            rel = low[len("data/checkpoints/"):]
            name = rel.rsplit("/", 1)[-1]
            top = rel.split("/", 1)[0]  # 하위 폴더(d6_teams/team_01.xlsx)는 폴더 이름의 dN_ 접두를 본다
            if name in SHARED_CHECKPOINTS:
                continue
            m = re.match(r"d(\d)_", top)
            if not m or int(m.group(1)) != day.n:
                sys.exit(f"[중단] 다른 날의 체크포인트는 Day{day.n} 목록에 넣을 수 없습니다(전날 정답이 미리 나간다): {it.src}")
            if top.startswith(f"d{day.n}_end"):
                sys.exit(f"[중단] 그날 정답본(d{day.n}_end*)은 사이트 허용 목록에 넣지 않습니다(릴리스 d{day.n}-end로만): {it.src}")
            if "answer" in name and it.phase != "answer":
                sys.exit(f"[중단] 정답 파일은 phase='answer'(정한 시각 공개)로만 넣습니다: {it.src}")


def git_tracked() -> set[str] | None:
    """이 저장소에서 git이 추적하는 파일(= 공개된 파일). git을 쓸 수 없거나 이 폴더가 저장소의 맨 위가 아니면 None."""
    base = ["git", "-c", f"core.excludesFile={os.devnull}", "-C", str(REPO)]
    try:
        top = subprocess.run(base + ["rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        if Path(top.stdout.strip()).resolve() != REPO.resolve():
            return None
        out = subprocess.run(base + ["ls-files", "-z"], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.decode("utf-8", "replace").split("\0") if p}


def is_held(day: Day, it: Item, tracked: set[str] | None, preview: bool) -> bool:
    """원본은 있지만 아직 공개 전인가(2일차부터만 본다)."""
    if preview or day.n == 1:
        return False
    if tracked is None:
        return not IN_CI and bool(SENSITIVE.search(it.src))
    return it.src not in tracked


# ---------------------------------------------------------------- 복사·압축
def human_size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{max(1, round(n / 1024)):,} KB"


def copy_files(day: Day, tracked: set[str] | None, preview: bool, dry: bool) -> None:
    dest_dir = day.dest_dir
    for it in day.items:
        resolve(it)
        src = REPO / it.src
        it.exists = src.is_file()
        it.held = it.exists and is_held(day, it, tracked, preview)
        it.size = src.stat().st_size if it.exists else 0
    expected = {it.dest for it in day.items if it.ready} | {day.zip_name}
    if not dry and dest_dir.exists():
        # 허용 목록 밖 파일·공개 전으로 돌아간 파일 정리
        for p in sorted(dest_dir.rglob("*"), reverse=True):
            rel = p.relative_to(dest_dir).as_posix()
            if p.is_file() and rel not in expected:
                p.unlink()
                print(f"  - 삭제(허용 목록 밖·공개 전): downloads/day{day.n}/{rel}")
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
    for it in day.items:
        if not it.exists:
            label = "없음(건너뜀)" if day.n == 1 else f"아직 없음 — 공개 예정 {day.when(it)}"
            print(f"  ! {label}: {it.src}")
            continue
        if it.held:
            print(f"  ~ 공개 전(git 미추적 — 공개 시각에 커밋·push하면 들어간다): {it.src}")
            continue
        if not dry:
            out = dest_dir / it.dest
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / it.src, out)
        print(f"  + {it.src}  →  docs/downloads/day{day.n}/{it.dest}  ({human_size(it.size)})")


def make_zip(day: Day) -> int:
    """공개된 파일만 묶는다. 같은 내용이면 같은 zip이 나오도록 날짜를 고정한다."""
    path = day.dest_dir / day.zip_name
    present = [it for it in day.items if it.ready]
    if not present:
        if path.exists():
            path.unlink()
        return 0
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for it in sorted(present, key=lambda x: x.dest):
            info = zipfile.ZipInfo(f"{day.zip_root}/{it.dest}", date_time=day.zip_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (day.dest_dir / it.dest).read_bytes())
    return path.stat().st_size


# ---------------------------------------------------------------- '파일 받기' 표
def link(day: Day, it: Item, prefix: str) -> str:
    if not it.ready:
        return "준비 중" if day.n == 1 else f"공개 예정<br>{day.when(it)}"
    fname = Path(it.dest).name
    return f'[:material-download: 받기]({prefix}{it.dest}){{ download="{fname}" }}'


def zip_row(day: Day, prefix: str, zip_size: int) -> str:
    if day.n == 1:
        what = (f"아래 파일 전부를 `{day.zip_root}` 폴더 하나로 묶은 압축 파일."
                f" 보고서 발췌(.md)는 `{day.zip_root}/reports` 폴더 안에 있다")
    else:
        subdirs = sorted({it.dest.split("/")[0] for it in day.items if it.ready and "/" in it.dest})
        what = f"지금까지 공개된 아래 파일을 `{day.zip_root}` 폴더 하나로 묶은 압축 파일"
        if subdirs:
            what += " · 하위 폴더 " + " · ".join(f"`{day.zip_root}/{d}`" for d in subdirs) + " 포함"
    return (
        f"| **`{day.zip_name}`**<br>**한 번에 받기** | {what}"
        f" | 전체 | {human_size(zip_size)} | [:material-folder-download: **받기**]({prefix}{day.zip_name})"
        f'{{ download="{day.zip_name}" }} |'
    )


def missing_note(day: Day) -> list[str]:
    if day.n == 1:
        return [
            "",
            '!!! note "준비 중인 파일"',
            "    '준비 중'으로 표시된 파일은 강사가 올리는 대로 이 표에 링크가 생깁니다."
            " 화면을 새로 고쳐도 없으면 강사에게 알려 주세요.",
        ]
    return [
        "",
        '!!! note "공개 전 파일"',
        "    '공개 예정'으로 표시된 파일은 적힌 시각에 이 표에 링크가 생깁니다."
        " 시각이 지났는데도 링크가 없으면 화면을 새로 고치고, 그래도 없으면 강사에게 알려 주세요.",
    ]


HEADER = "<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->"


def table_all(day: Day, prefix: str, zip_size: int) -> str:
    lines = [HEADER, "", "| 파일 | 무엇인가 | 쓰는 곳 | 크기 | 받기 |", "|---|---|---|---|---|"]
    if zip_size:
        lines.append(zip_row(day, prefix, zip_size))
    for it in day.items:
        where = " · ".join(day.labels[x] for x in it.labs)
        size = human_size(it.size) if it.ready else "–"
        lines.append(
            f"| `{Path(it.dest).name}`<br>{it.title} | {it.desc} | {where} {it.track} | {size} | {link(day, it, prefix)} |"
        )
    if any(not it.ready for it in day.items):
        lines += missing_note(day)
    return "\n".join(lines) + "\n"


def table_section(day: Day, key: str, prefix: str) -> str:
    lines = [HEADER, "", "| 파일 | 무엇인가 | 트랙 | 받기 |", "|---|---|---|---|"]
    for it in day.items:
        if key in it.labs:
            lines.append(f"| `{Path(it.dest).name}` | {it.desc} | {it.track} | {link(day, it, prefix)} |")
    return "\n".join(lines) + "\n"


def write_snippets(day: Day, zip_size: int, dry: bool) -> None:
    page_prefix = f"../downloads/day{day.n}/"  # docs/dayN/*.md 용
    outputs = {
        "files_all.md": table_all(day, page_prefix, zip_size),
        "files_all_root.md": table_all(day, f"downloads/day{day.n}/", zip_size),  # docs/*.md 용
    }
    for key in day.sections:
        outputs[f"files_{key}.md"] = table_section(day, key, page_prefix)
    if dry:
        return
    day.snip_dir.mkdir(parents=True, exist_ok=True)
    for p in day.snip_dir.glob("files_*.md"):  # 구역 이름이 바뀌어 남은 옛 표 정리
        if p.name not in outputs:
            p.unlink()
            print(f"  - 삭제(옛 표): docs/_snippets/day{day.n}/{p.name}")
    for name, text in outputs.items():
        (day.snip_dir / name).write_text(text, encoding="utf-8")
    print(f"  * 표 갱신: docs/_snippets/day{day.n}/ ({', '.join(outputs)})")


# ---------------------------------------------------------------- 실행
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="아무것도 바꾸지 않고 상태만 확인(필수 파일이 빠졌으면 종료코드 1)")
    ap.add_argument("--strict", action="store_true", help="필수 파일이 빠졌으면 종료코드 1")
    ap.add_argument("--require-day", type=int, action="append", default=[], metavar="N",
                    help="N일차 시작 파일도 필수로 본다(그날 공개 뒤에, 여러 번 쓸 수 있다)")
    ap.add_argument("--preview", action="store_true",
                    help="공개(커밋) 전 파일도 복사 — 강사 PC 미리 보기 전용. 이 결과로 만든 site/를 배포·USB로 나누지 않는다")
    args = ap.parse_args()

    days = build_days()
    bad_days = [n for n in args.require_day if not 1 <= n <= len(days)]
    if bad_days:
        ap.error(f"--require-day는 1–{len(days)}만 됩니다: {bad_days}")
    required_days = {1} | set(args.require_day)
    for day in days:
        guard(day)
    tracked = git_tracked()
    print(f"[sync_site_assets] 저장소: {REPO}")
    if tracked is None:
        print("  (git을 쓸 수 없어 공개 여부를 확인하지 못했습니다 — 2–6일차의 정답 위험 경로는 건너뜁니다)")
    if args.preview:
        print("  [미리 보기] 공개 전 파일도 복사합니다. 이 상태로 만든 site/·site_offline/을 배포하거나 나눠 주지 마세요.")

    missing_required: list[str] = []
    for day in days:
        print(f"[Day{day.n} · {day.date}]")
        copy_files(day, tracked, args.preview, dry=args.check)
        zip_size = 0 if args.check else make_zip(day)
        if not args.check and day.dest_dir.is_dir() and not any(day.dest_dir.iterdir()):
            day.dest_dir.rmdir()  # 공개된 파일이 하나도 없는 날은 빈 폴더를 남기지 않는다
        if zip_size:
            print(f"  + 묶음: docs/downloads/day{day.n}/{day.zip_name} ({human_size(zip_size)})")
        write_snippets(day, zip_size, dry=args.check)
        if not (REPO / "labs" / f"day{day.n}" / "prompts.md").is_file():
            print(f"  ! labs/day{day.n}/prompts.md 가 아직 없습니다 — 프롬프트 라이브러리 {day.n}일차 페이지가 비어 보입니다.")
        ready = sum(it.ready for it in day.items)
        print(f"  = Day{day.n}: 허용 목록 {len(day.items)}개 중 {ready}개 공개됨, {len(day.items) - ready}개 공개 전·없음")
        if day.n in required_days:
            missing_required += [f"Day{day.n} {it.src}" for it in day.items if it.phase == "start" and not it.ready]

    print(f"[sync_site_assets] 필수(Day{', Day'.join(str(n) for n in sorted(required_days))}) 중 빠진 파일 {len(missing_required)}개")
    for m in missing_required:
        print(f"  ! 필수 파일 없음: {m}")
    if missing_required and (args.check or args.strict):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
