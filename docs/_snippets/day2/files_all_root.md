<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 쓰는 곳 | 크기 | 받기 |
|---|---|---|---|---|
| **`day2_files.zip`**<br>**한 번에 받기** | 지금까지 공개된 아래 파일을 `D2` 폴더 하나로 묶은 압축 파일 | 전체 | 5 KB | [:material-folder-download: **받기**](downloads/day2/day2_files.zip){ download="day2_files.zip" } |
| `d2_start.xlsx`<br>2일차 시작 파일 | 1일차 강사 정답본에서 이어지는 파일. 시트 buyers · buyer_features_raw · fx_at_ref · invoices_raw(🟣) · dirty_list · map_ccy · map_country · dictionary | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/15(목) 08:30 |
| `fx_krw_daily.csv`<br>원화 환율(일별) | 최근 영업일 원화 환율. 기준일 이전 영업일(as-of) 환율로 USD 환산할 때 쓴다(엔화는 100엔 단위 → ÷100) | 실습 A 🟢 | 29 KB | [:material-download: 받기](downloads/day2/fx_krw_daily.csv){ download="fx_krw_daily.csv" } |
| `rules_template.md`<br>정제 규칙 양식 | 정제규칙.md 틀 — 0 메타 · 1–8 규칙마다 '규칙 / 왜' 두 줄 · 9 변경 기록. 사이트 Step 2의 복사 상자와 같다. 메모장에 붙여 정제규칙.md로 저장한다 | 실습 A 🟢 | – | 공개 예정<br>10/15(목) 08:30 |
| `d2_news.csv`<br>바이어 뉴스 | 바이어별 짧은 뉴스 문장(합성 300행). 블록 B 위험지수(0–10) 점수화 입력 | 실습 B 🟢 | – | 공개 예정<br>10/15(목) 08:30 |
| `news_warmup_10.txt`<br>워밍업 뉴스 10건 | Step 6 워밍업용 텍스트(한국어 4 · 영어 6, 점수 없음). P2-2 맨 아래에 그대로 붙여 넣는다(탭 구분) | 실습 B 🟢 | – | 공개 예정<br>10/15(목) 08:30 |
| `d2_news_answer.csv`<br>뉴스 점수 골든셋 | Step 7 일치도(MAE · ±2 이내 비율) 계산용 기준 점수. 정한 시각에 공개한다 | 실습 B 🟢 | – | 공개 예정<br>10/15(목) 15:35 |
| `d2_orange_preprocess.ows`<br>Orange 전처리 워크플로 | 막혔을 때 비교용 완성본: File(d2_step1.xlsx · features) → Column Statistics · Impute(재무비율 4종 = 내 중앙값, 1-NN 비교) · Continuize · Preprocess(보기만) · Save Data · (선택) 뉴스 Group by · Merge. Orange 3.40 File → Open | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/15(목) 08:30 |
| `byod_anonymize_template.xlsx`<br>BYOD 익명화 템플릿 | 자사 엑셀을 쓰기 전 점검표(규칙 7 + 마지막 확인 4) · 가상 예시 변환 수식. 원본은 내 PC에서만, 익명화본도 저장소에는 올리지 않는다(AI에는 익명화본만 · 학습 설정 끔) | 실습 A 🔵 | – | 공개 예정<br>10/15(목) 08:30 |
| `d2_challenge.ipynb`<br>Challenge 노트북 | Colab: 통화·금액 · 기준일 환율(merge_asof) · 결측 대체(중앙값 vs KNN) · 파이프라인 안 스케일링 · 특성 공학 · LLM 없는 사전 기준선 뉴스 점수와 골든셋 일치도 | 실습 A · 실습 B 🟣 | – | 공개 예정<br>10/15(목) 08:30 |
| `day2_slides.pdf`<br>강의 슬라이드(PDF) | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/15(목) 18:00 |

!!! note "공개 전 파일"
    '공개 예정'으로 표시된 파일은 적힌 시각에 이 표에 링크가 생깁니다. 시각이 지났는데도 링크가 없으면 화면을 새로 고치고, 그래도 없으면 강사에게 알려 주세요.
