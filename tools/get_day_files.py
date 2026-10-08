#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""그날 수업 파일 받기 — 파이썬 기본 기능만 쓰므로 따로 설치할 것이 없습니다.

사용 (저장소 맨 위 폴더에서 · VS Code 터미널):
    uv run python tools/get_day_files.py 1           # 1일차 파일   (uv run tools/get_day_files.py 1 도 됩니다)
    uv run python tools/get_day_files.py 2           # 2일차 파일 — 아침 공개 뒤에
    uv run python tools/get_day_files.py 2 --list    # 받지 않고 어떤 파일이 있는지만 보기
    uv run python tools/get_day_files.py 2 --force   # 이미 있는 파일도 다시 받아 덮어쓰기

하는 일
  1. 그날 파일 목록을 정합니다 — 내 저장소에 이미 있는 파일 + 과정 저장소(공개)에 올라온 파일.
  2. 내 저장소에 없는 파일은 과정 저장소에서 '같은 경로'로 내려받습니다(예: data/checkpoints/d2_start.xlsx).
     프롬프트의 @경로가 모든 사람에게 같게 됩니다.
  3. data/ 와 labs/ 의 파일은 workbench/dayN/data/ 에도 '작업 사본'으로 둡니다.
     원본(data/, labs/)은 고치지 않고, 고쳐 쓸 파일은 사본에서 다룹니다.
  이미 있는 파일은 덮어쓰지 않습니다(--force 를 줄 때만).

아직 공개되지 않은 날이면 '공개 전'이라고 알려 주고 아무것도 바꾸지 않습니다.
공개 시각이 지난 뒤 같은 명령을 다시 실행하면 됩니다. 하루에 여러 번 공개되는 날은 새로 올라온 파일만 더 받습니다.
막히면 과정 사이트의 '파일 받기' 표에서 직접 내려받을 수 있습니다.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import shutil
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parent.parent

SOURCE_REPO = "brainini/tradefin-ai-2026"  # 과정 저장소(공개). 내 저장소가 아니라 이쪽에서 받는다
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{BRANCH}/"
TREE_URL = f"https://api.github.com/repos/{SOURCE_REPO}/git/trees/{BRANCH}?recursive=1"
SITE_URL = "https://brainini.github.io/tradefin-ai-2026/"
TIMEOUT = 20  # 초
USER_AGENT = "tradefin-get-day-files/1.0"

CK = "data/checkpoints/"

# 일차별 설정
#   date     표시용 날짜
#   when     아직 공개 전일 때 알려 줄 공개 시각
#   marker   이 이름으로 시작하는 파일이 하나라도 있으면 '그날 파일이 공개됐다'고 본다(1일차는 처음부터 공개 = None)
#   prefixes 그날 파일로 보는 경로. 앞부분이 같으면 포함하고, 폴더는 '/'로 끝낸다
#   known    목록을 받지 못했을 때(인터넷 · 요청 한도) 이름으로 직접 받아 볼 대표 파일
DAYS: dict[int, dict] = {
    1: {
        "date": "10/14(수)", "when": "이미 공개돼 있습니다", "marker": None,
        "prefixes": ("data/day1/", "labs/day1/", "data/data_dictionary.xlsx"),
        "known": (
            "data/day1/d1_buyers_raw.xlsx", "data/day1/d1_buyers_raw.csv",
            "data/day1/d1_invoices.xlsx", "data/day1/d1_invoices.csv",
            "data/day1/d1_encoding_test.csv", "data/day1/real_buyers_ratios.csv",
            "data/day1/reports/halden_fictional_annual_report.md", "data/day1/reports/irobot.md",
            "data/data_dictionary.xlsx",
        ),
    },
    2: {
        "date": "10/15(목)", "when": "10/15(목) 아침 08:30", "marker": CK + "d2_",
        "prefixes": (CK + "d2_", CK + "fx_krw_daily.csv", "labs/day2/"),
        "known": (CK + "d2_start.xlsx", CK + "d2_news.csv", CK + "fx_krw_daily.csv",
                  "labs/day2/news_warmup_10.txt", CK + "d2_news_answer.csv"),
    },
    3: {
        "date": "10/16(금)", "when": "10/16(금) 아침 08:30", "marker": CK + "d3_",
        "prefixes": (CK + "d3_", "labs/day3/", "data/external/uci_taiwan_bankruptcy.csv",
                     "data/external/fred_dexkous.csv"),
        "known": (CK + "d3_start_features.csv", CK + "d3_start_scoring.csv", CK + "d3_features_panel.csv",
                  CK + "d3_end_scored.csv"),
    },
    4: {
        "date": "10/19(월)", "when": "10/19(월) 아침 08:30", "marker": CK + "d4_",
        "prefixes": (CK + "d4_", "labs/day4/"),
        "known": (CK + "d4_start_scored.csv", CK + "d4_params.csv", CK + "d4_scenarios.csv",
                  CK + "d4_open_inv.csv", CK + "d4_limit_model.xlsx", CK + "d4_end_limits.xlsx"),
    },
    5: {
        "date": "10/20(화)", "when": "10/20(화) 아침 08:30", "marker": CK + "d5_",
        "prefixes": (CK + "d5_", CK + "d3_start_scoring.csv", CK + "d4_start_scored.csv", CK + "d4_params.csv",
                     CK + "d4_scenarios.csv", "labs/day5/", "rag/", "agents/", "app/sample_data/", "models/"),
        "known": (CK + "d5_start.csv", CK + "d3_start_scoring.csv", CK + "d4_start_scored.csv",
                  CK + "d4_params.csv", CK + "d4_scenarios.csv", "labs/day5/TF_AR_Ledger_template.xlsx",
                  "models/day3_lgbm.pkl", "models/day3_lgbm.txt", "models/feature_list.json",
                  "models/grade_cutoffs.json", "models/metrics.json", "models/model_card.md"),
    },
    6: {
        "date": "10/21(수)", "when": "6일차 아침부터 단계별로 — 시각은 강사가 안내합니다", "marker": CK + "d6_",
        "prefixes": (CK + "d6_", "labs/day6/"),
        "known": (CK + "d6_crisis_pack.xlsx", CK + "d6_card5_stage2.xlsx",
                  *(f"{CK}d6_teams/team_{t:02d}.xlsx" for t in range(1, 6))),
    },
}

