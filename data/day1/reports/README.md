# 1일차 실습 자료 — AI로 해외 기업 보고서 읽고 검증하기

1일차(10/14) 블록 A(4–5교시) Step 2–3에서 AI에 올려 읽는 **해외 바이어 보고서 발췌**와, AI가 계산한 비율을 대조할 **SEC 추출 비율표**다.
핵심 습관은 하나다: **AI가 준 문장은 원문에서 Ctrl+F로 찾고, AI가 준 숫자는 1차 출처 숫자와 맞춰 본다.**

## 1. 파일 목록

| 파일 | 무엇인가 | 출처 | 언제 쓰나(과정 사이트 1일차 → 실습 A) |
|---|---|---|---|
| `irobot.md` | iRobot 10-K FY2024 발췌: 대출 약정 면제, 계속기업 의문, 위탁생산 의존, 유동성, 감사보고서, 고객·공급사 집중, 재무표 | SEC EDGAR(2025-03-12 접수) | 🟢 Step 3 ④(P1-2 → SEC 수치 대조, P1-1은 시간이 되면) |
| `plug_power.md` | Plug Power 3개 공시 발췌: PART A 10-Q 2023년 3분기(경고), PART B 10-K FY2023(경고 해소 문구), PART C 10-K FY2024(문구 없음) + 맨 끝 '이후 경과' | SEC EDGAR | 🔵 Step 2 Standard(P1-1 → P1-1b) · Step 3 Standard(P1-7) — **오탐 반례** |
| `wolfspeed.md` | Wolfspeed 10-Q(2025-03-30 분기) 발췌: 계속기업 의문, 약 65억 달러 부채, 최소 현금 약정, 분기·9개월 손익 | SEC EDGAR(2025-05-09 접수) | 확장(P1-1·P1-2) |
| `big_lots.md` | Big Lots 10-Q(2024-05-04 분기) 발췌: 최소 가용한도 약정 위반 가능성, 14.6% 차입 금리, 공급사 금융 중단 + 직전 10-K의 해외 직접 조달 비중 | SEC EDGAR(2024-06-13 접수) | 확장(P1-1·P1-2) |
| `halden_fictional_annual_report.md` | **가상** 영국 유통 바이어 연차보고서 발췌(재무표 2개년 포함). 위험 신호와 안심 요소를 강사가 미리 심어 둔 문서 | 강사 창작(가상) | 🟢 Step 2(P1-1 → Ctrl+F) · Step 3(P1-2) · 14:20 정답 공개 뒤 'AI 채점 실험'(아래 3절) |
| `gorman_note.md` | D&B 샘플 보고서 "Gorman Manufacturing"(가상 기업, 13쪽) **링크와 읽기 안내만** | D&B 샘플(링크) | 확장(P1-2) |
| `../real_buyers_ratios.csv` (`.xlsx`) | 위 4개사의 SEC XBRL companyfacts 원값과 4대 비율(9행: 발췌와 같은 기간 + 비교 기간) | SEC companyfacts API | 🟢 Step 3 ④ 대조 |

> 옛 기획 문서(03 Part2 §1.3)에 적힌 경로 `data/reports/excerpts/*.md`는 이 폴더 `data/day1/reports/`를 가리킨다. 클릭 순서는 과정 사이트 1일차 → 실습 A 페이지(Step 2–3)가 정본이다.

## 2. 실습 흐름 (실습 A Step 2–3, 슬라이드 #52)

