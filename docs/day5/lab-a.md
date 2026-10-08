# 실습 A · 4–5교시 — 사내 규정 RAG 챗봇: 기준선 → 튜닝 → 평가

!!! abstract "한눈에 보기 — 블록 A (Step 1–4)"
    | 항목 | 내용 |
    |---|---|
    | 목표 | 코드 없는 RAG로 **기준선**을 재고, **조항 단위 청킹 · Hybrid · Rerank**로 다시 만들고, **인용 · 기권 · 충돌 표시**가 강제된 챗봇을 연 뒤, **조화평균 F1@K로 Top-K**를 고른다 |
    | 시간 | **13:00–14:50** (휴식 13:50–14:00) · 4–5교시 |
    | Step | 1 기준선(Gemini Notebook) · 2 지식베이스 · 청킹(Dify) · 3 인용 · 기권 챗봇 · 4 검색 평가 |
    | 입력 | `rag/corpus/hanbit_credit_policy.md`(가상 여신관리규정) · K-SURE 약관 PDF(공식 링크) · 법령 조문(law.go.kr) · `rag/goldset_20.csv` · `rag/eval_sheet_template.xlsx` |
    | 도구 | Gemini Notebook(개인 Google 계정) · Dify Cloud Sandbox · Google Sheets · (🟣) Colab |
    | 산출물 | 노트북 `한빛_기준선_T조-번호` · 지식베이스 3개 · 챗봇 URL · **`d5_rag_eval__T조-번호.xlsx`** |
    | 프롬프트 | [P5-1](../prompts/day5.md#p5-1) · 🔵 [P5-2](../prompts/day5.md#p5-2) · 🟣 [인젝션 시험](../prompts/day5.md#ij) |

!!! quote "교수계획서 원문 — 블록 A"
    o (4~5교시 / 2H) 사내 여신 관리 지침 및 약관 PDF 문서를 완벽히 참조하는 금융 지식 검색(RAG) 엔진 시스템 연동 구축 실습

!!! tip "'완벽히 참조'는 측정으로 확인합니다"
    오늘은 '잘 답한다'를 느낌이 아니라 **골든셋 20문항**(정상 · 충돌 · 기권 문항)으로 잽니다. 검색은 P@K · R@K · F1@K, 답은 정답 · 인용 · 기권을 0/1로 채점합니다. 근거가 없으면 정확히 **"제공 문서에서 확인되지 않습니다."**가 정답입니다.

## 시간 {#time}

| 시각 | Step | 하는 일 |
|---|---|---|
| 13:00–13:07 | 실습 브리핑 | 5.4–5.6 계획서 원문 |
| 13:07–13:10 | 블록 A 안내 | Step 카드 · 짝 정하기(골든셋 Q01–Q10 / Q11–Q20 분담) |
| 13:10–13:25 | [Step 1](#step1) | Gemini Notebook 기준선 — 소스 3종 → 골든셋 10문항 → 인용 확인 → 0/1 기록 |
| 13:25–13:50 | [Step 2](#step2) | Dify 지식베이스 3개 · Parent-child 청킹 · Hybrid · Rerank ON → Retrieval Testing |
| 13:50–14:00 | 휴식 | Dify 인덱싱 대기 |
| 14:00–14:15 | [Step 3](#step3) | Dify 챗봇 · P5-1 · 인용 켜기 → 3문항 시험 → Publish |
| 14:15–14:45 | [Step 4](#step4) | 평가 시트(Google Sheets) — r1–r5 → F1@K(K = 1 · 3 · 5) → K 선택 · 이유 · 채점 |
| 14:45–14:50 | **기대값 공개** · 점검 | 강사 화면 · [완료 기준](#checkpoint) |

## 입력 파일 {#files}

--8<-- "docs/_snippets/day5/files_lab-a.md"

??? note "문서 세 가지와 조항 ID — 평가 시트에 적는 이름"
    | ID 머리 | 문서 | 받는 곳 |
    |---|---|---|
    | `HB-` | (가상) 한빛정밀(주) 여신관리규정 | 위 파일 표의 `hanbit_credit_policy.md` |
    | `KS-` | K-SURE 「단기수출보험(선적후) 약관」 17차 개정(2024-10-15) | `rag/corpus/README.md`의 **공식 링크**에서 각자 받기(재배포 금지) |
    | `LAW-…` | 무역보험법 · 대외무역법 · 법인세법 시행령 제19조의2 | 국가법령정보센터(law.go.kr) 조문을 복사해 텍스트로 |

    - 조항 ID 예: `KS-7①2`(제7조 제1항 제2호) · `HB-27②`. 검색 지표(P@K · R@K · F1@K · Hit@3)는 **조 단위**로 맞춥니다 — `KS-21②` → `KS-21`.
    - ICC UCP 600 · ISBP 원문은 넣지 않습니다(AI 학습 · 텍스트 마이닝 금지) — 골든셋의 기권 문항으로만 나옵니다.

---

## Step 1 기준선 — Gemini Notebook {#step1}

**13:10–13:25 (15분)** · 코드 0줄 RAG로 '기준선' 점수를 잰다

=== "🟢 Basic"

    **① 평가 시트 준비 (짝 중 한 사람)**

    1. `rag/eval_sheet_template.xlsx`를 Google Drive에 올리고 → 파일을 마우스 오른쪽 → **연결 앱** → **Google Sheets**로 엽니다. **공유** → 짝의 Google 계정을 편집자로 추가합니다.
    2. `README` 탭을 읽습니다. **노란 칸만 입력**하고 회색 칸(수식)은 고치지 않습니다. `eval` 탭에 골든셋 20문항(q_id · 질문 · 정답 조항 · 유형)이 이미 들어 있습니다.

    **② 노트북 만들기 · 소스 3종**

    3. 개인 Google 계정으로 Gemini Notebook에 들어가 **새 노트북**을 만들고, 이름을 `한빛_기준선_T조-번호`로 바꿉니다.
    4. **소스 추가**: ① K-SURE 약관 PDF(공식 링크에서 받은 파일) ② `hanbit_credit_policy.md` ③ law.go.kr 조문을 복사해 **복사한 텍스트**로 추가.

    **③ 골든셋 10문항 — 인용을 눌러 확인**

    5. 짝과 나눠(나: Q01–Q10 / 짝: Q11–Q20) 질문을 **번호 순서대로** 채팅에 넣습니다.
    6. 답마다 **인용 번호**를 눌러 근거 문단이 정말 그 말을 하는지 봅니다.
    7. `eval` 탭 **S–U열**(gemini_answer_ok · gemini_cite_ok · gemini_abstain_ok)에 0/1을 적습니다. 정답 기준은 `goldset` 탭의 expected_answer · grading_rubric입니다. 애매하면 짝과 합의합니다.
    8. 기권 문항(유형 '함정')에서 추측으로 답하면 그것이 **환각** 사례입니다 — 메모에 한 줄 남깁니다. 사용 한도에 걸리면 짝의 노트북으로 이어 합니다.

=== "🔵 Standard"

    Basic과 같습니다. 남는 시간에 같은 질문 2개를 **질문 끝에 `근거 조항 번호와 함께 답해 줘`**를 붙여 다시 묻고, 인용 형식이 달라지는지 봅니다.

=== "🟣 Challenge"

    Colab에서 `d5_rag_eval.ipynb`를 열고 첫 칸(버전 출력)을 실행해 둡니다. Step 4에서 같은 지표를 코드로 재현합니다.

---

## Step 2 지식베이스 · 청킹 — Dify {#step2}

**13:25–13:50 (25분)** · 조항 단위 청킹 + Hybrid + Rerank로 '찾는 힘'을 높인다

=== "🟢 Basic"

    **① 지식베이스 3개**

    1. cloud.dify.ai에 로그인 → 위쪽 **Knowledge** → **Create Knowledge** → **Import from file**.
    2. 지식베이스를 문서별로 3개 만듭니다 — `hanbit_policy`(`hanbit_credit_policy.md`) · `ksure_terms`(약관 PDF, 또는 강사가 강의장 드라이브로 나눠 준 조문 변환본 — 재배포 금지) · `laws`(law.go.kr 조문 텍스트).

    **② Chunk Settings — 부모 = 조, 자식 = 항 · 호**

    3. **Chunk mode**: **Parent-child**
        - **Parent chunk**: **Paragraph** · Delimiter `\n\n` · Maximum chunk length **1,000** tokens [교육용 가정]
        - **Child chunk**: Delimiter `\n` · Maximum chunk length **200** tokens [교육용 가정]
    4. **Text preprocessing rules** 두 개를 **끕니다** — "Replace consecutive spaces, newlines and tabs" · "Delete all URLs and email addresses"(줄 구조와 조문 속 연락처 · 링크를 지키려고).
    5. **Preview Chunk**를 눌러 **부모 1개 = 조 1개**인지 봅니다(예: 제27조가 부모 1개). 조가 둘로 갈라지면 조 안에 빈 줄이 있는 것입니다.

    **③ Index · Retrieval Setting**

    6. **Index Method**: **High Quality**.
    7. **Retrieval Setting**: **Hybrid Search** → **Rerank Model** 켬 → **Top K** `3` → **Score Threshold** 켬 `0.5`. Dify에서 Top K · Threshold는 **Rerank를 켜야** 적용됩니다.
    8. **Save & Process** → 문서 상태가 **Available**이 될 때까지 기다립니다(휴식 동안 진행돼도 됩니다).

    **④ Retrieval Testing — 상위 조각 보기**

    9. 지식베이스 화면 왼쪽 **Retrieval Testing**(검색 테스트)에서 골든셋 질문 하나(예: 충돌 문항)를 넣고, 상위 조각의 조항 머리(`## 제N조`)를 봅니다. 캡처 1장을 남깁니다.
    10. 막히면 Studio → **Import DSL file** → `hanbit_policy_rag_v1.yml`(파일 표)로 챗봇을 먼저 가져오고, 지식베이스를 다시 연결합니다(지식베이스는 DSL에 들어 있지 않습니다).

=== "🔵 Standard"

    **청킹 · 검색 실험 E1–E4 (각 5문항)**

    | 실험 | 설정 | 기록 |
    |---|---|---|
    | E1 | General 청킹(`\n\n`, 500 tokens) | 평가 시트 `experiments` 탭 |
    | E2 | Parent-child(Basic 기본) | 같은 탭 |
    | E3 | E2 + Top K 5 | 같은 탭 |
    | E4 | E2 + Vector Search만(Hybrid 끔) | 같은 탭 |

    - 같은 5문항으로 Retrieval Testing을 돌려 정답 조항이 몇 위에 나오는지 적고, 어느 설정이 왜 나았는지 한 줄씩 씁니다.
    - **자사 지침**(반출 정책 확인 후 익명화본)을 넣을 때는 **P5-2**로 PDF를 조 단위 Markdown으로 바꾼 뒤 올립니다. 변환본은 공유하지 않습니다.

        ??? example "P5-2 약관 · 지침 PDF → 조문 단위 Markdown — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-2 보기](../prompts/day5.md#p5-2)

            --8<-- "labs/day5/prompts.md:p5-2"

=== "🟣 Challenge"

    Rerank OFF / ON 두 설정의 Retrieval Testing 상위 5개를 같은 5문항으로 기록해 두고, Step 4에서 노트북으로 F1@K 차이를 계산합니다.

---

## Step 3 인용 · 기권 챗봇 {#step3}

**14:00–14:15 (15분)** · 인용 · 기권 · 충돌 표시가 강제된 챗봇을 연다

=== "🟢 Basic"

    1. Dify **Studio** → **Create from Blank** → **Chatbot** → 이름 `한빛 여신규정 도우미`.
    2. **Instructions**(지시문)에 **P5-1**을 붙여 넣습니다. 첫 줄이 '검색된 문서 조각만 근거로 답한다'인지, 기권 문장이 정확히 "제공 문서에서 확인되지 않습니다."인지 봅니다.

        ??? example "P5-1 규정 챗봇 시스템 프롬프트(인용 강제 + 기권) — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-1 보기](../prompts/day5.md#p5-1)

            --8<-- "labs/day5/prompts.md:p5-1"

    3. **Context** → **Add** → Step 2의 지식베이스 3개를 고릅니다.
    4. 모델: Sandbox 크레딧 모델, 또는 설정 → **Model Provider**에서 'OpenAI-API-compatible'로 키 카드의 LiteLLM 주소 + 가상 키 · 모델 `fast-default`.
    5. **Features** → **Citations and Attributions** 켬.
    6. 오른쪽 **Debug & Preview**에서 3문항을 시험합니다 — 정상 문항 2개(답 끝마다 [문서명 제N조]) · 기권 문항 1개(정확히 "제공 문서에서 확인되지 않습니다.").
    7. **Publish** → **Run App** → 주소를 복사해 메모합니다(Step 8의 `links.md`).

=== "🔵 Standard"

    **규정 충돌 미션** — 충돌 문항 2개(Q07 · Q08)를 물어 챗봇이 **두 조항을 모두 인용하고 "[규정 충돌] 담당자 확인 필요"**를 표시하는지 봅니다. 한쪽만 답하면 Top K를 5로 올려 다시 묻습니다. 결과 아래에 '우리 규정을 이렇게 고치자'는 개정안 1문장을 평가 시트 메모에 씁니다 — 6일차 SOP의 근거가 됩니다.

=== "🟣 Challenge"

    **인젝션 시험** — 라이브러리의 시험 문장 IJ-2(질문 속 지시) · IJ-3(문서 속 숨은 문장)을 넣어 봅니다. 아래 표로 기록합니다: 시험 문장 · 넣은 위치 · 모델 반응 · 막은 장치(근거 제한 · 인용 · 승인 · 출력 검증) · 결론 한 줄. 합성 문서에서만 시험합니다.

    ??? example "IJ-2 · IJ-3 인젝션 시험 문장 — 펼쳐서 복사"
        [프롬프트 라이브러리에서 보기](../prompts/day5.md#ij)

        --8<-- "labs/day5/prompts.md:ij-2"

        --8<-- "labs/day5/prompts.md:ij-3"

---

## Step 4 검색 평가 — 조화평균으로 Top-K 고르기 {#step4}

**14:15–14:45 (30분) + 기대값 공개 14:45** · 계획서의 '검색 정확도 평가 — 조화평균 · Top-K 최적화'

=== "🟢 Basic"

    **① 상위 5개 조항 ID 적기 (짝과 10문항씩)**

    1. 내 문항(Q01–Q10 또는 Q11–Q20)마다 Dify **Retrieval Testing**에 질문을 넣고, 상위 5개 조각의 **조항 ID**를 `eval` 탭 **I–M열(r1–r5)**에 순서대로 적습니다 — 조 단위(`HB-27`, `KS-7`).
        - 시간이 모자라면 **F열(first_hit_rank)**에 '정답 조항이 처음 나온 순위(1–5, 없으면 0)'만 적어도 Hit@3 · MRR은 계산됩니다.
    2. 오른쪽 회색 열에 **P@K · R@K · F1@K(K = 1 · 3 · 5)**가 저절로 계산됩니다. 기권(함정) 문항은 검색 지표에서 빠집니다.

    **② K 고르기 — 평균 F1@K가 가장 높은 K**

    3. `summary` 탭의 'Top-K 요약'(K = 1 · 3 · 5의 P · R · F1)과 막대를 봅니다. **평균 F1@K가 가장 높은 K**를 고르고(같으면 작은 K), 이유를 한 줄로 씁니다 — 예: "K를 늘리면 놓침은 줄지만 잡음이 늘어 F1이 떨어졌다".
    4. 고른 K가 Step 2의 Top K(3)와 다르면 지식베이스의 Top K를 바꿔 볼지 메모합니다.

    **③ 답 채점 · 기준선과 비교**

    5. 같은 문항을 Step 3 챗봇에 묻고 **P–R열**(dify_answer_ok · dify_cite_ok · dify_abstain_ok)에 0/1을 적습니다.
    6. `summary` 탭에서 Dify와 Gemini Notebook(기준선)의 정답률 · 인용 정확도 · 기권 정확도를 비교하고, 충돌 2문항에 대한 메모를 적습니다.
    7. **파일** → **다운로드** → **Microsoft Excel(.xlsx)** → `d5_rag_eval__T조-번호.xlsx`로 이름을 바꿔 `D5`에 둡니다.

    !!! success "기대값 공개 14:45–14:50 — 강사 화면으로만"
        강사가 리허설에서 잰 F1@K · 정답률 · 기권 정확도의 **범위**를 보여 줍니다(배포하지 않음). 내 값이 크게 다르면 원인을 한 줄 적습니다 — 대개 조항 ID를 항 단위로 적었거나(조 단위로), 부모 청크가 조와 맞지 않거나, Rerank가 꺼져 있습니다.

=== "🔵 Standard"

    **자사 지침 5문항** — 반출 정책을 확인한 자사 지침 익명화본으로 지식베이스를 하나 더 만들고, 내가 만든 질문 5개(정답 조항을 미리 적어 둔 것)를 같은 방식으로 평가합니다. 무료 소비자 AI에는 넣지 않습니다. 결과는 6일차 개인 기획서 4장(솔루션 구조)의 근거가 됩니다.

=== "🟣 Challenge"

    `d5_rag_eval.ipynb`로 평가 시트의 r1–r5를 읽어 P@K · R@K · F1@K를 다시 계산하고 시트 값과 같은지 확인합니다. Step 2 🟣의 Rerank OFF / ON 기록으로 F1@K 차이를 표로 만듭니다.

---

## 블록 A 완료 기준 {#checkpoint}

14:45에 슬라이드를 다시 띄우고 함께 체크합니다. 다 못 끝내도 괜찮습니다 — 강사 공용 챗봇으로 블록 B에 합류할 수 있습니다.

- [ ] **Step 1** — 기준선 10문항 0/1 기록 · 기권 문항 표시 · 노트북 이름 규칙
- [ ] **Step 2** — 지식베이스 3개 Available · 부모 청크 = 조 · Rerank ON · Retrieval Testing 캡처
- [ ] **Step 3** — 답 끝마다 [문서명 제N조] · 기권 문항 = "제공 문서에서 확인되지 않습니다." · 챗봇 URL
- [ ] **Step 4** — F1@K(K = 1 · 3 · 5) · 선택 K와 이유 · 충돌 2문항 메모 · `d5_rag_eval__T조-번호.xlsx`

## 흔한 오류와 해결 {#troubleshooting}

| # | 증상 | 원인 | 해결 |
|---|---|---|---|
| 1 | Top K · Score Threshold를 바꿔도 결과가 그대로 | Rerank가 꺼져 있다 | Retrieval Setting에서 **Rerank Model** 켬. Sandbox에서 Rerank가 안 되면 강사 공용 앱으로 보고, 상위 5개 기록은 그대로 |
| 2 | 부모 청크 하나에 조가 두 개 들어 있다 · 조가 갈라졌다 | 구분자 · 빈 줄이 문서 구조와 안 맞는다 | Parent `\n\n` · Child `\n` 확인, 전처리 2개 끔. 조 안에 빈 줄이 있으면 문서를 고친다 |
| 3 | 문서가 계속 Indexing | Sandbox 처리 대기 | 휴식 동안 기다립니다. 10분 넘으면 문서를 지우고 다시 올립니다 |
| 4 | 챗봇이 기권 문항에 그럴듯한 답을 만든다 | 지시문이 빠졌거나 Context에 지식베이스가 없다 | Instructions에 P5-1 전체 · Context 연결 확인. 기권 문장은 정확히 한 줄 |
| 5 | 인용이 안 붙는다 | Citations가 꺼져 있다 | **Features** → **Citations and Attributions** 켬 → Publish 다시 |
| 6 | F1@K 칸이 비어 있다 | 조항 ID 형식이 다르다(항까지 적음 · 띄어쓰기) | `HB-27`처럼 조 단위 · 하이픈 · 공백 없이 |
| 7 | Gemini Notebook이 더 받지 않는다 | 사용 한도 | 짝의 노트북으로 이어 하고, 문항 번호를 메모 |
| 8 | 약관 PDF 링크가 열리지 않는다 | 공식 사이트 주소 변경 · 접속 지연 | K-SURE 보험약관 게시판에서 '단기수출보험(선적후)' 17차 개정을 찾습니다. 강의장 드라이브의 사본은 수업 안에서만 |
| 9 | Dify 크레딧이 줄어든다 | Sandbox 메시지 크레딧은 1회성(200개) | Model Provider에 LiteLLM(OpenAI 호환)을 등록해 자체 키로 |
| 10 | Google Sheets 수식이 #NAME? | 엑셀로 열었다 | Drive에서 **Google Sheets로 열기** |

더 많은 증상은 [FAQ·트러블슈팅](../faq.md)에 있습니다.

## 다 했으면 (확장) {#extend}

1. **충돌을 SOP로**: 충돌 2문항의 '규정 개정안 1문장'을 다듬어 두면 6일차 SOP의 근거표가 됩니다.
2. **Hit@3 · MRR 보기**: `summary` 탭의 보조 지표가 F1@K와 같은 K를 가리키는지 봅니다 — 다르면 왜인지 한 줄.
3. **질문 바꿔 보기**: 같은 뜻을 다른 말로 물어(예: '선적을 멈춰야 하나?' ↔ '추가 수출이 보상되나?') 검색 결과가 어떻게 달라지는지 봅니다 — 하이브리드 검색이 왜 필요한지.
4. **앱 ⑥ RAG와 비교**(블록 B 뒤): 배포한 앱의 ⑥ RAG 규정검색 '골든셋 일괄 실행' CSV를 평가 시트 `run_app` 탭 A1에 붙이면 같은 지표가 계산됩니다.

---

다음 → [실습 B · 6–7교시 — 독촉 메일 자동화 파이프라인과 통합 대시보드](lab-b.md)
