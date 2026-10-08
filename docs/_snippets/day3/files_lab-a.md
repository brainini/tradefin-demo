<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 트랙 | 받기 |
|---|---|---|---|
| `d3_start_features.csv` | 150개사 × 기준일 2개, 레이블 late_30d(정상 0 / 연체 1). Orange File 위젯: buyer_id = meta, late_30d = target | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `d3_start_scoring.csv` | 같은 특성, 기준일 2026-09-30, 레이블 없음. Predictions 위젯 입력 → 바이어별 연체 확률 | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `d3_features_panel.csv` | 같은 특성의 월별 패널(4,017행, 2024-01~2026-08). 🔵 시간 분할 비교 · 🟣 SMOTE 실습 | 🔵 | 공개 예정<br>10/16(금) 08:30 |
| `d3_orange_model.ows` | 완성 워크플로: 70/30 층화 분할 · 학습셋 복제 오버샘플 · Gradient Boosting(xgboost) · Test and Score · Confusion Matrix · ROC(FP 1 : FN 5) · Calibration Plot · Predictions · Save Data · Explain Model/Prediction. CSV와 같은 D3 폴더에서 File → Open | 🟢 | 공개 예정<br>10/16(금) 08:30 |
| `uci_taiwan_bankruptcy.csv` | 외부 공개 벤치마크(CC BY 4.0, 출처 표기). 🔵 부도가 드문 데이터에서 지표 비교 | 🔵 | 공개 예정<br>10/16(금) 08:30 |
| `d3_challenge.ipynb` | Colab: LightGBM · SMOTE(학습셋만) · SHAP + Prophet 환율 예측 구간. '런타임 다시 시작 후 모두 실행'으로 재현을 확인한다 | 🟣 | 공개 예정<br>10/16(금) 08:30 |
| `day3_slides.pdf` | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 🟢 | 공개 예정<br>10/16(금) 18:00 |