1. 파일을 내려받아 바탕화면 `D1` 폴더에 둔다. 발췌 파일은 메모장이나 브라우저로 열린다.
2. **🟢 Halden(가상)**: AI 새 채팅 → `halden_fictional_annual_report.md` 업로드 → P1-1(`{회사명}`=Halden Industrial Supplies Ltd., `{문서}`=Annual Report FY2026(2025-07-01~2026-06-30)). AI 표의 '원문 인용' 2개를 원문에서 Ctrl+F로 찾는다.
3. **🟢 비율**: 같은 채팅에서 P1-2(`{기간}`=FY2026(2026-06-30 기준), `{비교기간}`=FY2025) → 14:20에 강사가 공개하는 기준값과 비교한다.
4. **🟢 iRobot(실제 공시)**: 새 채팅 → `irobot.md` 업로드 → (시간이 되면 P1-1) → P1-2(`{회사명}`=iRobot Corporation, `{문서}`=Form 10-K FY2024) → `real_buyers_ratios.csv`의 iRobot 행과 대조(차이율 1% 초과면 원인을 적는다).
5. **🔵 Plug Power(오탐 반례)**: 새 채팅 → `plug_power.md` 업로드 → P1-1(`{문서}`=PART A — Form 10-Q 2023년 3분기) → 같은 채팅에서 P1-1b(`{문서1}`=PART A → `{문서2}`=PART B — Form 10-K FY2023; 한 번 더: PART B → PART C) → AI 주장을 P1-7로 판정.
   - 파일 맨 끝 '이후 경과'는 P1-1b까지 끝낸 뒤 읽는다.
6. **확장**: Wolfspeed·Big Lots 발췌로 P1-1·P1-2(10-Q는 분기 기간 일수 주의), Gorman PDF(링크)로 P1-2.

## 3. Halden(가상 보고서) 쓰는 법 — 'AI 채점 실험'

1. Step 2–3에서 Halden으로 P1-1·P1-2를 돌린 결과(템플릿 `01_보고서신호`·`02_비율검증`)를 그대로 쓴다.
2. 강사가 정답 목록(심어 둔 위험 신호와 안심 요소)을 공개하면, AI가 **놓친 신호**와 **위험이 아닌데 위험으로 표시한 것**을 센다.
3. 놓친 비율(재현율)과 헛짚은 비율(정밀도)은 3일차 모델 평가 지표와 같은 생각이다.

## 4. 검증 요령

- **인용 찾기**: 발췌 파일의 따옴표는 모두 곧은 따옴표(`'` `"`)다. 그래도 Ctrl+F가 안 되면 인용 중간의 짧은 단어 4–5개로 찾는다. 없으면 P1-1c로 재질문한다.
- **단위**: 발췌의 재무표는 천 달러(iRobot·Big Lots·Plug Power) 또는 백만 달러(Wolfspeed), Halden은 천 파운드다. `real_buyers_ratios.csv`는 모두 **달러 원 단위**다.
- **기간**: 10-Q는 분기(3개월·13주) 또는 누적(9개월) 손익이다. 분기 매출로 DSO를 구할 때 365를 곱하면 약 4배로 부풀려진다. 기간 일수(91일 등)를 쓴다.
- **총부채**: Wolfspeed·Big Lots 재무상태표에는 '총부채' 합계 행이 없다. 유동부채만 넣지 말고 부채 항목을 모두 더한다.
- **자본잠식**: 자본총계가 0 이하이면 부채비율은 "해석 불가"다(P1-2 규칙 4).
- **XBRL 태그**: iRobot의 FY2024 10-K는 매출채권을 `AccountsAndOtherReceivablesNetCurrent`로 공시했다. companyconcept에서 `AccountsReceivableNetCurrent`로 조회해도 같은 날짜(2024-12-28) 값이 나오지만, 그 값의 출처는 이후 10-Q의 비교 열이다(`form`·`filed` 열로 확인). Wolfspeed의 2025-06-29 `Liabilities`도 FY2025 10-K에는 없고 이후 공시의 비교 열에만 있다. Big Lots는 매출채권 계정 자체가 없다(소매업) → DSO는 "없음".

## 5. 비율표 `real_buyers_ratios.csv` 읽는 법

