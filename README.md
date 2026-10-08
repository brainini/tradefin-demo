# tradefin-ai-2026 — 생성형 AI 기반 무역 금융 리스크 최적화 과정 실습 저장소

수출·구매 실무자를 위한 6일 실습 과정의 **과정 사이트 원고, 실습 파일, (가상) 한빛정밀(주) 합성 데이터**를 담은 저장소입니다.
무역금융 판단은 수강생 여러분이 하고, 이 저장소는 AI로 읽고·검증하고·정리하는 방법을 손으로 익히도록 돕습니다.

> (가상) 한빛정밀(주)과 Halden은 교육용 가상 회사이며 실존 기업과 무관합니다.
> 이 저장소의 어떤 자료도 투자·여신 판단 자료가 아닙니다.

## 과정 정보

| 항목 | 내용 |
|---|---|
| 과정 | 생성형 AI 기반 무역 금융 리스크 최적화 과정(재직자) |
| 기간 | 2026-10-14(수) ~ 10-21(수), 주말 빼고 6일 · 매일 09:00–18:00 |
| 강사 | 한태구 |
| 과정 사이트 | [https://brainini.github.io/tradefin-ai-2026/](https://brainini.github.io/tradefin-ai-2026/) (GitHub Pages) |
| 문의 | 과정 오픈채팅 |

| 일차 | 날짜 | 주제(교수계획서 원문) | 파이프라인 단계 | 오늘의 파일 |
|---|---|---|---|---|
| 1 | 10/14(수) | 무역 금융 AI 트렌드 및 글로벌 바이어 데이터 탐색 | 원시 데이터 확보 및 탐색적 데이터 분석(EDA) | [1일차 페이지 → 파일 받기](docs/day1/index.md) |
| 2 | 10/15(목) | 금융/재무 데이터 전처리 및 리스크 평가지표 변수화 | 정형·비정형 융합 특성 공학(Feature Engineering) | 그날 08:30 공개 |
| 3 | 10/16(금) | AI 기반 대금 결제 연체 및 바이어 부도 리스크 예측 | 머신러닝 모델링 및 평가지표 검증 | 그날 08:30 공개 |
| 4 | 10/19(월) | 수출채권 회수 전략 최적화 및 조기 경보 시뮬레이션 | 예측 기반 의사결정 최적화 및 시뮬레이션 | 그날 08:30 공개 |
| 5 | 10/20(화) | AI 금융 에이전트 및 채권 관리 종합 제어 대시보드 구축 | 엔드투엔드(End-to-End) 솔루션 패키징 및 배포 | 그날 08:30 공개 |
| 6 | 10/21(수) | 실전 적응력 고도화 및 자사 솔루션 도입 기획(해커톤) | [최종 산출물] AI 기반 무역 금융 리스크 관리 통합 파이프라인 솔루션 킷 | 그날 09:00 공개 |

## 3분 시작 — 과정 사이트 쓰는 법

1일차에는 사이트만 있으면 됩니다 — 로그인 없이 읽고, 파일을 받고, 프롬프트를 복사합니다.
**GitHub 계정은 전원 필요합니다.** 2일차 8교시에 이 저장소를 템플릿으로 개인 저장소를 만들어 첫 커밋을 하고(`workbench/`), 5일차에는 fork해 Streamlit 앱을 배포하고 팀 저장소를 만듭니다. 개강 전에 가입과 이메일 인증을 끝내 주세요 → [사전 준비](docs/setup.md).

1. [과정 사이트](https://brainini.github.io/tradefin-ai-2026/)를 엽니다(주소는 첫날 화면과 오픈채팅으로도 안내합니다).
2. 홈에서 **오늘(Day1) 실습 열기**를 누르고, Day1 페이지의 **파일 받기**에서 `day1_files.zip`을 받습니다.
3. 받은 zip을 바탕화면 `D1` 폴더에 풉니다.
4. Lab 페이지 위쪽 탭에서 트랙을 고릅니다 — 🟢 Basic(전원) · 🔵 Standard · 🟣 Challenge. 언제든 바꿔도 됩니다.
5. 프롬프트 상자 오른쪽 위의 **복사** 버튼으로 프롬프트를 복사해 AI 채팅에 붙여 넣고, 맨 아래 `[이번 입력]` 줄의 `{중괄호}`만 바꿉니다.
6. 결과는 템플릿 `d1_end_eda_template.xlsx` 하나에 쌓고, `d1_end_eda__T조-번호.xlsx`(예: `d1_end_eda__T2-07.xlsx`)로 저장해 제출합니다.
7. 🟣 Challenge는 `d1_challenge.ipynb`를 받아 Colab 메뉴 **파일 → 노트북 업로드**로 엽니다.

못 끝낸 실습이 있어도 괜찮습니다. 다음 날 아침 전날 실습의 **체크포인트 파일**이 올라오고, 그 파일로 바로 합류합니다.

바로가기: [사이트 홈 원고](docs/index.md) · [과정 소개](docs/course.md) · [사전 준비](docs/setup.md) · [1일차](docs/day1/index.md) · [이론 요약](docs/day1/theory.md) · [실습 A(Step 1–4)](docs/day1/lab-a.md) · [실습 B(Step 5–8)](docs/day1/lab-b.md) · [프롬프트 원문](labs/day1/prompts.md) · [데이터 설명](docs/data.md) · [FAQ](docs/faq.md)

## 저장소 지도

| 경로 | 무엇 |
|---|---|
| `docs/` | 과정 사이트 원고(MkDocs Material). 사이트에서 보는 것이 가장 편합니다 |
| `workbench/` | **개인 작업 폴더** — 2일차에 이 저장소를 템플릿으로 만든 개인 저장소에서 `day2`–`day5` 결과(규칙 · 프롬프트 · 데이터 사전 · 결과 파일)를 커밋하는 곳. 쓰는 법은 `workbench/README.md` |
| `kit_template/` | 6일차 **팀 솔루션 킷 템플릿**의 원본(README 5항목 · data · app · sop · roi · docs · 이슈·PR 양식) — 강사가 `brainini/tradefin-kit-template`으로 공개합니다 |
| `labs/day1/` | 프롬프트 원문 `prompts.md` · 실습 템플릿 `d1_end_eda_template.xlsx` · AX 캔버스 · Challenge 노트북 |
| `data/day1/` | Day1 배포 파일 — 바이어 스냅샷 · 인보이스 원장(🟣) · 해외 기업 보고서 발췌(`reports/`) · SEC 비율표 |
| `data/data_dictionary.xlsx` | 데이터 사전(컬럼 · 코드 · 결제조건 코드표 · 파일 목록) |
| `data/checkpoints/` | 날짜별 체크포인트 — 그날 공개된 파일만 있습니다 |
| `data/external/` | FRED 환율 원본 캐시와 출처 표기(`ATTRIBUTION.md`) |
| `tools/` | 사이트 동기화·빌드 훅, 외부 데이터 수집, 노트북 빌더, 차트용 글꼴 |
| `mkdocs.yml` · `.github/workflows/pages.yml` | 사이트 설정과 자동 배포(이 저장소에서만 돈다 — 템플릿 사본·fork에서는 건너뜀) |
| `LICENSE` · `LICENSE-DATA.md` · `NOTICE.md` | 라이선스 전문(코드 MIT · 데이터·문서 CC BY 4.0)과 제3자 자료 출처 표기 |

## 데이터 위생

- 이 저장소의 실습 데이터는 전부 **합성 데이터**이거나 **공개 공시**입니다.
- 회사 실데이터, 고객사 실명, 담당자 이름·이메일·계좌, API 키는 이 저장소에도, 포크에도 올리지 않습니다.
- **AI 대화창은 외부 채널입니다.** 내 데이터를 쓰려면 먼저 [데이터 위생 5원칙과 익명화 체크리스트](docs/setup.md)를 확인하세요. 회사 보안 규정이 있으면 그것이 우선입니다.

## 라이선스와 출처

Copyright (c) 2026 Taegu Han. 전문은 [`LICENSE`](LICENSE)(코드 · MIT) · [`LICENSE-DATA.md`](LICENSE-DATA.md)(데이터·문서 · CC BY 4.0, 제3자 자료의 이용 조건)에, 제3자 자료의 출처 표기는 [`NOTICE.md`](NOTICE.md)에 있습니다.

| 대상 | 조건 | 전문·자세히 |
|---|---|---|
| 코드(`tools/`, `labs/`의 노트북·수식, 사이트 설정·워크플로) | **MIT License** | [`LICENSE`](LICENSE) |
| (가상) 한빛정밀 합성 데이터 · Halden 가상 보고서 · 사이트 글 · 템플릿 · 프롬프트 원문 | **CC BY 4.0** — 출처를 밝히면 자유롭게 쓸 수 있습니다. 표기 예: "생성형 AI 기반 무역 금융 리스크 최적화 과정(한태구), CC BY 4.0" | [`LICENSE-DATA.md`](LICENSE-DATA.md) 1절 |
| SEC 공시 발췌(iRobot · Plug Power · Wolfspeed · Big Lots) | 미국 SEC EDGAR의 **공개 공시를 교육 목적으로 일부 발췌**했습니다. 원문의 저작권과 책임은 각 회사에 있고(CC BY 4.0을 붙이지 않음), 원문 링크는 [데이터 페이지](docs/data.md)의 '보고서 발췌' 표에 있습니다 | [`LICENSE-DATA.md`](LICENSE-DATA.md) 2절 · [`NOTICE.md`](NOTICE.md) |
| SEC 비율표(`real_buyers_ratios`) | SEC XBRL companyfacts API(data.sec.gov)에서 2026-10-01에 추출·계산 | 같음 |
| D&B Gorman 샘플 보고서 | **링크만** 제공합니다. PDF는 이 저장소·공유 드라이브·단체방에 올리지 않습니다 | 같음 |
| 환율(`data/external/`) | FRED H.10 — "Public Domain: Citation Requested". 인용 방법은 `data/external/ATTRIBUTION.md` | [`NOTICE.md`](NOTICE.md) |
| 글꼴(`tools/fonts/`) | NanumGothic, SIL Open Font License 1.1(`tools/fonts/OFL.txt`) | [`NOTICE.md`](NOTICE.md) |
| 외부 공개 데이터(UCI 등) | 아직 넣지 않았습니다. 넣을 때 원본 조건·DOI·조회일을 `data/external/ATTRIBUTION.md`에 적습니다 | [`LICENSE-DATA.md`](LICENSE-DATA.md) 3절 |

## 다시 만들기

### 과정 사이트

저장소 루트에서 실행합니다(Python 3.12 이상).

```bash
pip install -r requirements-docs.txt
python tools/sync_site_assets.py              # 수강생 파일을 docs/downloads/로 복사하고 '파일 받기' 표를 만든다
mkdocs serve                                  # http://127.0.0.1:8000 에서 미리 보기
mkdocs build --strict -d site                 # 정적 사이트를 site/에 만든다(경고가 하나라도 있으면 실패)
OFFLINE=true mkdocs build -d site_offline     # USB·file:// 배포판(검색까지 오프라인으로 동작)
```

- **배포**: GitHub 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 한 번 정하면, `main`에 push할 때마다 `.github/workflows/pages.yml`이 파일 복사 → strict 빌드 → 배포를 합니다. Actions 탭의 **Run workflow**로 직접 돌려도 됩니다.
- `docs/downloads/`, `site/`, `site_offline/`은 빌드할 때마다 새로 만드는 결과물이라 커밋하지 않습니다(`.gitignore`).
- `tools/sync_site_assets.py`는 일차별 허용 목록에 있는 수강생 파일만 복사합니다. 정답·원천 경로가 섞이면 멈추고, 2일차부터는 git에 커밋된(= 공개된) 파일만 사이트에 넣습니다. `--strict`는 1일차 파일이 다 있는지, `--require-day N`은 N일차 시작 파일까지 확인합니다.

### 데이터

- 모든 합성 데이터는 고정 seed(`20261014`)로 만들었습니다. 같은 라이브러리 버전(`requirements.txt`)이면 같은 파일이 나오고, 파일별 SHA-256은 `data/checkpoints/_manifest.json`에 있습니다.
- 만드는 순서(자세한 설명은 `tools/README.md`):

    ```bash
    pip install -r requirements.txt
    python tools/fetch_external.py fred     # 1) FRED 환율 캐시(네트워크는 여기서만)
    python tools/generate_data.py           # 2) 원천 세계 → data/raw/
    python tools/build_checkpoints.py       # 3) Day별 배포 파일 · 체크포인트 · 데이터 사전
    python tools/validate_data.py           # 4) 검사(실패하면 종료코드 1)
    python tools/make_day1_charts.py        # 5) Day1 실습 가이드 차트
    python tools/build_day1_template.py     # 6) Day1 엑셀 템플릿 · AX 캔버스
    ```

- **과정 중에는 이 순서를 이 저장소만으로 돌릴 수 없습니다.** 모든 단계가 생성기 설정(`tools/config.yaml`)을 읽는데, 이 설정과 일부 생성기, 원천(`data/raw/`)에는 실습의 정답(숨은 등급·심어 둔 결함·시나리오)이 들어 있어 **과정이 끝난 뒤(2026-10-21 이후)** 올립니다. 그 전에 쓸 데이터는 `data/day1/`·`data/checkpoints/`·`data/external/`에 이미 만들어져 있습니다.
- SEC 보고서 발췌와 비율표는 강사가 SEC에서 추출해 만들었습니다. 원문 링크는 각 발췌 파일 머리와 [데이터 페이지](docs/data.md)에 있습니다. SEC 자료를 직접 받을 때는 User-Agent에 **본인 영문 이름과 이메일**을 적고, 초당 10회 미만으로 요청합니다.
- Challenge 노트북은 `tools/build_day1_notebook.py`로 다시 만듭니다(`--org <GitHub 조직 이름>`으로 Colab 배지와 데이터 주소를 채웁니다). 실행 검사(`--execute`)는 SEC에 접속하므로 `--user-agent "영문 이름 이메일"`을 함께 넘깁니다 — 기본값이 없습니다.

## 공개 범위 — 이 저장소에 없는 것

공개 저장소에는 **수강생 파일**만 둡니다. 실습 양식 · 노트북 · 프롬프트 · 사이트 페이지는 정답이 들어 있지 않아 미리 올라올 수 있고, **데이터 체크포인트 · 정답 · 위기 카드처럼 시각이 정해진 파일은 그 시각에 맞춰** 올립니다. 아래는 `.gitignore`로 막혀 있습니다.

| 무엇 | 왜 | 언제 공개 |
|---|---|---|
| 강사 정답지 · 정답 워크북 · 결함 기록 · 강사 운영 자료 | 실습 정답 | 공개하지 않습니다 |
| 다음 날 체크포인트(`data/checkpoints/d2_start.xlsx` 등) | 전날 실습의 정답본 | 그날 아침(09:00 전) |
| 원천 `data/raw/` · 생성기 설정과 일부 생성기 · `tools/news_pool/` | 숨은 정답 컬럼 · 결함 계획 · 점수 | 과정이 끝난 뒤 |
| Day1 정답 차트(`docs/assets/day1/`) | 정제한 결과 수치 | 과정이 끝난 뒤 |
| 사이트 빌드 결과(`site/`, `docs/downloads/`) | 배포 때마다 새로 만든다 | 커밋하지 않습니다 |

오류를 발견하면 과정 오픈채팅으로 알려 주세요. 과정 중 수정 사항은 사이트 위쪽 공지로 안내합니다.
