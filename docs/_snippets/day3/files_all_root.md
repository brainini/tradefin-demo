<!-- 자동 생성: tools/sync_site_assets.py — 직접 고치지 말고 스크립트를 다시 돌리세요 -->

| 파일 | 무엇인가 | 쓰는 곳 | 크기 | 받기 |
|---|---|---|---|---|
| **`day3_files.zip`**<br>**한 번에 받기** | 지금까지 공개된 아래 파일을 `D3` 폴더 하나로 묶은 압축 파일 | 전체 | 4 KB | [:material-folder-download: **받기**](downloads/day3/day3_files.zip){ download="day3_files.zip" } |
| `d3_start_features.csv`<br>학습용 특성(300행) | 150개사 × 기준일 2개, 레이블 late_30d(정상 0 / 연체 1). Orange File 위젯: buyer_id = meta, late_30d = target | 실습 A 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `d3_start_scoring.csv`<br>예측 대상(150행) | 같은 특성, 기준일 2026-09-30, 레이블 없음. Predictions 위젯 입력 → 바이어별 연체 확률 | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `d3_features_panel.csv`<br>바이어 × 월 패널 | 같은 특성의 월별 패널(4,017행, 2024-01~2026-08). 🔵 시간 분할 비교 · 🟣 SMOTE 실습 | 실습 A 🔵 | – | 공개 예정<br>10/16(금) 08:30 |
| `d3_orange_model.ows`<br>Orange 모델 워크플로 | 완성 워크플로: 70/30 층화 분할 · 학습셋 복제 오버샘플 · Gradient Boosting(xgboost) · Test and Score · Confusion Matrix · ROC(FP 1 : FN 5) · Calibration Plot · Predictions · Save Data · Explain Model/Prediction. CSV와 같은 D3 폴더에서 File → Open | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `d3_grade_banding.xlsx`<br>등급 매칭 시트 | pred 시트에 buyer_id · 확률을 붙이고 이름 t(빈칸)에 내 임계값 → IFS 등급 · 경계 · 분포 · 단조성(시험셋) · 6열 CSV 시트 | 실습 B 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `d3_shap_report_template.docx`<br>SHAP 해석서 양식 | P3-1 출력 5칸(결론 · 위험↑ 3 · 위험↓ 2 · 확인할 것 3 · 한계 3) + 캡처 2칸 — A4 1장 | 실습 B 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `fx_forecast_inputs.csv`<br>환율 예측 입력 | 원/달러 일별 종가(FRED DEXKOUS, 2023-09~2026-09)와 학습(train)·확인(valid) 구간 표시. Step 8 환율 위험 구간 | 실습 B 🟢 | – | 공개 예정<br>10/16(금) 08:30 |
| `uci_taiwan_bankruptcy.csv`<br>UCI 대만 기업 부도 데이터 | 외부 공개 벤치마크(CC BY 4.0, 출처 표기). 🔵 부도가 드문 데이터에서 지표 비교 | 실습 A 🔵 | – | 공개 예정<br>10/16(금) 08:30 |
| `fred_dexkous.csv`<br>FRED 원/달러 원본 | 미국 연준 FRED DEXKOUS 원본 시계열(퍼블릭 도메인, 출처 표기 요청). 🟣 Prophet 입력 | 실습 B 🟣 | 15 KB | [:material-download: 받기](downloads/day3/fred_dexkous.csv){ download="fred_dexkous.csv" } |
| `d3_challenge.ipynb`<br>Challenge 노트북 | Colab: LightGBM · SMOTE(학습셋만) · SHAP + Prophet 환율 예측 구간. '런타임 다시 시작 후 모두 실행'으로 재현을 확인한다 | 실습 A · 실습 B 🟣 | – | 공개 예정<br>10/16(금) 08:30 |
| `day3_slides.pdf`<br>강의 슬라이드(PDF) | 그날 강의 슬라이드의 수강생판 — 발표자 노트 제외, 외부 기관 화면 캡처는 자리 표시(강의장에서만 보여 준다). 당일 18:00 공개 | 실습 A · 실습 B 🟢 | – | 공개 예정<br>10/16(금) 18:00 |

!!! note "공개 전 파일"
    '공개 예정'으로 표시된 파일은 적힌 시각에 이 표에 링크가 생깁니다. 시각이 지났는데도 링크가 없으면 화면을 새로 고치고, 그래도 없으면 강사에게 알려 주세요.
