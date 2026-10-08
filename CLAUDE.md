# CLAUDE.md — tradefin-kit-T0

- 데이터: 가상 한빛정밀 데이터만 · 실명 · 이메일 · 키 금지
- 흐름: data/ → app/pipeline/ → out/ → docs/ · sop/ · roi/
- 숫자는 스크립트로 계산, 결과 끝에 검산 3줄
- 한도 변경 · 선적 보류 · 보험 통지 · 바이어 발송 = "승인 필요"만
- 작업 하나 = 이슈 하나 = 브랜치 하나 = PR 하나

## 환경
- 처음 한 번 `uv sync` — `.venv`(Python 3.13)를 `uv.lock` 그대로 만든다. 실행은 `uv run python app/pipeline/…`.
- 그날 파일 받기: `uv run python tools/get_day_files.py 6` (공개 시각마다 다시 실행하면 새로 공개된 파일만 더 온다).

## 우리 팀 규칙
- data/input/ 의 원본은 고치지 않고 out/ 에 새 파일로 쓴다
- 비공개 입력(cards/ · local/ · data/input/v2_demo_open_inv.csv)은 커밋하지 않는다
- 글에는 저장소 기준 상대 경로만 쓴다(홈 폴더 · 절대 경로 금지)
- 비공개 입력 3종은 저장소 관리자에게 받아 같은 이름 · 같은 자리에 둔다

## 팀
- T0-1 · 저장소 관리자 · GitHub 아이디 `brainini` (이 시연 저장소는 1인 팀이다)

## 이 시연 저장소 전용
- 이 저장소에서 '기준 브랜치(main)'는 `d6-kit-t0` 이다. GitHub의 main은 공유 시연 저장소의 다른 시연 몫이라 쓰지 않는다.
  PR 대상 · 릴리스 대상 · `git pull`/`git switch`는 모두 `d6-kit-t0`로 읽는다.
