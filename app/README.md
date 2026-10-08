# TradeRisk Control Tower — Day5 Streamlit 템플릿

(가상) 한빛정밀(주)의 미결 인보이스 원장으로 **전처리 → 연체확률·등급 → 한도·충격 시나리오 → 조기경보 → 영문 독촉 초안·승인 → 규정 RAG → 감사로그**를 돌리고, 맨 앞 **통합 상황판 한 장**(KPI 줄 · P1·P2 경보 · 바이어 표 · 기준일)으로 묶어 보는 실습용 대시보드입니다.

- 합성 데이터만 씁니다. 실데이터·바이어 실명·담당자 메일은 올리지 않습니다.
- **Draft-only**: 메일을 보내지 않습니다. AI 초안 → 가드레일 → 사람 승인 → 감사로그까지만 합니다.
- LLM 키가 없으면 **모의 모드**로 끝까지 돕니다(템플릿 초안·검색 결과 인용).

## 페이지 — 첫 화면은 ⓪ 통합 상황판

앱을 열면 **⓪ 통합 상황판**이 먼저 뜹니다. 결정 질문 하나 — "오늘 누구에게 선적·독촉·통지를 해야 하나?" — 에 답하는 한 장이고, 위에서 아래로 *요약 숫자 → 경보 → 표 → 근거* 순서입니다(숫자마다 기준일). 나머지 ①~⑦은 그 숫자를 만드는 단계입니다.

| 페이지 | 하는 일 | 입력 파일(저장소 안) |
|---|---|---|
| ⓪ 통합 상황판 | KPI 줄(미결 채권 · 연체 30일+ · P1 · P2 · 통지 기한 D-n · 독촉 초안 대상) → P1·P2 경보 표 → 바이어 표(경보 우선 → 연체 금액 순) → 근거·기준일. 경보 규칙은 ④와 같고, ②를 열면 등급·pd_30d·P4가 점수표 값으로 바뀐다 | 기본 원장 `data/checkpoints/d5_start.csv`(자동 정제) · (있으면) ② 점수표 |
| ① 업로드·전처리 | 날짜·통화·금액 표기 통일, 중복·빈칸·단위 의심 표시, 연체일·독촉 단계·사고통지 기한 계산 | `data/checkpoints/d5_start.csv`(Day5 08:30 공개) · `sample_data/upload_sample.csv` · 내 CSV |
| ② 예측·등급 | Day3 모델로 30일 연체확률(pd_30d) → S/A/B/C, 전월 대비 등급 변화, 상위 기여 3개 | `data/checkpoints/d3_start_scoring.csv` · `models/day3_lgbm.pkl`(.txt) · `feature_list.json` · `grade_cutoffs.json` |
| ③ 한도·시나리오 | 한도 = min(필요한도, 등급 상한, 인수한도 + 자기부담) · (선택) LP 재배정 · S0~S4 충격 기대손실 | (있으면) `d4_start_scored.csv` · `d4_params.csv` · `d4_scenarios.csv` |
| ④ 조기경보 | P1 파산·사기 → P2 선적 보류선·사고발생통지 기한 → P3 조건 변경·한도 사용률·수출통지 → P4 위험 신호(② 점수표가 있을 때). P1·P2는 대화상자 | 원장 + ② 점수표 |
| ⑤ 독촉메일 | D-3 · D+7 · D+15 · D+30 · 이관 사전 통지 영문 초안 → 가드레일 5개 → 승인/반려 → 감사로그, 초안 .txt | `prompts/dunning_v1.md` |
| ⑥ RAG 규정검색 | 가상 여신관리규정 조(條) 단위 검색 + 인용 + 기권(LLM 답은 인용·근거 검사 표시), 골든셋 20문항 일괄 실행(평가 시트용 CSV) | `rag/corpus/` · `rag/goldset_20.csv` · `prompts/rag_system_v1.md` |
| ⑦ 로그 | 감사로그 21필드 CSV, LLM 호출·토큰·추정 비용 | — |

## 1. 내 앱 배포하기 (Streamlit Community Cloud, 약 10분)