IGNORE_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db", "desktop.ini"}
IGNORE_DIRS = {"__pycache__", ".ipynb_checkpoints", "sec_cache", ".git", ".venv"}


class NetError(Exception):
    """인터넷 문제 — 사람이 읽을 이유를 담는다."""


# ---------------------------------------------------------------- 작은 도구들
def say(msg: str = "") -> None:
    print(msg, flush=True)


def ignored(rel: str) -> bool:
    parts = rel.split("/")
    name = parts[-1]
    return (name in IGNORE_NAMES or name.startswith("~$") or name.endswith((".part", ".pyc", ".tmp"))
            or any(d in IGNORE_DIRS for d in parts[:-1]))


def safe(rel: str) -> bool:
    """과정 저장소 목록에서 온 경로가 저장소 안쪽을 가리킬 때만 쓴다."""
    p = PurePosixPath(rel)
    return bool(rel) and not p.is_absolute() and ".." not in p.parts and "\\" not in rel and ":" not in rel


def at(rel: str) -> Path:
    return REPO.joinpath(*rel.split("/"))


def work_name(rel: str) -> str | None:
    """작업 사본 이름 — data/ 와 labs/ 의 파일만 workbench/dayN/data/ 에 둔다."""
    p = rel.split("/")
    if p[0] == "labs" and len(p) >= 3:  # labs/day2/x → x
        return "/".join(p[2:])
    if p[0] == "data":  # data/day1/x · data/checkpoints/x → x,  data/파일 → 파일
        return "/".join(p[2:] if len(p) >= 3 else p[1:])
    return None


def net_reason(err: BaseException) -> str:
    reason = getattr(err, "reason", err)
    if isinstance(reason, ssl.SSLError):
        return "보안 인증서 오류(회사 망의 보안 장비 때문일 수 있습니다)"
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return "응답이 없습니다(시간 초과)"
    return "인터넷에 연결하지 못했습니다"


NET_ERRORS = (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ssl.SSLError,
              http.client.HTTPException)


# ---------------------------------------------------------------- 파일 목록
def local_files(prefixes) -> set[str]:
    """이 저장소 안에서 그날 파일로 보는 경로를 찾는다."""
    found: set[str] = set()
    for pre in prefixes:
        if not pre.endswith("/") and at(pre).is_file():
            found.add(pre)
            continue
        folder = pre.rpartition("/")[0]
        base = at(folder) if folder else REPO
        if not base.is_dir():
            continue
        for f in base.rglob("*"):
            if f.is_file():
                rel = f.relative_to(REPO).as_posix()
                if rel.startswith(pre) and not ignored(rel):
                    found.add(rel)
    return found


