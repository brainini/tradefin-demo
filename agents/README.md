# agents — Day5 에이전트·워크플로 파일

| 파일 | 무엇 | 가져가는 곳 |
|---|---|---|
| [`n8n/dunning_workflow_v1.json`](n8n/dunning_workflow_v1.json) | 독촉 워크플로(스케줄 → Sheets 원장 → 단계 판정 → 사람 처리 분기 → 화이트리스트 → 단계 분기 → AI 초안 5종 → 가드레일 → 발송 시간창 → **검토자에게 승인 요청** → 승인 시 Gmail **초안** → 감사로그 → 원장 갱신 → D+30 에스컬레이션) | n8n Cloud(14일 체험) |
| [`n8n/code/*.js`](n8n/code/) | 위 워크플로의 Code 노드 원문(단계 판정 · 가드레일) — 앱(`app/core/dunning.py`·`guardrails.py`)과 같은 규칙 | (참고·수정용) |
| [`dify/hanbit_policy_rag_v1.yml`](dify/hanbit_policy_rag_v1.yml) | RAG 챗봇(Chatflow) DSL — 지식 검색(조 단위) → 결과 없으면 고정 기권 → LLM(인용 강제·기권·충돌 표시) | Dify Cloud Sandbox |
| [`litellm/config.yaml`](litellm/config.yaml) | LLM 관문 설정 — 별칭 `fast-default` · `fast-backup` · `quality`, 가상 키 예산 표 | 강사 서버(수강생은 키 카드만 받는다) |
| [`litellm/issue_keys.py`](litellm/issue_keys.py) | 가상 키 일괄 발급(강사) — 결과는 저장소 밖에만 | 강사 PC |

> **메일은 바이어에게 가지 않는다.** n8n의 'Send and wait for approval'은 **검토자(Config의 `approver_email` = 나)** 에게 승인 버튼이 달린 메일을 보내는 노드다. 승인하면 Gmail **임시보관함에 초안**만 생긴다(Draft-only). 바이어 주소는 자리표시(`buyer+B017@example.com`)이고, 실습에서는 내 Gmail의 플러스 주소로 바꾼다.

## 1. n8n 독촉 워크플로 (6교시, 약 50분)

**준비 — Google Sheets 원장**
1. `labs/day5/TF_AR_Ledger_template.xlsx`를 Google Drive에 올리고 → 'Google Sheets로 열기' → 이름 `TF_AR_Ledger`.
2. `Config` 탭: `approver_email`·`test_recipient` = 내 Gmail, `whitelist_regex`의 `myname` = 내 Gmail 아이디(예: `^gildong\+B\d{3}@gmail\.com$`). `as_of` = 2026-09-30 그대로.
3. `AR_Ledger` 탭: 맨 오른쪽 `plus_address_helper` 열을 전부 복사 → `contact_email` 열에 **값만 붙여넣기**(Ctrl+Shift+V) → `gildong+B017@gmail.com` 같은 주소가 된다.

**가져오기와 연결**
4. n8n → 새 워크플로 → 오른쪽 위 `…` → **Import from File** → `dunning_workflow_v1.json`.
5. 자격증명 3종을 연결한다(노드를 열면 빨간 표시가 있다).
   - Google Sheets OAuth2 → 노드 4개(`Config 읽기` · `AR_Ledger 읽기` · `감사로그: …` · `원장 갱신`)에서 문서 `TF_AR_Ledger` 선택
   - Gmail OAuth2 → 노드 5개(승인 요청 · 초안 · 내부 알림 3)
   - LLM: `LLM 모델 …` 노드 5개 → OpenAI 자격증명 새로 만들기 → API Key = 내 가상 키, **Base URL = 키 카드의 LiteLLM 주소**(노드 옵션 Base URL에도 같은 주소). 모델 = `fast-default`(Config `model_alias`). Gateway credits를 쓰려면 노드에서 'Use Gateway credits'를 고른다(체험 중 충전 불가).
6. 워크플로 **Settings → Timezone = Asia/Seoul**(가져온 파일에 들어 있다 — 확인만).

**실행 테스트(체크포인트)**
7. **Execute workflow**(수동 실행) → 받은편지함에 `[승인요청]` 메일이 단계별로 온다 → 하나 **승인**, 하나 **반려**, 하나는 그대로 둔다.
8. Gmail 임시보관함에 초안 1개, `Audit_Log`에 approve·deny 행, D+30 승인 건이면 `AR_Ledger.ship_hold = Y`와 `[D+30 에스컬레이션]` 내부 메일.
9. 가드레일 시험: `AR_Ledger` 한 행의 `contact_email`을 `test@other.com`으로 바꾸면 `감사로그: 수신자 차단`, 프롬프트 노드에 "mention legal action"을 넣으면 `감사로그: 금지 문구·요소 차단` — 확인 뒤 되돌린다.

