<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 트랙 | 받기 |
|---|---|---|---|
| `d3_start_scoring.csv` | 같은 특성, 기준일 2026-09-30, 레이블 없음. Predictions 위젯 입력 → 바이어별 연체 확률 | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `d3_orange_model.ows` | 완성 워크플로: 70/30 층화 분할 · 학습셋 복제 오버샘플 · Gradient Boosting(xgboost) · Test and Score · Confusion Matrix · ROC(FP 1 : FN 5) · Calibration Plot · Predictions · Save Data · Explain Model/Prediction. CSV와 같은 D3 폴더에서 File → Open | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `d3_grade_banding.xlsx` | pred 시트에 buyer_id · 확률을 붙이고 이름 t(빈칸)에 내 임계값 → IFS 등급 · 경계 · 분포 · 단조성(시험셋) · 6열 CSV 시트 | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `d3_shap_report_template.docx` | P3-1 출력 5칸(결론 · 위험↑ 3 · 위험↓ 2 · 확인할 것 3 · 한계 3) + 캡처 2칸 — A4 1장 | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `fx_forecast_inputs.csv` | 원/달러 일별 종가(FRED DEXKOUS, 2023-09~2026-09)와 학습(train)·확인(valid) 구간 표시. Step 8 환율 위험 구간 | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `fred_dexkous.csv` | 미국 연준 FRED DEXKOUS 원본 시계열(퍼블릭 도메인, 출처 표기 요청). 🟣 Prophet 입력 | 🟣 | [:material-download: 받기](../downloads/day3/fred_dexkous.csv){ download="fred_dexkous.csv" } |
| `d3_challenge.ipynb` | Colab: LightGBM · SMOTE(학습셋만) · SHAP + Prophet 환율 예측 구간. '런타임 다시 시작 후 모두 실행'으로 재현을 확인한다 | 🟣 | 공개 예정<br>10/16(금) 08:30 |
| `day3_slides.pdf` | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 🟢 | 공개 예정<br>10/16(금) 18:00 |