1. github.com 로그인 → 과정 저장소 `tradefin-ai-2026` → 오른쪽 위 **Fork** → Create fork.
2. [share.streamlit.io](https://share.streamlit.io) → **Continue with GitHub** → 권한 허용 → **Create app** → *Deploy a public app from GitHub*.
3. Repository = `내아이디/tradefin-ai-2026` · Branch = `main` · Main file path = **`app/streamlit_app.py`** · App URL = `traderisk-t{조}-{번호}`.
4. **Advanced settings** → Python version **3.12** → **Secrets** 칸에 [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)의 내용을 붙여 넣고 `<…>` 자리에 키 카드의 주소·가상 키를 넣는다 → Save → **Deploy**(첫 배포 2~5분).
   - 키를 비워 두면 모의 모드로 뜬다(그래도 모든 페이지가 돈다).
   - 키는 Secrets 칸에만 넣는다. 저장소(포크도 공개)에 `secrets.toml`을 올리지 않는다.
5. 앱에서 ⓪ 통합 상황판(첫 화면) → ① 기본 원장 → ② → ③ → ④(경보 대화상자 '확인하고 기록') → ⑤ 초안 → 승인 → ⑦ 감사로그 CSV 내려받기까지 한 바퀴.

- 의존성은 이 폴더의 `requirements.txt`(전부 `==` 고정)를 쓴다 — Community Cloud는 진입점 폴더의 파일을 먼저 찾는다.
- 12시간 동안 아무도 열지 않으면 앱이 잠든다 → 화면의 **Yes, get this app back up!**.
- Community Cloud 저장 공간은 휘발성 — 감사로그는 세션이 끝나기 전에 ⑦에서 CSV로 받는다.
- 밤에 리허설하면 ⑤ 발송 시간창(현지 08–21시) 검사 때문에 [승인]이 잠긴다. Secrets `[app]`에 `demo_clock = "2026-10-20 15:00"`을 넣으면 그 시각으로 검사한다.

## 2. 내 PC에서 돌리기 (🟣)

```bash
git clone https://github.com/내아이디/tradefin-ai-2026.git && cd tradefin-ai-2026
python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r app/requirements.txt
cp app/.streamlit/secrets.toml.example app/.streamlit/secrets.toml   # (선택) 키 채우기 — 이 파일은 .gitignore
streamlit run app/streamlit_app.py
python -m pip install pytest && python -m pytest app/tests -q          # 모의 모드 끝까지 + 상황판 포함 8페이지 검사(LLM은 가짜 로컬 서버)
```

## 3. 자연어로 기능 하나 추가하기 — 기능 카드 ①–⑤ (7교시)

GitHub에서 고칠 파일을 열어 **Raw** 전체를 복사 → AI 채팅에 아래 **P5-6** + 코드 → 받은 **파일 전체**를 GitHub 웹 편집기(연필 아이콘)에 Ctrl+A → 붙여넣기 → Commit → 1~2분 뒤 앱이 자동으로 다시 뜬다.

| 카드 | 고칠 파일 | 요청 문장 | 난이도 | 확인 |
|---|---|---|---|---|
| ① | `app/views/p4_alerts.py` | "국가별 연체 금액 막대차트를 추가하고, 막대 색을 OECD 국가등급으로 구분해줘" | 🟢 | 차트가 보인다 |
| ② | `app/views/p3_limits.py` | "금리(+bp), 원/달러 수준, 현지통화 하락률 슬라이더 3개를 추가해서 EL 변화를 적용 전·후로 나란히 보여줘" (Day6 🟣로 이어진다) | 🔵 | 슬라이더를 움직이면 EL이 바뀐다 |
| ③ | `app/views/p5_dunning.py` | "초안 본문에 금지 표현이 있으면 그 단어를 빨간색으로 표시한 미리보기를 초안 아래에 보여줘" | 🔵 | 본문에 lawyer를 넣어 시험 |
| ④ | `app/views/p7_log.py` | "감사로그를 decision(approve·edit·deny·ack)으로 거르는 선택 상자와 결정별 건수 막대차트를 추가해줘" | 🟢 | 반려 1건을 만들고 거르기 |
| ⑤ | `app/views/p2_score.py` | "직전 기준일보다 등급이 떨어진 바이어만 보는 체크박스를 추가해줘" (표의 `grade_change = down`) | 🟢 | 걸러진 바이어 수 |

- 템플릿에 이미 있는 것(카드로 다시 만들지 않는다): ⑤ 초안의 한국어 요약 · 승인자 이름 필수 · 반려 사유 드롭다운, ⑦ 날짜가 붙은 감사로그 파일명.

**P5-6 기능 추가(자연어 → 파일 전체)**
```text
아래는 Streamlit 1.64 앱의 {파일 경로} 전체 코드다. 비개발자인 내가 GitHub 웹 편집기에 그대로 붙여넣을 수 있게 '수정된 파일 전체'를 돌려줘.

[추가할 기능]
{위 표의 요청 문장}

[지킬 것]
1. 기존 기능·함수 이름·st.session_state 키를 지우거나 바꾸지 않는다(키 목록은 app/ui.py 맨 위 설명).
2. 새 패키지를 추가하지 않는다(requirements.txt 변경 금지). 꼭 필요하면 코드 대신 먼저 질문한다.
3. API 키·URL을 코드에 쓰지 않는다. 비밀값은 st.secrets만 쓴다.
4. 바꾼 줄에 "# [추가]" 또는 "# [수정]" 주석을 단다.
5. "... 이하 동일"처럼 생략하지 말고 파일 전체를 출력한다.
6. 코드 뒤에 '무엇을 바꿨는지 3줄'과 '앱에서 확인하는 방법 3단계'를 쓴다.

[코드]
{붙여넣기}
```

- 커밋한 뒤 화면이 그대로이거나 `has no attribute` 오류가 나면(특히 `core/`·`ui.py`를 고쳤을 때): 앱 오른쪽 위 ⋮ → **Rerun** → 그래도 같으면 Community Cloud **Manage app → ⋮ → Reboot app**(로컬은 Ctrl+C 뒤 `streamlit run` 다시).

**P5-7 배포 오류 고치기** — 빨간 오류 전문 + 현재 파일 전체를 붙여 "원인 1줄 + 가장 작은 수정으로 고친 파일 전체(requirements·Secrets 문제면 무엇을 어디에 넣을지)"를 요청한다.

🟣 Claude Code·Antigravity: 로컬에서 같은 요청을 저장소 전체 대상으로 하되 "`app/.streamlit/secrets.toml`은 읽지 마라 · 기존 함수 이름 유지 · `python -m pytest app/tests -q` 통과"를 조건으로 준다.

## 4. 구조 (고칠 때 참고)

```text
app/
├─ streamlit_app.py      진입점: st.navigation 8페이지(⓪ 통합 상황판 = 첫 화면 + ①~⑦) + 공통 사이드바(기준일·LLM 사용)
├─ ui.py                 화면 공용(세션 키·캐시·Secrets) — 페이지가 import
├─ views/p0~p7_*.py      화면만(계산은 core/) — p0_overview = 통합 상황판 · 메뉴 순서·이름은 streamlit_app.py의 st.Page 목록
├─ core/                 계산(Streamlit 없이 테스트 가능): clean · model · limits · alerts · overview · dunning · guardrails · rag · llm · audit · data_io
├─ prompts/              독촉 템플릿 T0~T4(dunning_v1.md) · RAG 시스템 프롬프트(rag_system_v1.md) — n8n 워크플로와 같은 원문
├─ sample_data/          upload_sample.csv(표기가 섞인 100행 + 중복 1행)
├─ tests/                pytest — 모의 모드 끝까지 · 가짜 LiteLLM 서버 · AppTest 화면 검사(상황판 포함)
└─ .streamlit/           config.toml · secrets.toml.example
```

- 화면 폴더 이름이 `pages/`가 아닌 이유: 진입점 옆에 `pages/` 폴더가 있으면 Streamlit은 서버가 막 켜진 뒤 `st.navigation`이 한 번 실행되기 전까지 옛 방식(폴더 자동 메뉴)으로 돈다 — 잠든 앱을 페이지 주소(…/p4_alerts)로 깨우면 진입점 없이 그 페이지만 뜬다. 새 페이지(예: Day6 `p8_scenario.py`)는 `views/`에 만들고 `streamlit_app.py`의 목록에 `st.Page("views/p8_scenario.py", title=…)` 한 줄을 더한다.
- LLM 호출은 `core/llm.py` 하나(OpenAI 호환 `/chat/completions`, 429·5xx면 `fallback_models`로 재시도, 다 실패하면 템플릿 초안).
- 가드레일(`core/guardrails.py`) = n8n 가드레일 Code 노드와 같은 규칙: ① 금지 표현(법적 절차·국가기관·위협, 계좌 변경 문구) ② 단계별 필수 요소 ③ 180단어 ④ 수신자 화이트리스트 ⑤ 발송 시간창.
- 모델은 저장소 루트 `models/`를 읽는다(`app/models/`에 복사본이 있으면 그것을 먼저).
