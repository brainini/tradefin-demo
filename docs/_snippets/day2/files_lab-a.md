<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 트랙 | 받기 |
|---|---|---|---|
| `d2_start.xlsx` | 1일차 강사 정답본에서 이어지는 파일. 시트 buyers · buyer_features_raw · fx_at_ref · invoices_raw(🟣) · dirty_list · map_ccy · map_country · dictionary | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `fx_krw_daily.csv` | 최근 영업일 원화 환율. 기준일 이전 영업일(as-of) 환율로 USD 환산할 때 쓴다(엔화는 100엔 단위 → ÷100) | 🟢 | [:material-download: 받기](../downloads/day2/fx_krw_daily.csv){ download="fx_krw_daily.csv" } |
| `rules_template.md` | 정제규칙.md 틀 — 0 메타 · 1–8 규칙마다 '규칙 / 왜' 두 줄 · 9 변경 기록. 사이트 Step 2의 복사 상자와 같다. 메모장에 붙여 정제규칙.md로 저장한다 | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `d2_orange_preprocess.ows` | 막혔을 때 비교용 완성본: File(d2_step1.xlsx · features) → Column Statistics · Impute(재무비율 4종 = 내 중앙값, 1-NN 비교) · Continuize · Preprocess(보기만) · Save Data · (선택) 뉴스 Group by · Merge. Orange 3.40 File → Open | 🟢 | 공개 예정<br>10/15(목) 08:30 |
| `byod_anonymize_template.xlsx` | 자사 엑셀을 쓰기 전 점검표(규칙 7 + 마지막 확인 4) · 가상 예시 변환 수식. 원본은 내 PC에서만, 익명화본도 저장소에는 올리지 않는다(AI에는 익명화본만 · 학습 설정 끔) | 🔵 | 공개 예정<br>10/15(목) 08:30 |
| `d2_challenge.ipynb` | Colab: 통화·금액 · 기준일 환율(merge_asof) · 결측 대체(중앙값 vs KNN) · 파이프라인 안 스케일링 · 특성 공학 · LLM 없는 사전 기준선 뉴스 점수와 골든셋 일치도 | 🟣 | 공개 예정<br>10/15(목) 08:30 |
| `day2_slides.pdf` | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 🟢 | 공개 예정<br>10/15(목) 18:00 |
