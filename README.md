# tradefin-kit-T0 — V2 카드 솔루션 킷

> 모든 데이터는 교육용 가상 한빛정밀 데이터입니다. 실제 기업 · 사람 · 사건과 관계없습니다.

## 1. 목적

- **위기 카드**: V2 — 미국 바이어 SB07 회생 신청(가상)
- **한 줄 요약**: 미국 바이어 SB07이 회생(미국 파산법 11장)을 신청했다는 공시가 떴고, 오늘 오후 이 바이어 앞 선적이 예정돼 있다(상황). 카드 트리거는 SB07 `bankruptcy_flag = 1`과 US 바이어 `pd_multiplier = 1.3`이다. 그 결과 기대손실(EL)이 **8,364 → 38,757 USD**로 늘어난다(영향).
- **답한 질문**: 등급이 바뀌는 바이어(`out/v2/grade_changes.csv`), 한도를 얼마나 줄여야 하는지(`out/v2/limits_diff.csv`), 기대손실이 얼마나 늘어나는지(`out/v2/el_table.md`)
- **사람이 승인하는 것**: 30% 이상 감액되는 한도 2건(SB07 100,000 → 0 · SB01 90,000 → 60,000)과 SB07 앞 선적 보류. 스크립트는 "승인 필요"로 표시만 하고, 결정은 `docs/decision_log.md`에 사람이 적습니다.
- **인젝트(I-1 · I-2)**: 아직 반영하지 않았습니다.
- **데모 링크**: 없음

## 2. 구성

| 폴더 · 파일 | 들어 있는 것 |
|---|---|
| `data/input/v2_buyers.csv` | 가상 바이어 12곳(등급 · PD · 한도) |
| `app/pipeline/v2_run.py` | V2 카드 파이프라인(재등급 → 한도 → EL) |
| `out/v2/` | 파이프라인 출력: `change_log.csv` · `grade_changes.csv` · `limits_diff.csv` · `el_table.md` |
| `docs/` | `decision_log.md`(V2 결정 3행) · `kit_checklist.md` · 기획서 · 설계도 · 근거표 · 데모 대본 템플릿 |
| `sop/` | `SOP_template.md` · `ai_usage_rules.md`(템플릿) |
| `roi/` | `README.md`(`roi_kpi.xlsx`는 아직 없음) |
| `tools/get_day_files.py` | 과정 저장소에서 그날 파일 받기 |

각 폴더의 담당은 5항 참고.

## 3. 실행 방법

쓴 경로: **앱**(파이프라인 스크립트). Excel 근사나 강사 정답본은 쓰지 않았습니다.

1. 환경 만들기(처음 한 번): `uv sync`. `uv.lock`에 맞춰 `.venv`(Python 3.13)를 만듭니다.
2. 비공개 입력 3개를 아래 자리에 둡니다. 저장소에는 없고 `.gitignore`가 커밋을 막습니다.

   | 파일 | 둘 자리 | 받는 곳 |
   |---|---|---|
   | 가상 미결 인보이스 | `data/input/v2_demo_open_inv.csv` | 저장소 관리자(`brainini`)에게 받는다 |
   | 가상 위기 카드 | `cards/V2_card.md` | 저장소 관리자(`brainini`)에게 받는다 |
   | 가상 약관 발췌(선택) | `local/terms_demo.md` | 저장소 관리자(`brainini`)에게 받는다. 없어도 실행되지만 `el_table.md` 끝의 '참고' 줄이 빠집니다 |

3. 실행: `uv run python app/pipeline/v2_run.py`
4. 결과: `out/v2/`에 4개 파일이 다시 써지고, 터미널에 검산 3줄이 나옵니다. 아래와 같으면 재현에 성공한 것입니다.

   ```
   검산 1: 바이어 12곳 중 등급이 바뀐 곳 3 · 한도가 바뀐 곳 3 · 승인 필요 2
   검산 2: 한도 합계 880,000 → 730,000 USD
   검산 3: EL 합계 8,364 → 38,757 USD
   ```

   `git status`에 변경이 없으면 커밋된 결과와 같은 것입니다(시각 · 난수를 쓰지 않음).
5. 비공개 입력이 빠졌으면 스크립트가 빠진 파일 이름을 알려 주고 종료 코드 2로 끝납니다.

## 4. 데이터 원천과 가상 여부

모든 파일이 교육용 가상 한빛정밀 데이터입니다. 실명 · 이메일 · 키는 넣지 않습니다.

| 파일 | 가상 여부 | 저장소에 있는가 |
|---|---|---|
| `data/input/v2_buyers.csv` | 가상(`Demo Buyer 01–12`) | 있음 |
| `data/input/v2_demo_open_inv.csv` | 가상 인보이스 12건 | 없음(비공개) |
| `cards/V2_card.md` | 가상 위기 카드 | 없음(비공개) |
| `local/terms_demo.md` | 가상 약관 조항(실제 약관 아님) | 없음(비공개) |
| `out/v2/*` | 위 입력으로 계산한 결과 | 있음 |

체크리스트에 있는 `data/d6_{카드}_scored.csv` · `d6_{카드}_open_inv.csv` · `change_log.csv`는 이 킷에서 각각 `data/input/v2_buyers.csv` · `data/input/v2_demo_open_inv.csv`(비공개) · `out/v2/change_log.csv`가 맡습니다.

## 5. 담당자

| 조-번호 | 역할 | GitHub 아이디 |
|---|---|---|
| T0-1 | 저장소 관리자 | `brainini` |
