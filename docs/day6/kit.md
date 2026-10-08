# 6일차 · 솔루션 킷 = 팀 저장소 `v1.0`

!!! abstract "한 줄"
    계획서의 [최종 산출물] **"AI 기반 무역 금융 리스크 관리 통합 파이프라인 솔루션 킷"**을 이 과정에서는 **팀 저장소 하나**로 냅니다.
    처음 보는 사람이 **README만 보고 5분 안에 다시 돌릴 수 있어야** 하고, 제출은 **릴리스 `v1.0`**으로 고정합니다 → [기초 F6](../foundations/f6.md)

!!! quote "계획서 원문 — 6일차 종합 결과물"
    o 6일차 종합 결과물: AI 기반 무역 금융 리스크 관리 통합 파이프라인 솔루션 킷 (SOP 매뉴얼 + ROI 산출서 + 도입 기획서)

| 계획서 결과물 | 킷 안의 자리 | 담당 |
|---|---|---|
| SOP 매뉴얼 | `sop/SOP_{카드}.md` + `sop/ai_usage_rules.md` | ⑤ · ④ |
| ROI 산출서 | `roi/roi_kpi.xlsx`(팀 ROI 3안) | ③ |
| 도입 기획서 | `docs/proposal_team.md`(팀 요약 2쪽) + 개인 자사판 기획서(비공개 폼 → [제출](submit.md#personal)) | ⑤ · 개인 |
| 스트레스 테스트 | `data/` · 등급 변동표 · 한도안 · EL 표 · `docs/decision_log.md` + 7분 데모 | ① – ③ |

## 팀 저장소 만들기 — 5일차 8교시 {#create}

어제 이미 만들었다면 건너뜁니다. 자세한 화면은 [5일차 8교시](../day5/lab-b.md#period8)에 있습니다.

1. **조장**: [`brainini/tradefin-kit-template`](https://github.com/brainini/tradefin-kit-template) → **Use this template** → **Create a new repository** → 이름 `tradefin-kit-T{조}`(예: `tradefin-kit-T2`) · **Public**(가상 데이터만) → **Create repository**.
2. **조장**: **Settings** → **Collaborators** → **Add people** → 팀원 GitHub 아이디로 초대합니다.
3. **팀원**: 초대 메일(또는 GitHub 알림)에서 수락 → `README.md` **5. 담당자** 표에 내 줄(조-번호 · 역할 · GitHub 아이디 — 실명 · 회사명 · 이메일 금지)을 더하는 **PR**을 엽니다.
4. **다른 팀원**: PR을 열어 리뷰 코멘트 1개 이상 → **Approve** → **Merge pull request**.

- 조장이 6일차의 **저장소 관리자**입니다(README · 릴리스 책임, 역할과 겸임).

## 폴더 구조 {#structure}

```text
tradefin-kit-T{조}/
├─ README.md                  5항목: 목적 · 구성 · 실행 방법(재현 절차) · 데이터 출처와 가상 여부 · 담당자
├─ data/                      ① 카드를 반영한 결과(가상 데이터만) · README.md
├─ app/README.md              ② · ⑤ 배포 주소 · 사용한 커밋 · 바꾼 기능 · 막혔을 때 쓴 경로
├─ sop/
│  ├─ SOP_template.md         복사해서 SOP_{카드}.md로(0–10장 + 부록)
│  └─ ai_usage_rules.md       ④ AI 사용 규칙서 1쪽
├─ roi/README.md              ③ roi_kpi.xlsx(팀 ROI 3안)를 이 폴더에
├─ docs/
│  ├─ architecture.md         CP1 A3 설계도 사진 + 역할 표
│  ├─ evidence.md             ④ 근거표(질문 · 답 · 조항 · 원문 인용 · 상태)
│  ├─ decision_log.md         사람이 내린 결정(시각 · 결정 · 근거 · 결정자 · AI 초안 여부 · 대안)
│  ├─ demo_script.md          ⑤ 7분 대본
│  └─ proposal_team.md        ⑤ 팀 도입 기획서 요약 2쪽
├─ .github/
│  ├─ ISSUE_TEMPLATE/         role.md(역할 이슈) · bug.md(버그 · 불일치 — 디버깅 4요소)
│  └─ PULL_REQUEST_TEMPLATE.md  무엇 · 왜 · 관련 이슈 · 올리기 전 확인 5
├─ .gitignore                 secrets.toml · .env · private/ 를 막는다(웹 업로드는 못 막는다)
└─ secrets.toml.example       값 없는 견본 — 진짜 키는 Streamlit Secrets 칸에만
```

| 경로 | 오늘 채울 것 | 담당 | 언제 |
|---|---|---|---|
| `README.md` | 5항목 + 위기 카드 요약 · 데모 링크 · 릴리스 | 저장소 관리자 | 골격 CP1 → 완성 CP4 |
| `data/` | `d6_{카드}_scored.csv` · `d6_{카드}_open_inv.csv` · `change_log.csv`(예: 카드 ② → `d6_2_scored.csv`) | ① 데이터 | CP2 |
| `app/README.md` | 배포 주소 `traderisk-t{조}-{번호}.streamlit.app` · 사용한 커밋 · 이번 카드에 쓴 화면 · 쓴 경로(앱 / 엑셀 근사) | ② · ⑤ | CP4 |
| `sop/` | `SOP_{카드}.md`(CP3 0–6장 → CP4 0–10장, P6-1 → P6-2 검증 이력) · `ai_usage_rules.md` | ⑤ · ④ | CP3 · CP4 |
| `roi/` | `roi_kpi.xlsx`(보수 · 기준 · 낙관, 도구비 시나리오) | ③ | CP3 |
| `docs/` | `architecture.md` · `evidence.md` · `decision_log.md` · `demo_script.md` · `proposal_team.md` | ⑤ · ④ | CP1 – CP4 |
| Releases | `v0.5`(CP2) · `v1.0`(15:50 제출) + 릴리스 노트(P6-3) | 저장소 관리자 | CP2 · CP4 |

- 개인 도입 기획서 · 개인 ROI 시트 · 사후 진단은 **저장소에 올리지 않습니다** — 비공개 폼으로 냅니다 → [제출](submit.md#personal).

<div class="img-slot" markdown>
**그림 6.3.1-1 (이미지 준비 중)** · 팀 저장소(킷 템플릿) 첫 화면 — 파일 목록(README · data · app · sop · roi · docs · .github)과 README 5항목 제목 — 출처: 강사 시연 화면 · GitHub(가상 데이터) · 슬라이드 #09
</div>

## README 5항목 — 심사 기준 ③ {#readme}

| 항목 | 무엇을 쓰나 | 예(형식만) |
|---|---|---|
| 1. 목적 | 카드 번호 · 제목 · 한 줄 요약(상황 · 트리거 · 영향 숫자 1개) · 답한 질문 · 반영한 인젝트 | "카드 ② — 대상 바이어 n곳의 EL이 S0 대비 □배(출처: `data/…`)" |
| 2. 구성 | 폴더마다 무엇이 있고 누가 맡았나(템플릿 표를 채운다) | `data/` — 카드 반영 결과 · ① |
| 3. 실행 방법(재현 절차) | **3–5줄** — 어떤 파일로 → 무엇을 누르면 → 무엇이 나오나 + 사용한 경로 | "`data/d6_2_open_inv.csv` → 앱 ① 업로드 → ② 예측 · 등급 → 점수표 CSV" |
| 4. 데이터 출처와 가상 여부 | 파일 · 출처 · 가상 여부 + 보안 점검 확인 시각 · 확인한 사람 | `data/…` — 과정 데이터 팩 · 가상 |
| 5. 담당자 | 조-번호 · 역할 · GitHub 아이디 | `T2-07` · ③ · `@아이디` |

- **재현 절차**는 남이 5분 안에 같은 결과를 내는 절차서입니다. '저장소 소개 글'이 아닙니다.
- 체크포인트에 못 미쳐 강사 정답본으로 합류했다면 3번 '사용한 경로'에 그대로 적습니다 — 감점하지 않습니다.
- 숫자 예의 □ · n은 자리표시입니다. 팀의 실제 결과로 채웁니다.

## 이렇게 일합니다 — 이슈 → PR → 릴리스 {#workflow}

| 단계 | 언제 | 하는 일 |
|---|---|---|
| 이슈로 나누기 | 09:25 B1 직후 | 역할 ①–⑤마다 이슈 1개(양식 **역할 (해커톤)**): 미션 · 받는 것 → 넘길 것 · 넘길 시각 · 사람이 결정할 항목 · 완료 체크 · 코칭 대행자 |
| 설계도 | 10:00–10:50 | A3 캔버스(가동 8단계 × 역할 × 입력 × 넘길 산출물 × 시각) 사진 → `docs/architecture.md` · README 골격 = **CP1** |
| 조각 합치기 | 하루 내내 | SOP · README · `data/`처럼 큰 변경은 **PR**로 올리고 다른 팀원 1명이 보고 병합. 오탈자는 바로 커밋해도 됩니다 |
| 중간 고정 | 11:45–12:00 | 태그 `v0.5`(재등급 · 한도 결과, 인젝트 I-1 반영 여부) = **CP2** |
| 사람 결정 기록 | 13:15 이후 | 인젝트 I-2의 결정 · 근거 · 결정자를 `docs/decision_log.md`에 |
| 최종 고정 | 15:40–15:50 | 코드 프리즈 → README 5항목 · 보안 점검 → **`v1.0` 릴리스** + 릴리스 노트 = **CP4** |

**웹에서 PR 올리기**: 파일 → 연필 아이콘 → 고친 뒤 **Commit changes** 창에서 **Create a new branch for this commit and start a pull request** → **Propose changes** → PR 양식(무엇을 바꿨나 · 왜 · 관련 이슈 `closes #번호` · 올리기 전 확인 5) → **Create pull request** → 리뷰어 1명이 **Files changed**에서 확인 → **Merge pull request**.

## 스트레스 테스트를 킷에 남기는 법 {#stress-test}

스트레스 테스트 = 극단적이지만 있을 법한 충격으로 **어디가 먼저 깨지는지** 보는 것입니다. 킷에는 그 흐름이 파일로 남아야 합니다.

| 흐름 | 남는 곳 |
|---|---|
| 카드 → 바뀐 데이터 | `data/d6_{카드}_scored.csv` · `d6_{카드}_open_inv.csv` · `change_log.csv` |
| 바뀐 등급 · 한도 · EL | 등급 변동표 · 한도 변경안 · EL 표(S0 vs 카드 시나리오) — `data/` 또는 `docs/` |
| 먼저 깨진 곳과 사람 결정 | `docs/decision_log.md` · 인젝트 대응 기록 |
| 대응 절차 | `sop/SOP_{카드}.md` |
| 도입 효과 | `roi/roi_kpi.xlsx` · `docs/proposal_team.md` |

<div class="img-slot" markdown>
**그림 6.3.1-2 (이미지 준비 중)** · 충격 × 단계 — 시나리오(S0 · 경미 · 중간 · 심각 · 극단) × 가동 8단계에서 어디가 먼저 깨지나(위치는 가상 예시) — 출처: 자체 작성
</div>

## 보안 점검 — CP4 전에 꼭 {#security}

**3검색**: 저장소 위쪽 검색창(키보드 `/`)에 아래 세 가지를 차례로 넣고 **이 저장소** 결과가 0건인지 봅니다. 결과가 늦게 뜨면 파일을 직접 열어 확인합니다.

| # | 검색어 | 기준 |
|---|---|---|
| 1 | 키 · 비밀값 — `sk-` · `AIza` · `ghp_` · `secrets`, 파일 목록에 `secrets.toml` · `.env`가 없는지 | 0건 |
| 2 | 실명 · 회사명 — 팀원 실명 · 자사 이름 · 실제 거래처 이름 | 0건 |
| 3 | 이메일 — `@`를 찾아 가상 주소(`example.com` · `.example`)만 있는지 | 실제 주소 0건 |

🟣 내 PC에 clone했다면 `git grep -nIE "sk-|AIza|ghp_|@"`로 한 번에 봅니다.

- [ ] 3검색 모두 0건
- [ ] `data/`에는 가상 한빛정밀 데이터만 있다(회사 실데이터 · 익명화본도 올리지 않는다)
- [ ] **Settings** → **Collaborators**: 우리 팀원과 강사 계정뿐이다
- [ ] 키가 한 번이라도 노출됐다면 이미 **교체**했다(파일을 지워도 커밋 이력에 남는다)
- [ ] AI 사용 규칙서 `sop/ai_usage_rules.md`가 있다

## 릴리스 `v0.5` · `v1.0` 만들기 {#release}

1. 저장소 첫 화면 오른쪽 **Releases** → **Draft a new release**(처음이면 **Create a new release**).
2. **Choose a tag** 칸에 `v1.0`을 입력 → **Create new tag: v1.0 on publish**. 대상(Target)은 `main`.
3. **Release title**: `v1.0 — {카드 제목} 솔루션 킷`.
4. 설명 칸에 릴리스 노트를 붙입니다. 초안은 [P6-3](../prompts/day6.md#p6-3)(커밋 목록 · README · 폴더 목록을 넣는다)으로 받고 사람이 고칩니다 — 6절: 이 릴리스에 든 것 · 다시 돌리는 법 · 데이터 · 사람이 승인하는 지점 · 알려진 한계 · 확인 필요 · v0.5 → v1.0 바뀐 것.
5. `v0.5`는 **Set as a pre-release**, `v1.0`은 **Set as the latest release**를 고릅니다.
6. **Publish release** → 주소 `https://github.com/{아이디}/tradefin-kit-T{조}/releases/tag/v1.0`을 복사해 [제출 폼](submit.md#team)에 붙입니다.
7. 15:50 이후에 고친 것은 `v1.1`로 새 릴리스를 만듭니다. 심사는 `v1.0` 기준입니다.

- 커밋 = 세이브 포인트, 태그 = 이름 붙인 세이브 포인트, 릴리스 = 태그 + 설명 + 첨부입니다.

<div class="img-slot" markdown>
**그림 6.9-1 (이미지 준비 중)** · `v1.0` 릴리스 만들기 — Draft a new release 화면의 태그 `v1.0` · 대상 `main` · 제목 · 노트 칸 — 출처: 강사 시연 화면 · GitHub · 슬라이드 #26
</div>

<div class="img-slot" markdown>
**그림 6.3.1-3 (이미지 준비 중)** · 릴리스 = 이름 붙인 고정 시점 — Releases 목록의 `v0.5` · `v1.0` — 출처: 강사 시연 화면 · GitHub · 슬라이드 #11
</div>

## 7분 데모 구성 {#demo}

| 시간 | 내용 | 보여 줄 곳 |
|---|---|---|
| 0:00–0:40 | **위기 요약** — 상황 · 트리거 · 영향 숫자 1개(결론 먼저) | README 1번 |
| 0:40–3:00 | **라이브 데모** — 데이터 갱신 → 재등급 → 한도 · EL → 경보 → RAG 근거 → 독촉 초안(DRY RUN) | 앱 · 워크북 · 챗봇 |
| 3:00–4:30 | **SOP 핵심**(T+0 … T+1주, 사람 승인 지점) + 인젝트 대응 | `sop/SOP_{카드}.md` · `decision_log.md` |
| 4:30–5:45 | **ROI · KPI** — 보수안부터, 재무 AI ROI 중앙값 10%와 비교 | `roi/roi_kpi.xlsx` |
| 5:45–6:30 | **솔루션 킷** — README 재현 절차 · 릴리스 | 저장소 · Releases |
| 6:30–7:00 | **도입 첫 30일과 요청 사항** | `proposal_team.md` |
| 질의응답 3분 | 심사위원 2문 + 청중 1문 — 숫자와 근거 파일로 답한다 | 근거표 · 파일 |

- **6:30 노란 카드, 7:00 컷**. 팀원 전원이 한 번 이상 말합니다.
- 대본은 [P6-4](../prompts/day6.md#p6-4)로 받아 `docs/demo_script.md`에 둡니다. 라이브가 실패하면 **60초 녹화 · 캡처**로 바로 바꿉니다(영상은 발표 PC로 옮기고 저장소에는 올리지 않습니다).
- 발표 순서는 15:45에 추첨하고, 16:05부터 10분 간격(데모 7분 + 질의응답 3분)으로 진행합니다.

## 킷 체크리스트 — CP4 15:40 {#checklist}

- [ ] README 5항목(목적 · 구성 · 실행 방법 · 데이터 출처와 가상 여부 · 담당자)
- [ ] 폴더 6개가 제자리(README · data · app · sop · roi · docs)
- [ ] `data/` — `d6_{카드}_scored.csv` · `d6_{카드}_open_inv.csv` · `change_log.csv`
- [ ] `sop/` — `SOP_{카드}.md` 0–10장(P6-2 검증 반영) · `ai_usage_rules.md`
- [ ] `roi/` — `roi_kpi.xlsx`(보수안부터 3안)
- [ ] `docs/` — `architecture.md` · `evidence.md` · `decision_log.md` · `demo_script.md` · `proposal_team.md`
- [ ] 역할 이슈 5개 · PR 이력
- [ ] 보안 점검 3검색 0건 · 협업자 확인
- [ ] `v0.5`(CP2) · `v1.0` + 릴리스 노트
- [ ] 팀 밖의 한 사람이 README만 보고 5분 안에 재현했다

## 킷 파일 {#files}

--8<-- "docs/_snippets/day6/files_kit.md"

- SOP 양식은 팀 저장소의 `sop/SOP_template.md`와 같은 내용입니다. 팀 저장소에서는 그 파일을 복사해 씁니다.
- 기획서 양식 `ax_proposal_template.md`는 Word · Google Docs로 옮겨 `.docx`로 냅니다 → [기획서 11장](submit.md#proposal).
