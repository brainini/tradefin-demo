# 실습 B · 6–7교시 — 독촉 메일 자동화 파이프라인과 통합 대시보드

!!! abstract "한눈에 보기 — 블록 B (Step 5–8)"
    | 항목 | 내용 |
    |---|---|
    | 목표 | 연체일 × 등급의 **톤을 사람이 먼저 정하고**, 1–4일차가 한 화면에 묶인 **TradeRisk Control Tower를 내 주소로 배포**해 업로드 → 등급 → 한도 → 경보 → 독촉 초안 → **승인** → 감사로그까지 돌린 뒤, **말로 기능 하나를 더하거나**(🟢) **n8n 승인 워크플로**를 붙인다(🔵) |
    | 시간 | **15:00–16:50** (휴식 15:50–16:00) · 6–7교시 |
    | Step | 5 톤 매트릭스 · 6 대시보드 배포 · 7 기능 추가 / 승인 워크플로 · 8 통합 점검(DRY RUN) |
    | 입력 | 과정 저장소 `app/`(Fork) · `d5_start.csv` · LiteLLM 키 카드 · 독촉 템플릿 T0–T4 · 🔵 `TF_AR_Ledger_template.xlsx` · `dunning_workflow_v1.json` |
    | 도구 | GitHub · Streamlit Community Cloud · AI 대화창 · GitHub 웹 편집기 · 🔵 n8n Cloud · Google Sheets · Gmail · 🟣 터미널 · 코딩 에이전트 |
    | 산출물 | 톤 매트릭스 · **앱 URL** · 기능 추가 커밋 링크 · `workbench/day5/spec.md` · `links.md` · 🔵 n8n JSON · `Audit_Log` 캡처 |
    | 프롬프트 | [독촉 템플릿](../prompts/day5.md#dunning) · [P5-4](../prompts/day5.md#p5-4) · [P5-6](../prompts/day5.md#p5-6) · [P5-7](../prompts/day5.md#p5-7) · 🔵 [P5-3](../prompts/day5.md#p5-3) · 8교시 [P5-5](../prompts/day5.md#p5-5) |

!!! quote "교수계획서 원문 — 블록 B"
    o (6~7교시 / 2H) 바이어 연체 조건 및 리스크 등급별 맞춤형 다국어 대금 결제 촉구 영문 메일 자동화 파이프라인 연동 실습

!!! warning "DRY RUN — 메일은 바이어에게 가지 않습니다"
    앱 ⑤와 n8n은 **초안**만 만듭니다. n8n의 승인 요청 메일은 바이어가 아니라 **승인자(나)**에게 가고, 승인하면 Gmail **임시보관함에 초안**이 생길 뿐입니다. 바이어 주소는 자리표시이고, 실습에서는 내 Gmail의 `+` 별칭으로 바꿉니다. 실제 발송은 0건이어야 합니다.

## 시간 {#time}

| 시각 | Step | 하는 일 |
|---|---|---|
| 15:00–15:05 | 블록 B 안내 | Step 카드 · LiteLLM 키 카드 확인 |
| 15:05–15:20 | [Step 5](#step5) | 톤 매트릭스 2 × 4 · 템플릿 번호 · 가드레일 5종 |
| 15:20–15:50 | [Step 6](#step6) | Fork → Community Cloud 배포(Secrets) → 한 바퀴 |
| 15:50–16:00 | 휴식 | 배포 대기 중이면 계속 |
| 16:00–16:05 | [Step 6](#step6) 마무리 | 승인 1건 · 로그 CSV |
| 16:05–16:40 | [Step 7](#step7) | 🟢 기능 카드 1개(명세 → 파일 전체 → 커밋 → 재배포) · 🔵 n8n 승인 워크플로 |
| 16:40–16:50 | [Step 8](#step8) · 기대값 · 확장 | DRY RUN 확인 · `links.md` · 16:40 완료 기준(강사 화면) · 16:45 5.8 확장 |

## 입력 파일 {#files}

--8<-- "docs/_snippets/day5/files_lab-b.md"

---

## Step 5 톤 매트릭스 — 사람이 먼저 정한다 {#step5}

**15:05–15:20 (15분)** · 연체일(7일 · 15일) × 등급(S/A/B/C)의 톤과 템플릿을 사람이 정한다 — 계획서 '정중하거나 강력한 톤앤매너'

=== "🟢 Basic"

    **① 톤 매트릭스 8칸**

    1. `TF_AR_Ledger_template.xlsx`의 `Config` 탭 아래나 종이에 아래 표를 만들고, 칸마다 **톤(정중 / 단호)**과 **템플릿 번호**를 적습니다.

        | 등급 \ 연체 | 7일(7–14일) | 15일(15–29일) |
        |---|---|---|
        | S | | |
        | A | | |
        | B | | |
        | C | | |

    2. 근거는 가상 여신관리규정 **제25조(독촉 단계) · 제26조(독촉 문안 · 발송 승인) · 제27조(선적 보류)**입니다. 공통 규칙을 표 아래에 적습니다 — **D+30 = T3**(전 등급, 최종 통지 + 선적 보류 고지) · **T4 = 사람이 이관을 결정한 건만**(`escalation_approved = Y`) · 파산 · 사기 신호 = 초안 금지(사람 처리) · L/C · 선수금 = 독촉 대상 제외.
    3. **C등급은 한 단계 앞당깁니다** — C등급 7일 칸에 어떤 템플릿을 둘지 정하고 그 칸에 '앞당김' 표시를 합니다.

    **② 템플릿 T0–T4 읽기**

    4. [프롬프트 라이브러리의 독촉 템플릿](../prompts/day5.md#dunning)에서 T1(D+7 정중) · T2(D+15 단호) · T3(D+30 최종 + 선적 보류) · T4(이관 예고) · (선택) T0(D-3 사전 안내)의 단어 상한과 '하지 않을 것'을 읽습니다.
    5. 사고발생통지(결제기일 + 1개월 이내)는 메일이 아니라 **사람이 결정**합니다. 위약금 15/1000은 문구에 쓰지 않습니다(약관 제21조③ 한정).

    **③ 가드레일 5종 체크**

    6. 아래 다섯 가지가 앱 ⑤ · n8n에 들어 있는지 표 옆에 체크합니다 — ① **금지 문구**(법적 조치 · 법원 · 경찰 · 신용평가기관 · 정부기관, 계좌 정보 변경 · 확인 언급) ② **필수 요소**(인보이스 번호 · 금액 · 만기) ③ **길이 상한** ④ **수신자 화이트리스트**(내 Gmail `+` 별칭만) ⑤ **발송 시간창**(수신지 현지 21:00–08:00 차단, 수업은 한국 시각) + Draft-only · 승인 · 감사로그.

        ??? example "금지 문구 목록(정규식) — 펼쳐서 보기"
            --8<-- "labs/day5/prompts.md:dunning-blocklist"

=== "🔵 Standard"

    자사 결제조건 · 독촉 관행으로 칸을 고칩니다(예: 자사는 D+10에 첫 통지, VIP 바이어는 영업 담당이 먼저 전화). 고친 칸마다 '왜'를 한 줄씩 적습니다 — 6일차 SOP의 커뮤니케이션 장이 됩니다.

=== "🟣 Challenge"

    금지 문구 정규식에 **한국어 표현**(예: 법적 조치 · 소송 · 추심)을 더한 판을 만들고, 단어 경계를 지키는지 예문 5개로 시험합니다. 오탐(정상 문장을 막음)이 나오면 정규식을 고칩니다.

---

## Step 6 대시보드 배포 — 내 주소로 {#step6}

<span class="chip chip--f">[기초 F5]</span> **15:20–15:50 · 16:00–16:05 (35분)** · 템플릿 앱을 내 주소로 배포하고 한 바퀴 돌린다 — 계획서의 '[자동 전처리] → [LightGBM 예측 등급 도출] → [여신 한도 재배정 및 조기 경보 팝업] → [맞춤형 영문 독촉 메일 자동 생성]'

=== "🟢 Basic"

    **① Fork**

    1. github.com 로그인 → 과정 저장소 [`brainini/tradefin-ai-2026`](https://github.com/brainini/tradefin-ai-2026) → 오른쪽 위 **Fork** → **Create fork**. 내 계정에 `내아이디/tradefin-ai-2026` 사본이 생깁니다(원본은 그대로).

    **② Community Cloud에 배포**

    2. [share.streamlit.io](https://share.streamlit.io) → **Continue with GitHub** → 권한 허용 → **Create app** → *Deploy a public app from GitHub*.
    3. **Repository** `내아이디/tradefin-ai-2026` · **Branch** `main` · **Main file path** `app/streamlit_app.py` · **App URL** `traderisk-t조-번호`(예: `traderisk-t2-07`).
    4. **Advanced settings** → Python version **3.12** → **Secrets** 칸에 아래를 붙이고, `<…>` 자리에 **키 카드의 주소 · 가상 키**를 넣습니다 → **Save** → **Deploy**(첫 배포 2–5분).

        ```toml
        [llm]
        base_url = "https://<강사 LiteLLM 주소>/v1"
        api_key = "<내 가상 키>"
        default_model = "fast-default"
        fallback_models = ["fast-backup"]
        ```

        - 키는 **Secrets 칸에만** 넣습니다. 포크 저장소도 공개이니 `secrets.toml`을 올리지 않습니다. 키를 비워 두면 앱은 **모의 모드**로 끝까지 돕니다.
        - 견본 전체(`[app]` 칸 포함)는 저장소의 `app/.streamlit/secrets.toml.example`에 있습니다.

    **③ 한 바퀴 — ⓪ → ⑦**

    5. 앱이 열리면 첫 화면 **⓪ 통합 상황판**(KPI 줄 · P1 · P2 경보 · 바이어 표 · 기준일)을 봅니다 — 결정 질문 "오늘 누구에게 선적 · 독촉 · 통지를 해야 하나?".
    6. **① 업로드 · 전처리**: 기본 원장 또는 `d5_start.csv`를 올립니다 → 표기 통일 · 중복 · 빈칸 · 단위 의심 표시 · 연체일 · 독촉 단계 · 통지 기한을 봅니다.
    7. **② 예측 · 등급** → **③ 한도 · 시나리오** → **④ 조기경보**: P1 · P2 경보가 **대화상자**로 뜨면 내용을 읽고 **확인하고 기록**을 누릅니다.
    8. **⑤ 독촉메일**: 바이어 한 곳을 골라 초안을 만들고, 가드레일 결과를 본 뒤 **승인**(또는 반려 + 사유)합니다. 밤에 리허설하면 발송 시간창 때문에 승인이 잠깁니다 — 수업 시간에는 정상입니다.
    9. **⑦ 로그**: 감사로그를 **CSV로 내려받습니다**(Community Cloud 저장 공간은 세션이 끝나면 사라집니다).
    10. 앱 주소를 짝의 휴대폰에서 열어 봅니다 — 열리면 '모두의 앱'입니다. 주소를 메모합니다(Step 8).

=== "🔵 Standard"

    Basic ①–③을 끝낸 뒤, Step 5에서 고친 자사 톤 규칙을 ⑤ 화면의 초안과 비교해 다른 칸을 메모합니다(앱 규칙은 바꾸지 않습니다). Step 7에서 n8n으로 같은 규칙을 다시 만납니다.

=== "🟣 Challenge"

    **내 PC에서 띄우기 — localhost:8501**

    ```bash
    git clone https://github.com/내아이디/tradefin-ai-2026.git && cd tradefin-ai-2026
    python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -r app/requirements.txt
    streamlit run app/streamlit_app.py
    ```

    - 터미널의 `Local URL: http://localhost:8501`과 작업 관리자의 python 프로세스를 확인하고, 터미널을 닫으면 앱이 꺼지는 것을 봅니다([기초 F5](../foundations/f5.md)).
    - 키를 쓰려면 `app/.streamlit/secrets.toml.example`을 `secrets.toml`로 복사해 채웁니다(이 파일은 `.gitignore`가 막습니다).

---

## Step 7 기능 추가 · 승인 워크플로 {#step7}

**16:05–16:40 (35분)** · 말로 기능 하나를 더하고(🟢), 승인이 있는 워크플로를 붙인다(🔵)

=== "🟢 Basic"

    **① 기능 카드 고르기**

    | 카드 | 고칠 파일 | 요청 문장 | 확인(Then) |
    |---|---|---|---|
    | ① | `app/views/p4_alerts.py` | 국가별 연체 금액 막대차트를 추가하고, 막대 색을 OECD 국가등급으로 구분해줘 | 차트가 경보 페이지에 보인다 |
    | ② | `app/views/p3_limits.py` | 금리(+bp), 원/달러 수준, 현지통화 하락률 슬라이더 3개를 추가해서 EL 변화를 적용 전 · 후로 나란히 보여줘 | 슬라이더를 움직이면 EL이 바뀐다 |
    | ③ | `app/views/p5_dunning.py` | 초안 본문에 금지 표현이 있으면 그 단어를 빨간색으로 표시한 미리보기를 초안 아래에 보여줘 | 본문에 금지어를 넣으면 빨간색 |
    | ④ | `app/views/p7_log.py` | 감사로그를 결정(approve · edit · deny · ack)으로 거르는 선택 상자와 결정별 건수 막대차트를 추가해줘 | 반려 1건을 만들고 거른다 |
    | ⑤ | `app/views/p2_score.py` | 직전 기준일보다 등급이 떨어진 바이어만 보는 체크박스를 추가해줘 | 체크하면 등급 하락 바이어만, 건수 표시 |

    - 🟢 권장: ① · ④ · ⑤ · 🔵: ② · ③. 기초 트랙 F1–F6과 헷갈리지 않게 '기능 카드 ①–⑤'라고 부릅니다.

    **② 명세 먼저 — P5-4**

    1. AI 화면에서 **새 채팅** → **P5-4**를 붙이고 카드 번호 · 요청 문장 · 고칠 파일을 넣어 명세 1장을 받습니다.

        ??? example "P5-4 명세 1장(Given/When/Then) — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-4 보기](../prompts/day5.md#p5-4)

            --8<-- "labs/day5/prompts.md:p5-4"

    2. **Then**이 화면에서 확인할 수 있는 문장인지 봅니다('잘 보인다' ✘ → '체크하면 등급 하락 바이어만 남고 건수가 보인다' ✔). 명세를 메모장에 저장해 둡니다(`spec.md`).

    **③ 파일 전체 받기 — P5-6**

    3. 내 포크 저장소에서 고칠 파일을 열고 **Raw** → 전체 복사.
    4. 같은 채팅에 **P5-6**을 붙이고 파일 경로 · 기능 · 명세 · 코드 전체를 넣어 보냅니다. **수정된 파일 전체**와 바꾼 줄의 `# [추가]` · `# [수정]` 주석, '무엇을 바꿨는지 3줄 · 확인 방법 3단계'를 받습니다.

        ??? example "P5-6 앱에 기능 추가(자연어 → 파일 전체) — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-6 보기](../prompts/day5.md#p5-6)

            --8<-- "labs/day5/prompts.md:p5-6"

    5. 답이 "… 이하 동일"처럼 생략했으면 `생략하지 말고 파일 전체를 다시 출력해 줘`라고 보냅니다.

    **④ 웹 편집기로 커밋 → 자동 재배포 → Then 확인**

    6. 포크 저장소의 그 파일에서 연필 아이콘(**Edit this file**) → ++ctrl+a++ → 받은 파일 붙여넣기 → **Commit changes** → 메시지 두 줄(`무엇: 기능 카드 ⑤ 등급 하락 체크박스` / `왜: …`) → 커밋.
    7. 1–2분 뒤 앱이 자동으로 다시 뜹니다. 명세의 **Then**을 배포 주소에서 확인합니다.
    8. 오류 화면이 뜨면 오류 전문과 현재 파일을 **P5-7**에 넣어 '원인 1줄 + 최소 수정 파일 전체'를 받고 다시 커밋합니다. 그래도 안 되면 GitHub **History**에서 이전 커밋으로 되돌립니다.

        ??? example "P5-7 배포 오류 고치기 — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-7 보기](../prompts/day5.md#p5-7)

            --8<-- "labs/day5/prompts.md:p5-7"

=== "🔵 Standard"

    **n8n 승인 워크플로 — 원장 → 단계 분기 → AI 초안 → 가드레일 → 승인 요청 → Gmail 초안 → 감사로그**

    **준비 — Google Sheets 원장**

    1. `TF_AR_Ledger_template.xlsx`를 Google Drive에 올리고 **Google Sheets로 열기** → 파일 이름 `TF_AR_Ledger`.
    2. `Config` 탭: `approver_email` · `test_recipient` = **내 Gmail**, `whitelist_regex`의 `myname` = 내 Gmail 아이디. `as_of`(2026-09-30)는 그대로.
    3. `AR_Ledger` 탭: 맨 오른쪽 `plus_address_helper` 열을 전부 복사 → `contact_email` 열에 **값만 붙여넣기**(++ctrl+shift+v++). 실제 바이어 주소는 절대 넣지 않습니다.

    **가져오기와 연결**

    4. n8n Cloud(14일 체험) → 새 워크플로 → 오른쪽 위 `…` → **Import from File** → `dunning_workflow_v1.json`.
    5. 빨간 표시가 있는 노드에 자격증명 3종을 연결합니다 — **Google Sheets OAuth2**(문서 `TF_AR_Ledger`) · **Gmail OAuth2** · **LLM**(OpenAI 자격증명 → API Key = 내 가상 키, **Base URL = 키 카드의 LiteLLM 주소**, 모델 `fast-default`).
    6. 워크플로 **Settings** → **Timezone = Asia/Seoul**인지 확인.

    **실행 테스트**

    7. **Execute workflow**(수동 실행) → 받은편지함에 `[승인요청]` 메일이 옵니다 → 하나 **승인**, 하나 **반려**, 하나는 그대로 둡니다.
    8. Gmail **임시보관함**에 초안 1개, `Audit_Log` 탭에 approve · deny 행이 생겼는지 확인하고 캡처합니다(주소 가림).
    9. n8n 화면의 `…` → **Download**로 워크플로 JSON을 내려받습니다(제출).

    **페르소나 3종 지시서 — P5-3**

    10. 리스크 감시 · 사내 규정 검색 · 독촉 메일 작성 요원의 STICC 지시서를 P5-3으로 받고, **발송 · 한도 변경 · K-SURE 통지는 어느 역할에도 주지 않았는지** 확인합니다.

        ??? example "P5-3 페르소나 3종 지시서(STICC) — 펼쳐서 복사"
            [프롬프트 라이브러리에서 P5-3 보기](../prompts/day5.md#p5-3)

            --8<-- "labs/day5/prompts.md:p5-3"

    - 막히면: Gmail OAuth '액세스 차단' → 개인 Gmail로 · 모든 행이 '대상 아님' → `due_date`가 날짜 형식인지 · 크레딧 소진 → LiteLLM 자격증명으로. n8n이 시간 안에 안 끝나면 기능 카드(🟢)로 바꿉니다.

=== "🟣 Challenge"

    **코딩 에이전트로 기능 추가 — diff를 직접 읽는다**

    1. 로컬 저장소(Step 6 🟣)에서 코딩 에이전트에게 기능 카드 하나와 P5-4 명세를 주고 구현시킵니다.
    2. **diff를 직접 읽고**, 셀마다 · 함수마다 '무엇을 왜'를 한 줄로 설명할 수 없는 변경은 되돌립니다(이해의 부채).
    3. `python -m pytest app/tests -q`로 앱 시험을 돌린 뒤 commit · push → 배포 주소에서 Then 확인.

---

## Step 8 통합 점검 — DRY RUN {#step8}

**16:40–16:50 (10분)** · 실제 발송 0건을 확인하고 제출 링크를 정리한다

=== "🟢 Basic"

    1. **보낸편지함 0건**(임시보관함에 초안만) · **저장소에 키 0**(포크 저장소에서 `api_key`로 검색)을 확인합니다.
    2. 개인 저장소 `tradefin-my-T{조}-{번호}` → `workbench/day5/` → **Add file** → **Create new file** → 이름 `links.md` → 아래 네 줄을 적고 커밋합니다.

        ```markdown
        - 챗봇(Dify): https://…
        - 기준선 노트북(Gemini Notebook, 보기): https://…
        - 앱: https://traderisk-t조-번호.streamlit.app
        - 기능 추가 커밋: https://github.com/…/commit/…
        ```

    3. 같은 폴더에 `spec.md`(Step 7 명세)를 올립니다. 메시지는 두 줄(무엇 / 왜).

    !!! success "완료 기준 확인 16:40–16:45 — 강사 화면"
        강사가 블록 A · B 완료 기준과 리허설 실행 예시(경보 · 감사로그 · 초안)를 띄웁니다. 아래 [완료 기준](#checkpoint)을 함께 체크합니다.

=== "🔵 Standard"

    **화이트리스트 차단 시험 1건**: `AR_Ledger` 한 행의 `contact_email`을 `test@other.com`으로 바꿔 실행하면 '수신자 차단'이 `Audit_Log`에 남는지 보고, 확인 뒤 **원래대로 되돌립니다**.

=== "🟣 Challenge"

    `links.md`에 로컬 실행 캡처와 push한 커밋 링크를 더하고, 노트북 · 코드의 첫 칸에 버전이 찍히는지 확인합니다.

---

## 블록 B 완료 기준 {#checkpoint}

- [ ] **Step 5** — 톤 매트릭스 8칸(톤 + 템플릿 번호) · C등급 7일 '앞당김' · 가드레일 5종 + Draft-only · 승인 · 감사로그 체크
- [ ] **Step 6** — 앱 URL이 다른 기기에서도 열림 · Secrets에만 키(저장소 키 0) · 경보 대화상자 1회 · 승인 1건 · 로그 CSV
- [ ] **Step 7** — 🟢 기능 1개 커밋 + 배포 주소에서 Then 확인 · 🔵 승인 1 · 반려 1 · 임시보관함 초안 1 · `Audit_Log` 캡처 · n8n JSON
- [ ] **Step 8** — 실제 발송 0건 · `workbench/day5/links.md` · `spec.md`

## 흔한 오류와 해결 {#troubleshooting}

| # | 증상 | 원인 | 해결 |
|---|---|---|---|
| 1 | 배포가 'Main module does not exist' | Main file path 오타 | `app/streamlit_app.py` 그대로(앞에 `/` 없이) |
| 2 | 앱이 모의 모드로만 돈다 | Secrets가 비었거나 `<…>` 자리표시 그대로 | 앱 → **Settings** → **Secrets**에 키 카드 값 넣고 저장 → 재시작 |
| 3 | `AuthenticationError` · 401 | 가상 키 오타 · 만료 · 다른 사람 키 | 키 카드 다시 확인. 노출됐으면 강사에게 알려 예비 키로 |
| 4 | 승인 버튼이 잠겨 있다 | 발송 시간창 밖(현지 21:00–08:00) | 수업 시간에는 열립니다. 밤 리허설은 Secrets `[app]`에 `demo_clock` |
| 5 | 앱이 잠들었다 | 12시간 무접속 | 화면의 **Yes, get this app back up!** |
| 6 | 감사로그가 사라졌다 | Community Cloud 저장 공간은 휘발성 | 세션이 끝나기 전에 ⑦에서 CSV로 받기 |
| 7 | 기능 추가 뒤 앱이 빨간 오류 화면 | 받은 코드가 일부 생략됐거나 이름이 바뀌었다 | P5-7 → 그래도 안 되면 History에서 이전 커밋으로 되돌리기 |
| 8 | AI가 `requirements.txt`를 바꾸라고 한다 | 새 패키지가 필요한 방식으로 짰다 | `새 패키지 없이, 지금 있는 것만으로 다시` — requirements는 바꾸지 않는다 |
| 9 | n8n 승인 요청 메일이 안 온다 | `approver_email`이 자리표시 그대로 · Gmail 자격증명 미연결 | `Config` 탭 확인 · Gmail OAuth 연결 |
| 10 | n8n에서 모든 행이 '대상 아님' | `due_date`가 글자로 들어갔다 | Sheets에서 날짜 형식으로 바꾸기 |
| 11 | 저장소 검색에 키가 나온다 | `secrets.toml`이나 코드에 키를 적어 커밋했다 | 즉시 강사에게 알리고 **키부터 교체** — 파일을 지워도 커밋 이력에 남습니다 |
| 12 | Fork 버튼이 회색 | 이미 같은 이름의 포크가 있다 | 내 계정의 기존 포크를 쓰거나 이름을 바꿔 Fork |

더 많은 증상은 [FAQ·트러블슈팅](../faq.md)에 있습니다.

## 다 했으면 (확장) — 5.8 {#extend}

| 트랙 | 확장 |
|---|---|
| 🔵 Standard · 자사 데이터 | 자사 여신 지침 RAG 5문항(반출 정책 확인 후 익명화본, 무료 소비자 AI 금지) → 기획서 4장 솔루션 구조 · n8n 승인 워크플로를 자사 독촉 관행으로 · 명세 1장 → 기획서 4 · 8장 |
| 🟣 Challenge · 코딩 | `d5_rag_eval.ipynb`로 P@K · R@K · F1@K 재현 · Rerank 비교 · 로컬 `streamlit run` · 코딩 에이전트로 기능 추가(diff 확인) · 금지 문구 정규식을 앱 초안 함수 뒤에 |
| 기초 F5 | 배포 URL · Secrets 점검 · 8교시 팀 저장소 + PR 리뷰 1건 · 내일 솔루션 킷 = 팀 저장소 `v1.0` |

- **오늘 밤 21:00** 개인 기획서 초안(1–6장) 제출 → 내일 09:00 1차 서면 피드백.

## 8교시 — [기초 F5] 팀 저장소 + PR 리뷰 1건 {#period8}

<span class="chip chip--f">[기초 F5]</span> **17:10–17:26 따라 하기(15분)** · 내일 해커톤의 작업대를 깐다

1. **조장**: [`brainini/tradefin-kit-template`](https://github.com/brainini/tradefin-kit-template) → **Use this template** → **Create a new repository** → 이름 `tradefin-kit-T{조}`(예: `tradefin-kit-T2`) · **Public**(가상 데이터만) → **Create repository**.
2. **조장**: 저장소 **Settings** → **Collaborators** → **Add people** → 팀원 GitHub 아이디로 초대.
3. **팀원**: 초대 메일(또는 GitHub 알림 — 종 아이콘)에서 수락 → 저장소의 `README.md` → 연필 아이콘 → **5. 담당자**(팀원) 표에 내 줄 하나(조-번호 · 내일 역할 ①–⑤ · GitHub 아이디, 맡을 일 1줄 — **실명 · 회사명 · 이메일 금지**) → **Commit changes** 창에서 **Create a new branch for this commit and start a pull request** → **Propose changes** → **Create pull request**.
4. **다른 팀원**: PR → **Files changed** → 줄 옆 **+**로 코멘트 1개(P5-5의 [확인] · [질문] · [제안] 중 하나 + 비밀값 · 실명 점검) → **Review changes** → **Approve** → **Submit review** → **Merge pull request**.

    ??? example "P5-5 PR 리뷰 코멘트 — 펼쳐서 복사"
        [프롬프트 라이브러리에서 P5-5 보기](../prompts/day5.md#p5-5)

        --8<-- "labs/day5/prompts.md:p5-5"

- **완료 기준**: 팀 저장소 URL · 팀원 전원 PR 1건 병합 · 리뷰 1건 이상 · 비밀값 · 실명 0. 팀 저장소 구조와 내일 쓰는 법은 [6일차 솔루션 킷](../day6/kit.md)에 있습니다.

---

이전 ← [실습 A · 4–5교시 — 사내 규정 RAG 챗봇](lab-a.md)
