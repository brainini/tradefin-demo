# 실습 A · 4–5교시 — 30일 이내 연체 확률 예측 모델(Orange)

!!! abstract "한눈에 보기 — 블록 A (Step 1–4)"
    | 항목 | 내용 |
    |---|---|
    | 목표 | 코딩 없이 30일 연체 확률 모델을 학습하고, **정확도 대신 놓친 연체(FN)와 비용**으로 평가해 **임계값 t**를 정한다 |
    | 시간 | **13:00–14:50** (휴식 13:50–14:00) · 4–5교시 |
    | Step | 1 실행 · 분할 · 2 학습셋만 늘리기 · 3 학습 · 평가(FN 목록) · 4 비용으로 임계값 |
    | 입력 | `d3_start_features.csv`(300행 = 150개사 × 기준일 2개, 라벨 `late_30d`) · `d3_orange_model.ows` |
    | 도구 | Orange 3.40(포터블 + Explain · Timeseries 애드온) · 엑셀 · (🔵) AI 대화창 |
    | 산출물 | `d3_work__T조-번호.xlsx`의 `01_평가` · `02_임계값` |
    | 프롬프트 | 🔵 [P3-2](../prompts/day3.md#p3-2) |

!!! quote "교수계획서 원문 — 블록 A"
    o (4~5교시 / 2H) 노코딩 머신러닝 AI 도구를 활용하여 과거 거래 패턴 데이터 기반 바이어의 30일 이내 대금 연체 가능성 확률 예측 모델 구현 실습

!!! tip "계획서의 'LightGBM'은 오늘 Orange에서 xgboost로 합니다"
    Orange에는 LightGBM 위젯이 없어 Gradient Boosting 위젯의 **xgboost** 방식(같은 GBDT 계열)으로 대신합니다. SMOTE 대신 **학습셋 복제 오버샘플**을 씁니다. 원형은 🟣 Colab `d3_challenge.ipynb`에 있습니다.
    오늘 시험셋에는 연체가 몇 건뿐이라 지표가 조마다 흔들립니다 — **숫자보다 절차**를 맞춥니다.

## 시간 {#time}

| 시각 | Step | 하는 일 |
|---|---|---|
| 13:00–13:07 | 실습 브리핑 | 3.4–3.6 계획서 원문(#34–36) |
| 13:07–13:15 | [Step 1](#step1) | 강사 시연(워크플로 열기 · File 재지정, 5분) → 역할 지정 → Data Sampler 70/30(층화 · 재현) → `d3_work` 만들기 |
| 13:15–13:30 | [Step 2](#step2) | 학습셋의 연체 행만 복제해 늘리기 → 누수 퀴즈 |
| 13:30–13:50 | [Step 3](#step3) | xgboost 학습 → Test on test data → Confusion Matrix의 FN 목록 |
| 13:50–14:00 | 휴식 | |
| 14:00–14:05 | [Step 3](#step3) 마무리 | `01_평가` 정리 · 손계산 |
| 14:05–14:42 | [Step 4](#step4) | ROC Analysis 비용 5:1 → Calibration Plot(Sigmoid 보정) → 보정 척도의 t |
| 14:42–14:50 | **기대값 공개** · 점검 | 강사 화면 · [완료 기준](#checkpoint) 체크 · 저장 |

!!! tip "13:30 손 점검"
    13:30에 Concatenate 위젯까지 연결됐나요? 늦었다면 Step 2는 워크플로에 이미 연결된 그대로 두고 Step 3으로 넘어갑니다. 누수 퀴즈만 `01_평가`에 답합니다.

## 입력 파일 {#files}

--8<-- "docs/_snippets/day3/files_lab-a.md"

한 번에 받으려면 [3일차 → 파일 받기](index.md#files)의 `day3_files.zip`을 받아 바탕화면 `D3` 폴더로 풉니다. 🟣 노트북은 `d3_challenge.ipynb` 하나입니다.

??? note "워크플로 한 장 — `d3_orange_model.ows`의 위젯 체인"
    ```text
    [File] d3_start_features.csv  (late_30d: target · buyer_id · ref_date · split_suggested · sample_weight: meta)
      └─> [Data Sampler ①] 70% · Stratify ✔ · Replicable ✔
            ├─ Data Sample(학습 70%) ─┬────────────────────────────────────────┐
            │                        └─> [Select Rows] late_30d is 1           │
            │                               └─> [Data Sampler ②] 고정 개수 · 복원 추출 ─> [Concatenate] = 학습셋(오버샘플)
            └─ Remaining Data(시험 30% — 늘리지 않는다)
    [Gradient Boosting](xgboost) · [Logistic Regression](기준선)
      └─> [Test and Score] Test on test data · Target class 1
            ├─> [Confusion Matrix] → [Data Table](선택한 칸의 바이어)
            ├─> [ROC Analysis] FP 비용 1 · FN 비용 5
            └─> [Calibration Plot] Calibration curve + Sigmoid → 보정 모델  또는  지표 그래프의 세로선 = t → 임계값 모델 (하나만 출력) → (블록 B) [Predictions]
    [Gradient Boosting] ─> [Explain Model] · [Explain Prediction]   (블록 B Step 7)
    [File ②] d3_start_scoring.csv ─> [Predictions] ─> [Save Data]    (블록 B Step 5)
    ```

    워크플로 파일이 열리지 않으면 강사가 화면으로 보여 주는 이 체인을 위젯 하나씩 따라 이어도 됩니다.

---

## Step 1 실행 · 분할 {#step1}

**13:07–13:15 (8분, 강사 시연 포함)** · 완성 워크플로를 열고 역할을 맞춘 뒤, 시험셋을 먼저 떼어 둔다

=== "🟢 Basic"

    **① 작업 파일 만들기**

    1. 엑셀에서 **새 통합 문서**를 엽니다. 아래 시트 탭을 4개로 늘리고(**＋**), 탭을 더블클릭해 이름을 `01_평가` · `02_임계값` · `03_등급` · `04_환율`로 바꿉니다.
    2. **파일** → **다른 이름으로 저장** → `D3` 폴더 → `d3_work__T조-번호`(예: `d3_work__T2-07`) → **Excel 통합 문서** → **저장**.

    **② 워크플로 열기 → File 다시 지정**

    3. Orange를 실행합니다. 처음이면 **Options** → **Add-ons**에서 **Explain**과 **Timeseries**가 체크돼 있는지 봅니다(없으면 체크 → **OK** → Orange 다시 시작, [사전 준비 5번](../setup.md#orange)).
    4. **File** 메뉴 → **Open** → `D3` 폴더의 `d3_orange_model.ows`를 엽니다.
    5. 캔버스 왼쪽의 **File** 위젯을 더블클릭 → 폴더 아이콘 → `D3/d3_start_features.csv`를 고릅니다. 파일 경로가 PC마다 달라서 한 번은 다시 지정해야 합니다.

    **③ 역할 확인 — 정답과 식별자는 특성이 아니다**

    6. File 창 아래 열 표에서 **Role**을 확인하고, 다르면 고칩니다.

        | 열 | Role | 왜 |
        |---|---|---|
        | `late_30d` | **target** | 맞힐 정답(정상 0 / 연체 1) |
        | `buyer_id` · `ref_date` | **meta** | 식별자 · 날짜 |
        | `sample_weight` · `split_suggested` | **meta** | 보조 열 — `sample_weight`는 정답에서 만든 가중치라 특성으로 넣으면 **누수** |
        | `fx_krw_close` · `usd_krw_close` | **skip** | 기준일 환율 수준 — 같은 날 모든 바이어가 같은 값이라 '날짜 표시'일 뿐 |

    7. **Apply**를 누릅니다. 캔버스의 위젯 위 진행 막대가 사라질 때까지 기다립니다(전체가 다시 계산됩니다).

    **④ Data Sampler ① — 70/30 층화 · 재현**

    8. **Data Sampler** ①을 더블클릭해 설정을 확인합니다: **Fixed proportion of data** `70%` · **Stratify sample** ✔(연체 비율을 학습 · 시험에 똑같이) · **Replicable (deterministic) sampling** ✔(오늘의 시드).
    9. **Remaining Data**(시험셋 30%) 출력에 이어진 **Data Table**을 엽니다(없으면 Data Sampler 오른쪽 가장자리를 끌어 Data Table을 놓고, 연결선에서 **Remaining Data**를 고릅니다). `late_30d` 열 머리를 눌러 정렬하고 **1의 개수**를 셉니다.
    10. `01_평가` 시트 맨 위에 적습니다: 학습 행 수 · 시험 행 수 · **시험셋 연체 수**. 시험셋 연체가 몇 건뿐이라는 것을 기억해 둡니다 — 오늘 지표가 흔들리는 이유입니다.

=== "🔵 Standard"

    **바이어 단위로 나누기 — `split_suggested`**

    같은 바이어의 2월 · 8월 행이 학습과 시험에 갈려 들어가면 시험이 쉬워집니다(이미 본 바이어). `split_suggested`는 바이어 단위로 70/30을 미리 나눠 둔 열입니다.

    1. File 뒤에 **Select Rows**를 두 개 놓습니다: 하나는 `split_suggested` **is** `train`, 하나는 `split_suggested` **is** `test`.
    2. train 쪽을 Step 2의 Select Rows · Concatenate에, test 쪽을 Test and Score의 **Test Data**에 연결해 같은 체인을 하나 더 만듭니다(위젯은 ++ctrl+c++ · ++ctrl+v++ 로 복제).
    3. 무작위 70/30과 바이어 단위 분할의 시험 행 수 · 연체 수를 `01_평가`에 나란히 적습니다. Step 3에서 두 결과의 AUC를 비교합니다.

=== "🟣 Challenge"

    **Colab `d3_challenge.ipynb` A절 — 두 가지 분할**

    1. Colab에서 **파일** → **노트북 업로드** → `d3_challenge.ipynb`. 첫 칸(버전 출력)을 실행해 런타임 버전과 lightgbm · shap · imbalanced-learn · scikit-learn · prophet 버전을 메모합니다.
    2. `d3_start_features.csv`를 올리고 A절의 분할 칸을 실행합니다: `train_test_split(…, stratify=y, random_state=42)`(무작위) vs 바이어 단위 분할(같은 `buyer_id`는 한쪽에만).
    3. 특성 목록에서 `buyer_id` · `ref_date` · `sample_weight` · `split_suggested`가 빠졌는지 코드로 확인합니다.

---

## Step 2 학습셋만 늘리기 — 불균형 보정 {#step2}

**13:15–13:30 (15분)** · 학습셋의 연체 행만 복제해 늘리고, 왜 '나눈 뒤'에만 해야 하는지 이해한다

=== "🟢 Basic"

    **① 연결 확인 — 워크플로에 이미 있습니다**

    1. Data Sampler ①의 **Data Sample**(학습 70%) 출력 → **Select Rows**를 더블클릭: 조건이 `late_30d` **is** `1`인지 봅니다. 학습셋의 연체 행만 남깁니다.
    2. Select Rows → **Data Sampler** ②를 더블클릭: **Fixed sample size**의 개수 = **학습셋 연체 수 × 2** · **Sample with replacement** ✔(복원 추출 = 복제) · **Replicable** ✔. 학습셋 연체 수는 Select Rows 출력의 Data Table 행 수로 봅니다.
    3. **Concatenate**: 원래 학습셋(Data Sample) + 복제한 연체 행(Data Sampler ②)을 합칩니다. 연체가 원래의 **3배**가 됩니다 [교육용 가정].
    4. Concatenate 출력의 Data Table 행 수가 '학습 행 수 + 연체 수 × 2'인지 확인해 `01_평가`에 적습니다.

    **② 시험셋은 건드리지 않는다**

    5. **Remaining Data**(시험셋)는 어떤 위젯을 거쳐서도 Concatenate에 들어가지 않는지 연결선을 따라가 봅니다. 시험셋은 현실 비율 그대로 평가에만 씁니다.

    **③ 누수 퀴즈 — `01_평가`에 한 줄**

    6. **"Data Sampler ②(복제)를 Data Sampler ①(분할) 앞에 두면 무엇이 부풀까?"** — 이유까지 한 줄로 적습니다. 순회 때 강사가 묻습니다. 힌트: [이론 3.3.2](theory.md#m332)의 '올바른 순서' 그림.

=== "🔵 Standard"

    **class weight와 비교 — 'Balance class distribution'**

    1. Data Sampler ①의 **Data Sample**(오버샘플 **전** 원래 학습셋)을 **Random Forest**와 **Logistic Regression**에 각각 잇고, 두 위젯에서 **Balance class distribution** ✔(class weight)를 켭니다.
    2. 두 번째 **Test and Score**를 놓고 Data = 원래 학습셋, Test Data = Remaining Data, Learner = 두 모델 → **Test on test data** · Target class 1.
    3. Step 3의 '오버샘플 + xgboost'와 AUC · Recall을 `01_평가`에 나란히 적고, **"보정이 순서(AUC)를 바꾸나, 확률의 크기만 바꾸나"**를 한 줄로 씁니다.
    4. 언더샘플링(정상 행을 덜어 내기)을 했다면 무엇이 버려지는지 짝과 1분 토론합니다.

=== "🟣 Challenge"

    **SMOTE는 학습 폴드에만 — imblearn Pipeline**

    1. A절의 SMOTE 칸: `Pipeline([("smote", SMOTE(k_neighbors=3, random_state=42)), ("clf", LGBMClassifier(...))])` — `imblearn.pipeline`의 Pipeline이어야 fit 때 학습 폴드에만 적용됩니다.
    2. 기준 모델(SMOTE 없음)과 SMOTE · class weight 판의 ROC-AUC · PR-AUC · 평균 예측 확률을 표로 비교합니다. SMOTE가 성능을 '반드시' 올리지는 않는다는 것을 숫자로 확인합니다.
    3. 일부러 분할 **전에** SMOTE를 적용한 판을 하나 만들어 AUC가 얼마나 부풀는지 보고, 그 칸에 `# 누수 시연 — 실무에서 쓰지 않음` 주석을 답니다.

---

## Step 3 학습 · 평가 — FN 목록 {#step3}

**13:30–13:50 · 14:00–14:05 (25분)** · xgboost로 학습하고, 시험셋으로만 평가하고, '우리가 놓친 돈'을 바이어 목록으로 뽑는다

=== "🟢 Basic"

    **① 모델 설정 확인 — 바꾸지 않는다**

    1. **Gradient Boosting** 위젯을 더블클릭 → **Method**: **Extreme Gradient Boosting (xgboost)** · Number of trees `100` · Learning rate `0.1` · Limit depth `3` · **Replicable training** ✔ [교육용 가정]. 오늘은 이 값을 바꾸지 않습니다(작은 시험셋에 맞춰 튜닝하면 그 시험셋에 과적합).
        - xgboost가 회색(설치 안 됨)이면 [흔한 오류 3](#troubleshooting).
    2. **Logistic Regression**(기준선)도 같은 Test and Score에 연결돼 있는지 봅니다 — 새 모델은 단순한 기준선을 이겨야 씁니다.

    **② Test and Score — 시험셋으로만**

    3. **Test and Score**를 더블클릭: 왼쪽 **Test on test data**가 선택돼 있는지, 위쪽 **Target class**가 `1`인지 확인합니다. 입력은 Data = 학습셋(Concatenate) · Test Data = Remaining Data입니다.
    4. 표에서 두 모델의 **AUC · CA(정확도) · F1 · Precision · Recall**을 `01_평가`에 옮겨 적습니다.
    5. AUC가 0.99 이상으로 '너무 좋거나' 아래 ③의 FN이 이상하면, Step 1의 역할(특히 `sample_weight` · `buyer_id`)부터 다시 봅니다.

    **③ Confusion Matrix — '우리가 놓친 돈'**

    6. **Confusion Matrix**를 더블클릭 → 왼쪽 Learners에서 **Gradient Boosting** → Show: **Number of instances**.
    7. **실제 1 · 예측 0** 칸(놓친 연체 = FN)을 클릭합니다. 연결된 **Data Table**에 그 바이어들이 나옵니다.
    8. Data Table의 `buyer_id` 열을 끌어 선택해 복사하고 `01_평가`에 붙인 뒤 제목을 `FN — 정상이라 보고 선적했다가 연체된 바이어`라고 씁니다. 0곳이면 '0'이라고 적습니다.

    **④ 손계산 (14:00–14:05)**

    9. Confusion Matrix의 4칸(TP · FN · FP · TN)을 `01_평가`에 옮기고, 직접 계산합니다.

        | 칸 | 수식(셀 주소는 내 시트에 맞게) |
        |---|---|
        | 정밀도 | `=TP/(TP+FP)` |
        | 재현율 | `=TP/(TP+FN)` |
        | 비용 | `=5*FN+1*FP` [교육용 가정] |

    10. 손계산 정밀도 · 재현율이 Test and Score와 같은지 봅니다. ++ctrl+s++.

=== "🔵 Standard"

    **팀장용 3문단(P3-2) · 벤치마크**

    1. Test and Score · Confusion Matrix · ROC Analysis 화면을 캡처합니다(++win+shift+s++). **데이터 파일은 올리지 않고 캡처만** AI 새 채팅에 붙입니다.
    2. **P3-2**를 붙여 보냅니다. 화면에 없는 숫자가 답에 나오면 지웁니다.

        ??? example "P3-2 평가 화면 → 팀장용 3문단 — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P3-2 보기](../prompts/day3.md#p3-2)

            --8<-- "labs/day3/prompts.md:p3-2"

    3. (UCI 대만 데이터가 공개된 경우) 새 File로 `uci_taiwan_bankruptcy.csv`를 열고 target = `Bankrupt?`, 값이 모두 같은 열(`Net Income Flag`)은 **Select Columns**로 뺀 뒤 같은 체인을 돌립니다. 부도가 드문 다른 데이터에서 AUC와 Recall이 어떻게 달라지는지 한 줄로 적습니다. 열 이름 앞에 공백이 있을 수 있습니다.
    4. Step 1 🔵의 바이어 단위 분할 체인 결과(AUC)를 무작위 분할과 비교해 한 줄로 씁니다.

=== "🟣 Challenge"

    **패널 시간 분할 LightGBM**

    1. B절: `d3_features_panel.csv`(바이어 × 월, 4,017행)를 `split_suggested`의 train(과거) / test(최근) 기준으로 나눕니다 — 미래 행으로 과거를 맞히지 않는 **시간 분할**입니다.
    2. `LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=15, random_state=42)`로 학습하고 ROC-AUC · PR-AUC와 임계값 0.5의 혼동행렬을 출력합니다.
    3. 300행 Orange 결과와 숫자가 다른 이유(데이터 크기 · 분할 방식 · 모델)를 주석 3줄로 씁니다.

---

## Step 4 비용으로 임계값 정하기 {#step4}

**14:05–14:42 (37분) + 기대값 공개 14:42** · FN:FP = 5:1 비용으로 기준선을 정하고, 확률을 보정한다

=== "🟢 Basic"

    **① ROC Analysis — 비용 5:1의 최적점**

    1. **ROC Analysis**를 더블클릭 → **Target** `1` → **Show performance line** ✔ → **FP Cost** `1` · **FN Cost** `5`.
    2. 성능선(직선)이 곡선에 닿는 점이 비용이 가장 작은 지점입니다. 그 점의 **TPR(재현율) · FPR(헛경보 비율)**을 `02_임계값`에 적습니다.
    3. FN Cost를 `1`로 바꿔 점이 어디로 움직이는지 봅니다(캡처) → 다시 `5`로 돌립니다. 놓친 연체를 비싸게 볼수록 점이 오른쪽 위(더 많이 잡고 헛경보도 늘어남)로 갑니다.

    **② 이론값 — 비용 기준 임계값**

    4. 확률이 잘 보정돼 있다면 비용이 가장 작은 기준선은 **t = FP 비용 ÷ (FP 비용 + FN 비용) = 1 ÷ (1 + 5) ≈ 0.17**입니다. `02_임계값`에 식과 함께 적습니다.
    5. 오버샘플링으로 학습한 모델은 연체 확률을 부풀려 냅니다 — 그래서 다음 ③의 **보정**이 먼저입니다.

    **③ Calibration Plot — 보정 모델을 내보내고, 지표 그래프는 '감'만 잡는다**

    6. **Calibration Plot**을 더블클릭 → **Target** `1` → **Metrics**는 **Calibration curve**로 두고 **Output model calibration**에서 **Sigmoid calibration**을 고릅니다(이 선택은 Calibration curve 그래프에서만 보입니다). 곡선이 대각선에 가까울수록 '0.2라고 한 바이어 중 약 20%가 실제 연체'에 가깝습니다.
    7. 그래프 종류(**Metrics**)를 성능 지표(**Sensitivity and specificity** — 민감도 · 특이도 대 임계값)로 바꾸고, 그래프 위의 **세로 임계값 선**을 끌어 보며 선을 옮길 때 민감도(놓친 연체 FN)와 특이도(헛경보 FP)가 어느 쪽으로 움직이는지, 비용이 작은 구간이 얼마나 넓은지 '감'을 잡습니다(캡처 1장). **이 그래프의 가로축은 보정 전 모델의 확률**이라, 여기서 읽은 선의 위치를 t로 적지 않습니다 — 보정한 확률과 척도가 다릅니다.
    8. t는 **보정된 확률과 같은 척도**에서 정합니다. 기본은 ②의 이론값 **t = 1 ÷ (1 + 5) ≈ 0.17**을 `02_임계값`에 적는 것이고(보정이 잘 됐다면 비용 최소점과 같습니다), 시간이 있으면 🔵의 비용표(보정 모델의 시험셋 확률 `d3_test_pred.xlsx`로 t = 0.10 … 0.50의 FN · FP · 비용)를 만들어 비용이 가장 작은 구간에 0.17이 들어 있는지 확인합니다. 옆 칸에 근거 한 줄을 씁니다(예: `FN:FP = 5:1 → 이론 1/6 · 시험셋 비용표의 최소 구간 안`). 이 t가 그대로 Step 6 등급 매칭의 t입니다.
    9. **Metrics를 Calibration curve로 되돌려 둡니다.** Calibration Plot의 **출력 모델**은 **둘 중 하나**입니다(Orange 3.40) — **Metrics**가 **Calibration curve**이면 **보정(Sigmoid) 모델**, 지표 그래프에서 세로선을 끌어 둔 상태면 **보정하지 않은 원래 모델 + 임계값**이 나갑니다. 둘을 합친 모델은 없고, Predictions의 확률은 **마지막에 본 그래프**를 따릅니다. 이 과정은 보정한 확률을 쓰고 Step 6의 등급 매칭(`d3_grade_banding.xlsx`의 `pd_30d`와 이름 `t`)도 같은 척도여야 하므로, 되돌려 둔 상태로 넘깁니다. 그 출력 모델이 블록 B의 **Predictions**에 연결돼 있는지 봅니다(워크플로에 연결됨). ++ctrl+s++ 로 `d3_work`를 저장하고, Orange도 **File** → **Save As**로 `D3/d3_orange_model.ows`에 저장합니다(내 설정이 담긴 판 — 8교시 커밋).

    !!! success "기대값 공개 14:42–14:50 — 강사 화면으로만"
        1. 강사가 시험셋 크기에 따른 지표의 흔들림 범위, FN 목록 개수의 범위, t의 위치를 화면에 띄웁니다.
        2. 내 숫자가 범위 밖이면 원인을 `02_임계값`에 한 줄 적습니다 — 대개 **Target class가 0** · 교차검증 모드 · 역할 지정(누수) · 보정 안 함 중 하나입니다.
        3. 정답 파일은 나눠 주지 않습니다. 18:00에 강사 정답본이 공개됩니다.

=== "🔵 Standard"

    **임계값 게임 — t를 옮기면 비용이 어떻게 바뀌나**

    1. 시험셋에 보정 모델의 확률을 붙입니다: **Predictions** 위젯을 하나 더 놓고 Data = **Remaining Data**, Predictors = Calibration Plot의 출력 모델 → **Save Data** → `D3/d3_test_pred.xlsx`.
    2. 엑셀로 열어 표로 만들고(++ctrl+t++), 연체 확률 열(이름 끝에 `(1)`)과 실제 `late_30d` 열을 확인합니다.
    3. `02_임계값`에 표를 만듭니다: t = `0.10` · `0.17` · `0.25` · `0.35` · `0.50`마다

        | 칸 | 수식(표 이름 `tp`, 확률 열 `p1`로 바꾼 경우) |
        |---|---|
        | FN | `=COUNTIFS(tp[p1],"<"&t,tp[late_30d],1)` |
        | FP | `=COUNTIFS(tp[p1],">="&t,tp[late_30d],0)` |
        | 비용 | `=5*FN+FP` |

    4. 비용이 가장 작은 t 구간과, 0.17 근처에서 비용이 얼마나 평평한지 한 줄로 씁니다. 이 표의 확률은 보정 모델의 것이므로 여기서 고른 t가 그대로 Step 6 등급 매칭의 t입니다(`d3_grade_banding.xlsx` `기준` 시트 B3, 이름 `t`).
    5. **자사 비용비**: 내 회사에서 '놓친 연체 1건'과 '괜히 막은 바이어 1건'의 손해 비율을 추정해(예: 3:1 · 10:1) t를 다시 계산하고, **근거 한 줄**(마진 · 부보 여부 · 바이어 대체 가능성)을 적습니다.

=== "🟣 Challenge"

    **TunedThresholdClassifierCV — 비용 함수로 t 찾기**

    1. 비용 함수: `def neg_cost(y, p): tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel(); return -(5*fn + 1*fp)`.
    2. `TunedThresholdClassifierCV(pipe, scoring=make_scorer(neg_cost), cv=5, random_state=42).fit(X_train, y_train)` → `.best_threshold_`.
    3. `CalibratedClassifierCV(…, method="sigmoid", cv=5)`로 보정한 모델의 t와 Orange의 t를 비교하고, 다르다면 이유(보정 여부 · 데이터 · 분할)를 주석으로 씁니다.

---

## 블록 A 완료 기준 {#checkpoint}

14:42에 슬라이드를 다시 띄우고 함께 체크합니다. 다 못 끝내도 괜찮습니다 — 워크플로가 이미 연결돼 있어 블록 B는 그대로 이어집니다.

- [ ] **Step 1** — 역할 지정(target · meta · skip) · `01_평가`에 학습 · 시험 행 수와 시험셋 연체 수
- [ ] **Step 2** — 복제 오버샘플이 **학습셋에만** 연결 · 누수 퀴즈 답 한 줄
- [ ] **Step 3** — Test on test data · Target 1 지표(두 모델) · FN 바이어 목록 · 손계산(정밀도 · 재현율 · 비용)
- [ ] **Step 4** — ROC 5:1 최적점(TPR · FPR) · t와 근거 한 줄 · 보정 모델이 Predictions에 연결
- [ ] **저장** — `d3_work__T조-번호.xlsx` · Orange `d3_orange_model.ows`

## 흔한 오류와 해결 {#troubleshooting}

| # | 증상 | 원인 | 해결 |
|---|---|---|---|
| 1 | ROC Analysis · Calibration Plot에서 임계값 모델이 안 나온다 | Test and Score가 교차검증(Cross validation) 모드 | **Test on test data**를 고르고 Test Data 입력(Remaining Data)이 연결됐는지 확인 |
| 2 | AUC가 0.99 이상으로 비현실적으로 높다 | 분할 전에 복제했거나, `sample_weight` · `buyer_id`가 특성 | 체인 순서(분할 → 학습셋만 복제) · File의 Role을 다시 확인 |
| 3 | Gradient Boosting의 Method 목록에서 xgboost가 회색 | xgboost 라이브러리가 없다 | 강사가 준 포터블 Orange를 쓰거나, 임시로 scikit-learn 방식을 고르고 `01_평가`에 적어 둡니다 |
| 4 | 지표가 이상하게 좋거나 나쁘다 | **Target class가 0** | Test and Score · ROC Analysis · Calibration Plot 모두 Target = `1` |
| 5 | Confusion Matrix의 FN 칸을 눌러도 Data Table이 비어 있다 | Learner가 다르거나 Data Table이 연결되지 않았다 | 왼쪽 Learners에서 Gradient Boosting · 연결선의 출력이 **Selected Data**인지 확인 |
| 6 | File을 다시 지정했더니 역할이 모두 feature로 돌아갔다 | 파일 위치가 바뀌면 설정이 초기화될 수 있다 | [Step 1 ③](#step1)의 표대로 다시 지정 → **Apply** |
| 7 | 내 AUC가 옆 사람과 다르다 | 시험셋 연체가 몇 건뿐이라 행 하나에도 크게 움직인다 | 정상입니다. Replicable이 켜져 있는지만 확인하고, 숫자보다 절차를 맞춥니다 |
| 8 | 확률이 전반적으로 높게 나온다 | 오버샘플로 부풀려진 확률을 그대로 썼다(또는 Calibration Plot을 지표 그래프에 둔 채 넘겼다) | Calibration Plot(Sigmoid)의 출력 모델을 쓴다 — **Metrics**를 **Calibration curve**로 되돌린 뒤 Predictions를 다시 확인 |
| 9 | 세로 임계값 선이 안 잡힌다 | 그래프 종류가 보정 곡선이다 | 성능 지표 그래프로 바꾼 뒤 선을 끈다 · 확대 · 축소를 원래대로 |
| 10 | 워크플로를 열자 경고(!)가 여러 개 | File 경로가 비어 있어 아래 위젯이 계산을 못 했다 | Step 1 ②의 File 재지정 후 기다리면 사라집니다 |

더 많은 증상은 [FAQ·트러블슈팅](../faq.md)에 있습니다.

## 다 했으면 (확장) {#extend}

1. **기준선이 이겼나?** Logistic Regression과 Gradient Boosting의 AUC · Recall · 비용을 한 줄로 비교합니다. 기준선이 비슷하면, 설명하기 쉬운 쪽을 고를 이유가 됩니다.
2. **P3-2 팀장 설명**(🔵 탭)을 Basic도 해 봅니다 — 화면에 없는 숫자가 끼어들지 않는지 확인하는 연습입니다.
3. **FN 바이어 들여다보기**: FN 목록의 바이어 한 곳을 골라 `d3_start_features.csv`에서 연체 잔액 · 최장 미결 연체일 · 뉴스 위험을 보고, 모델이 왜 놓쳤을지 한 줄로 추측해 둡니다(블록 B Step 7의 SHAP과 비교).
4. **Replicable을 끄면?** Data Sampler ①의 Replicable을 잠깐 끄고 두 번 실행해 AUC가 바뀌는지 본 뒤 다시 켭니다 — 8교시 [기초 F3](../foundations/f3.md)의 '같은 입력이면 같은 결과'.

---

다음 → [실습 B · 6–7교시 — S/A/B/C 등급 매칭 · SHAP 해석서 · 환율 위험 구간](lab-b.md)