def remote_files(prefixes) -> tuple[set[str] | None, str]:
    """과정 저장소(공개)의 파일 목록 중 그날 것. 못 받으면 (None, 이유)."""
    req = urllib.request.Request(TREE_URL, headers={
        "User-Agent": USER_AGENT, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return None, "GitHub 목록 조회가 잠시 막혔습니다(여럿이 동시에 쓰면 그럴 수 있습니다)"
        return None, f"GitHub가 {e.code} 오류를 돌려주었습니다"
    except NET_ERRORS + (ValueError,) as e:
        return None, net_reason(e)
    paths = {t["path"] for t in data.get("tree", []) if t.get("type") == "blob"}
    return {p for p in paths if safe(p) and not ignored(p) and any(p.startswith(x) for x in prefixes)}, ""


def fetch(rel: str, dest: Path) -> bool:
    """과정 저장소에서 rel 을 dest 로 받는다. 아직 없으면(404) False, 인터넷 문제는 NetError."""
    url = RAW_BASE + urllib.parse.quote(rel) + f"?t={int(time.time())}"  # ?t= : 방금 올라온 파일이 캐시에 가려지지 않게
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    try:
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp, open(tmp, "wb") as out:
                shutil.copyfileobj(resp, out)
                want = resp.headers.get("Content-Length")
            if want and want.isdigit() and tmp.stat().st_size != int(want):
                raise NetError("받는 도중 연결이 끊겼습니다")
            os.replace(tmp, dest)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise NetError(f"서버가 {e.code} 오류를 돌려주었습니다") from e
        except NET_ERRORS as e:
            raise NetError(net_reason(e)) from e
    finally:
        if tmp.exists():
            tmp.unlink()


# ---------------------------------------------------------------- 본 작업
def run(day: int, args) -> int:
    cfg = DAYS[day]
    prefixes, marker, known = cfg["prefixes"], cfg["marker"], set(cfg["known"])
    say(f"== {day}일차 파일 받기 ({cfg['date']}) ==")

    # 1) 어떤 파일인가 — 내 저장소에 있는 것 + 과정 저장소에 올라온 것
    local = local_files(prefixes)
    remote: set[str] | None = None
    if args.offline:
        say("(인터넷을 쓰지 않는 모드 — 이 저장소에 있는 파일만 다룹니다)")
        fetchable: set[str] = set()
    else:
        remote, why = remote_files(prefixes)
        if remote is None:
            say(f"(과정 저장소의 파일 목록을 확인하지 못했습니다 — {why}. 대표 파일 이름으로 직접 받아 봅니다)")
            fetchable = known
        else:
            say("과정 저장소(공개)의 파일 목록을 확인했습니다.")
            fetchable = remote
    listing_known = args.offline or remote is not None  # 무엇이 공개됐는지 확실히 안다
    wanted = sorted(local | fetchable)

    def released(files) -> bool:
        return marker is None or any(f.startswith(marker) for f in files)

    if listing_known and not released(wanted):
        return not_released(day, cfg)

    # 2) 내 저장소에 없는 파일을 같은 경로로 받는다
    results: dict[str, str] = {}  # 경로 → new | have | miss | err
    problem = ""
    for rel in wanted:
        can_fetch = rel in fetchable
        if at(rel).is_file() and not (args.force and can_fetch):
            results[rel] = "have"
        elif not can_fetch:
            results[rel] = "miss"
        elif args.list:
            results[rel] = "new"
        else:
            try:
                results[rel] = "new" if fetch(rel, at(rel)) else "miss"
            except NetError as e:
                results[rel], problem = "err", str(e)
            except PermissionError:
                results[rel], problem = "err", "파일을 저장하지 못했습니다(엑셀 등에서 열어 둔 파일이면 닫고 다시 실행하세요)"
            except OSError as e:
                results[rel], problem = "err", f"파일을 저장하지 못했습니다({e.__class__.__name__})"

    have_now = [r for r, s in results.items() if s in ("new", "have")]
    if not listing_known and not args.list and not released(have_now):
        if problem:  # 받아 보려 했으나 인터넷 문제
            say("")
            say(f"{day}일차 파일을 받지 못했습니다 — {problem}.")
            say("인터넷 연결을 확인하고 다시 실행하세요. 계속 안 되면 과정 사이트의 '파일 받기' 표에서 직접 받습니다:")
            say(f"    {SITE_URL}day{day}/index.html")
            return 1
        return not_released(day, cfg)

    # 3) 작업 사본 — workbench/dayN/data/
    wb_root = REPO / "workbench" / f"day{day}" / "data"
    copies: dict[str, str] = {}
    for rel in have_now:
        name = work_name(rel)
        if name is None:
            continue
        dest = wb_root.joinpath(*name.split("/"))
        if dest.exists() and not args.force:
            copies[rel] = "have"
        elif args.list:
            copies[rel] = "new"
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(at(rel), dest)
            copies[rel] = "new"

    # 4) 결과 보고
    label = {"new": "받을 예정" if args.list else "받음", "have": "있음", "miss": "공개 전", "err": "오류"}
    clabel = {"new": "사본 만들 예정" if args.list else "사본 만듦", "have": "사본 있음"}
    for rel in wanted:
        if results[rel] == "miss" and listing_known:
            continue
        tail = f"  ({clabel[copies[rel]]})" if rel in copies else ""
        say(f"  [{label[results[rel]]}] {rel}{tail}")

    def count(d: dict, key: str) -> int:
        return sum(1 for v in d.values() if v == key)

    miss = count(results, "miss") if not listing_known else 0
    say("")
    say(f"요약: {'받을 예정' if args.list else '새로 받음'} {count(results, 'new')}개 · 이미 있음 {count(results, 'have')}개 · "
        f"작업 사본 {'만들 예정' if args.list else '새로 만듦'} {count(copies, 'new')}개 · 사본 이미 있음 {count(copies, 'have')}개"
        + (f" · 아직 공개 전 {miss}개" if miss else "") + (f" · 오류 {count(results, 'err')}개" if count(results, "err") else ""))
    if problem:
        say(f"일부 파일을 받지 못했습니다 — {problem}. 잠시 뒤 같은 명령을 다시 실행하세요.")
    if miss:
        say("공개 전인 파일은 공개 시각이 지난 뒤 같은 명령을 다시 실행하면 받습니다.")
    say("")
    if args.list:
        say("목록만 보았습니다 — 파일은 바꾸지 않았습니다.")
        return 0
    say("다음")
    say(f"  - 원본(data/, labs/)은 고치지 않습니다. 고쳐 쓸 파일은 작업 사본 workbench/day{day}/data/ 에서 다룹니다.")
    say(f"  - 결과 파일은 workbench/day{day}/outputs/ 에 저장합니다.")
    if day >= 2:
        say("  - 하루에 여러 번 공개되는 날은 같은 명령을 다시 실행하면 새로 올라온 파일만 더 받습니다.")
    return 1 if count(results, "err") else 0


def not_released(day: int, cfg: dict) -> int:
    say("")
    say(f"{day}일차 파일은 아직 공개 전입니다. 공개 예정: {cfg['when']}")
    say("공개 시각이 지난 뒤 같은 명령을 다시 실행하세요:")
    say(f"    uv run python tools/get_day_files.py {day}")
    say(f"labs/day{day}/ 의 실습 양식은 이미 저장소에 있으니 미리 열어 봐도 됩니다.")
    say(f"급하면 과정 사이트의 '파일 받기' 표를 확인하세요: {SITE_URL}day{day}/index.html")
    return 0


class Parser(argparse.ArgumentParser):
    def error(self, message: str):  # argparse 기본 영어 안내 대신 한국어로
        say(f"사용법이 맞지 않습니다: {message}")
        say("")
        say("예)  uv run python tools/get_day_files.py 1      (1~6 중 오늘 일차)")
        say("     uv run python tools/get_day_files.py 2 --list")
        raise SystemExit(2)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):  # Windows 터미널에서도 한글이 깨지지 않게
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = Parser(add_help=False)
    ap.add_argument("day", nargs="?")
    ap.add_argument("--list", action="store_true", help="받지 않고 목록만 보기")
    ap.add_argument("--force", action="store_true", help="이미 있는 파일도 다시 받아 덮어쓰기")
    ap.add_argument("--offline", action="store_true", help="인터넷 없이, 이 저장소에 있는 파일만 다루기")
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help or args.day is None:
        say(__doc__)
        return 0 if args.help else 2
    text = str(args.day).lower().replace("day", "").replace("일차", "").strip()
    if not text.isdigit() or int(text) not in DAYS:
        ap.error(f"일차는 1~6 중 하나여야 합니다(입력: {args.day})")
    return run(int(text), args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say("\n중단했습니다. 받다 만 파일은 지워졌으니 같은 명령을 다시 실행하면 됩니다.")
        sys.exit(130)