**단계 규칙(앱 ⑤와 같다)**: DM3(D-3~D-1) · D7(D+7~14) · D15(D+15~29, **C등급은 D+7부터 앞당김**) · D30(D+30~44) · PRE(D+30 이후 + `escalation_approved = Y`). 제외: 신용장·선수금, 이미 보낸 단계(`last_dunning_stage`), 파산·사기 신호와 D+45 이후는 **사람 처리**(바이어당 내부 알림 1통). 기준일 2026-09-30 원장으로 돌리면 초안 대상 29건(DM3 9 · D7 1 · D15 16 · D30 3)이 나온다.

**막히면**: Gmail OAuth '액세스 차단' → 개인 Gmail로 · 모든 행이 '대상 아님' → `due_date`가 날짜 형식인지(텍스트면 판정 못 함) · 'credits exhausted' → LiteLLM 자격증명으로 · 승인 응답 필드가 `data.approved`가 아니면 `승인?` IF 노드 왼쪽 값을 실행 결과에 맞게 바꾼다.

## 2. Dify RAG 챗봇 (4~5교시)

1. 지식베이스(Knowledge) 3개를 먼저 만든다 — `hanbit_policy`(`rag/corpus/hanbit_credit_policy.md`) · `ksure_terms`(K-SURE 약관 PDF 또는 P5-2 변환본) · `laws`(law.go.kr 조문 복사). 설정은 [`rag/corpus/README.md`](../rag/corpus/README.md) 2절: **Parent-child**(부모 `\n\n` 1,000 tokens = 조, 자식 `\n` 200 tokens = 항·호) · 전처리 2개 끔 · High Quality · **Hybrid + Rerank 켬 · Top K 3 · Threshold 0.5**.
2. Studio → **Import DSL file** → `dify/hanbit_policy_rag_v1.yml`(버전 경고가 뜨면 계속).
3. `지식 검색(조 단위)` 노드 → 지식베이스 3개 다시 연결 → Rerank 모델 선택(지식베이스는 DSL에 들어가지 않는다).
4. `답변` 노드 모델: 'OpenAI-API-compatible' 공급자(LiteLLM 주소 + 가상 키, 모델 `fast-default`) 또는 Sandbox 크레딧 모델.
5. Features → Citations and Attributions 켜짐 확인 → Debug & Preview에서 3문항 → Publish → Run App.
6. 골든셋 20문항(`rag/goldset_20.csv`)을 돌려 `rag/eval_sheet_template.xlsx`의 `eval` 탭에 순위(F열) 또는 r1~r5와 채점(P~U열)을 적는다.

## 3. LiteLLM 관문 (강사)

- 강사 서버에서 `litellm --config agents/litellm/config.yaml` (환경변수: 공급자 키 3개 · `LITELLM_MASTER_KEY` · `DATABASE_URL`). HTTPS 리버스 프록시(예: Caddy) 뒤에 둔다.
- D-2(10/12) `python agents/litellm/issue_keys.py --out ../instructor/day5/keys/litellm_keys.csv` → QR 카드 인쇄 → Day5 09:00 배부. 시험은 `--test-keys`(T01–T03, 3일).
- 수강생 키는 `fast-*`만, `quality`(Claude Haiku 4.5)는 강사·공용 키만. 모델 ID는 D-3에 콘솔에서 다시 확인한다.
- 앱(`app/`)·n8n·Dify 모두 OpenAI 호환 `/v1/chat/completions`로 부른다 — 공급자를 바꿔도 앱 코드는 그대로다.

## 4. Gemini Notebook 기준선 (4교시 15분)

개인 Google 계정 → 새 노트북 `한빛_기준선_T{조}-{번호}` → 소스: K-SURE 약관 PDF(공식 링크에서 직접 받은 파일) · `hanbit_credit_policy.md` · law.go.kr 조문(복사한 텍스트) → 골든셋을 번호 순서대로(짝과 1~10 / 11~20) → 답마다 인용을 눌러 근거 확인 → 평가 시트 S~U열(answer·cite·abstain). Q19·Q20에서 추측하면 '환각' 사례로 기록한다. 사용 한도에 걸리면 짝의 노트북으로 이어 한다.

## 다시 만들기

`python tools/build_day5_agents.py` — 프롬프트 원문(`app/prompts/dunning_v1.md` · `rag_system_v1.md`)과 Code 노드 원문(`n8n/code/*.js`)으로 n8n JSON·Dify DSL을 다시 만들고, Node.js가 있으면 Code 노드 JS를 실제로 돌려 앱 규칙과 같은지 대조한다.