- 한 행 = 한 회사·한 기간. `row_role` 열에 그 행의 용도(발췌 일치, 전년 비교, 실습 가이드 정답 등)가 있다.
- 금액 열: `current_assets`, `current_liabilities`, `total_liabilities`, `stockholders_equity`, `accounts_receivable_net`, `revenue`, `operating_income`(모두 USD).
- 비율 열: `current_ratio`, `debt_to_equity`(자본잠식이면 빈칸, `negative_equity_flag`=1), `dso_days`(연간은 365일, 분기는 `dso_basis_days`), `op_margin`(소수)·`op_margin_pct`(%).
- 근거 열: `xbrl_tags_used`(어떤 태그에서 뽑았나), `data_note`(태그 모호성·주의), `filing_url`, `companyfacts_url`.
- 이후 경과 열: `going_concern_flag`, `later_event`, `later_event_date`, `creditor_outcome` — **실습 후** 본다.
- `.xlsx`에는 `dictionary`(한글 열 설명)·`source` 시트가 함께 있다.

## 6. 출처와 이용 조건

- **SEC 공시**(iRobot·Wolfspeed·Big Lots·Plug Power): 미국 SEC EDGAR에 제출된 **공개 공시**를 교육 목적으로 **일부만** 발췌했다. 원문 전체는 각 파일 머리의 URL에서 본다. 문장은 고치지 않았다(곧은 따옴표 변환만). 원문의 저작권과 책임은 각 회사에 있다. 비율표는 SEC XBRL companyfacts API(`data.sec.gov`)에서 2026-10-01에 추출해 계산했다.
- **SEC 자료를 직접 받을 때**: User-Agent에 이름과 이메일을 적고 초당 10회 미만으로 호출한다(SEC 공정접근 정책).
- **D&B Gorman 샘플**: **링크만** 제공한다. PDF에 D&B 저작권 표시가 있으므로 이 저장소나 공유 공간에 PDF를 올리지 않는다.
- **Halden**: 강사가 만든 가상 문서다. 등장하는 회사·은행·감사법인·보험사는 모두 가상이며 실존 기업과 무관하다. 과정 저장소의 문서 라이선스(CC BY 4.0)를 따른다.
- 이 폴더의 어떤 자료도 투자·여신 판단 자료가 아니다.

## 7. [실습 후 읽기] 네 회사의 이후 경과 (2026-09-30 기준, SEC 공시로 확인)

| 회사 | 경고 공시 | 이후 사건 | 거래처(무담보 채권자) 결과 | 근거 |
|---|---|---|---|---|
| iRobot | 10-K FY2024(2025-03-12): 계속기업 의문 | 2025-12-14 Chapter 11(사전조정형) → 2026-01-23 회생계획 발효 → 2026-01-26 등록 말소(Form 15) | 담보채권 전부를 가진 공급사 Picea가 지분 100%. **Picea 외 거래처 미지급금은 전액 지급 대상**, 기존 주주는 0 | 8-K 2025-12-15, 8-K 2026-01-26 |
| Wolfspeed | 10-Q(2025-05-09): 계속기업 의문 | 2025-06-30 Chapter 11(사전조정형) → 2025-09-29 회생계획 발효·탈출 → 지금도 공시 중 | 공급사 등 무담보채권자는 **전액·정상 지급 예정**으로 신청 | 8-K 2025-07-01, 8-K 2025-09-30, 10-K 2026-08-20 |
| Big Lots | 10-Q(2024-06-13): 약정 위반 가능성 → 계속기업 의문 | 2024-09-09 Chapter 11 → 2025-01-03 자산 매각 종결 → 2025-10-24 Chapter 7(청산) 전환 신청 | 정상 지급 대상은 **신청 '이후' 공급분**으로 명시. 신청 전 미수금은 파산 절차 배당에 의존 | 8-K 2024-09-10, 8-K 2025-10-30 |
| Plug Power | 10-Q(2023-11-09): 계속기업 의문 | 2024-02-29 10-K에서 '의문 해소' 기재. 2026-09-30까지 파산 신청 공시 없음 | 해당 없음(부도 없음) — **오탐** | `plug_power.md` 맨 끝 |

**교훈 두 줄**: ① 같은 '파산'이라도 거래처 채권의 운명은 담보·우선순위·절차 종류(사전조정 회생 vs 매각·청산)에 따라 전혀 다르다. ② 경고 문구는 부도를 예고하지 않을 수도 있다(Plug Power). 문구 유무가 아니라 현금 소진 속도, 차입 약정, 공급사 조건 변화를 함께 본다.
