<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 트랙 | 받기 |
|---|---|---|---|
| `d2_start.xlsx` | 1일차 강사 정답본에서 이어지는 파일. 시트 buyers · buyer_features_raw · fx_at_ref · invoices_raw(🟣) · dirty_list · map_ccy · map_country · dictionary | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `d2_news.csv` | 바이어별 짧은 뉴스 문장(합성 300행). 블록 B 위험지수(0–10) 점수화 입력 | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `news_warmup_10.txt` | Step 6 워밍업용 텍스트(한국어 4 · 영어 6, 점수 없음). P2-2 맨 아래에 그대로 붙여 넣는다(탭 구분) | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `d2_news_answer.csv` | Step 7 일치도(MAE · ±2 이내 비율) 계산용 기준 점수. 정한 시각에 공개한다 | 🟢 | 공개 예정<br>10/15(목) 15:35 |
| `d2_orange_preprocess.ows` | 막혔을 때 비교용 완성본: File(d2_step1.xlsx · features) → Column Statistics · Impute(재무비율 4종 = 내 중앙값, 1-NN 비교) · Continuize · Preprocess(보기만) · Save Data · (선택) 뉴스 Group by · Merge. Orange 3.40 File → Open | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `d2_challenge.ipynb` | Colab: 통화·금액 · 기준일 환율(merge_asof) · 결측 대체(중앙값 vs KNN) · 파이프라인 안 스케일링 · 특성 공학 · LLM 없는 사전 기준선 뉴스 점수와 골든셋 일치도 | 🟣 | 공개 예정<br>10/15(목) 08:30 |
| `day2_slides.pdf` | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 🟢 | 공개 예정<br>10/15(목) 18:00 |
