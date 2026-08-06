# -*- coding: utf-8 -*-
"""TONE.md 기계 규칙 검사기.

사용법:  python tone_check.py 글_1회차.md
TONE.md의 Mechanics / Banned terms 중 자동 판정 가능한 항목만 검사한다.
문체·구조 판단(분량 비대칭, 훈계조 등)은 사람이 봐야 한다.
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BANNED = [
    # (A) AI 상투구
    "오늘날", "현대 사회", "급변하는",
    "알아보겠습니다", "살펴보겠습니다", "다루겠습니다",
    "결론적으로", "마무리하며", "종합해보면", "정리하면",
    "주목할 필요", "눈여겨볼",
    "라고 할 수 있습니다",
    "아무리 강조해도",
    "핵심은",
    "적극 활용", "도움이 되셨", "도움이 되길",
    "인사이트", "레버리지",
    # (B) 카테고리 클리셰
    "월 300", "월 500", "수익 인증",
    "이것만 알면", "이것만 하면",
    "지금 시작하세요", "늦기 전에",
    "블루오션", "황금 키워드",
    "꿀팁", "총정리", "강추",
    "돈 버는 방법",
    "보장합니다", "무조건", "확실히 됩니다",
    # (C) 톤 위반
    "여러분", "구독자님", "이웃님",
    "했답니다", "하답니다",
    "명심하세요", "기본을 지키",
    "모르시는 분들이 많은데",
    "흙수저", "월급쟁이",
    # (D) 내부 지표 용어 — 도구가 쓰는 말이지 독자가 쓰는 말이 아니다
    "배율", "vph", "VPH",
    "breakout", "브레이크아웃", "아웃라이어", "이상치",
    "트래킹", "트랙쿼리", "추적 쿼리",
    "브레이크아웃 스코어", "돌파 점수",
]

# 우리말로 세는 법 — 주 단위는 숫자로 쓴다 ("두 주 연속" 아니고 "2주 연속")
COUNTER_FIX = {
    "한 주 연속": "1주 연속", "두 주": "2주", "세 주": "3주",
    "네 주": "4주", "다섯 주": "5주", "여섯 주": "6주",
    "두주": "2주", "세주": "3주", "네주": "4주",
}

# 내부 용어를 독자 말로 바꾸는 법 (위반 시 함께 보여준다)
PLAIN = {
    "배율": "'평소보다 N배' 또는 '평소 올리던 영상보다 N배 퍼졌습니다'",
    "vph": "'시간당 조회수'",
    "아웃라이어": "'유독 튄 영상'",
    "이상치": "'유독 튄 영상'",
    "트래킹": "'따라가 봤습니다', '계속 재고 있습니다'",
    "브레이크아웃": "'평소보다 크게 터진'",
}

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⭐✅❌]"
)


def strip_frontmatter(text: str) -> str:
    """제목/카테고리/태그 블록과 이미지 플레이스홀더를 본문에서 제외."""
    text = re.sub(r"^#\s.*$", "", text, flags=re.M)          # H1 제목
    text = re.sub(r"^>\s.*$", "", text, flags=re.M)          # 인용 메타
    text = re.sub(r"^\*\*\[.*?\]\*\*$", "", text, flags=re.M)  # **[이미지.png]**
    text = re.sub(r"^---$", "", text, flags=re.M)
    return text


def extract_title(text: str) -> str:
    """H1 제목. 가장 많이 읽히는 문장이라 낱말 검사에 반드시 포함한다."""
    m = re.search(r"^#\s+(.*)$", text, flags=re.M)
    return m.group(1).strip() if m else ""


def main(path: str) -> int:
    raw = Path(path).read_text(encoding="utf-8")
    body = strip_frontmatter(raw)
    title = extract_title(raw)
    # 구조 검사(문단 길이·볼드 수)는 body 만, 낱말 검사는 제목까지 포함
    words = title + "\n" + body
    problems, notes = [], []

    # 볼드 (글 전체 최대 3회)
    bold = re.findall(r"\*\*(?!\[)(.+?)\*\*", body, flags=re.S)
    if len(bold) > 3:
        problems.append(f"볼드 {len(bold)}회 - 최대 3회")
    else:
        notes.append(f"볼드 {len(bold)}/3")

    # 이모지 금지
    if EMOJI.search(body):
        problems.append(f"이모지 발견: {set(EMOJI.findall(body))}")
    else:
        notes.append("이모지 없음")

    # 느낌표 (최대 1회)
    bang = body.count("!") + body.count("！")
    if bang > 1:
        problems.append(f"느낌표 {bang}회 - 최대 1회")
    else:
        notes.append(f"느낌표 {bang}/1")

    # 말줄임표 금지
    if "..." in body or "…" in body:
        problems.append("말줄임표 사용 - 금지")
    else:
        notes.append("말줄임표 없음")

    # 연속 불릿 3개 이상인 블록은 글당 최대 2회
    runs, run = [], 0
    for line in body.splitlines():
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            run += 1
        else:
            if run >= 3:
                runs.append(run)
            run = 0
    if run >= 3:
        runs.append(run)
    if len(runs) > 2:
        problems.append(f"3개 이상 목록 블록 {len(runs)}개 - 최대 2개")
    else:
        notes.append(f"긴 목록 블록 {len(runs)}/2")

    # 금지어
    hits = sorted({w for w in BANNED if w in words})
    if hits:
        problems.append("금지어: " + ", ".join(hits))
        for w in hits:
            if w.lower() in PLAIN:
                problems.append(f"    '{w}' 대신 {PLAIN[w.lower()]}")
    else:
        notes.append("금지어 없음")

    # 세는 법: 주 단위는 숫자로
    counter_hits = [(k, v) for k, v in COUNTER_FIX.items() if k in words]
    if counter_hits:
        for k, v in counter_hits:
            problems.append(f"'{k}' -> '{v}' (주 단위는 숫자로 씁니다)")
    else:
        notes.append("세는 법 정상")

    # 문단당 문장 수: 대부분 4문장 이하, 5문장까지 허용, 6문장 이상은 위반
    total_paras, over4, over5 = 0, 0, 0
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith("#") or re.match(r"^\s*([-*|]|\d+\.)", p):
            continue
        total_paras += 1
        n = len([s for s in re.split(r"(?<=[.?!])\s+", p) if s.strip()])
        if n > 5:
            over5 += 1
        elif n > 4:
            over4 += 1
    if over5:
        problems.append(f"6문장 이상 문단 {over5}개 - 잘라야 함")
    long_ratio = (over4 + over5) / total_paras * 100 if total_paras else 0
    if long_ratio > 40:
        problems.append(f"긴 문단 비율 {long_ratio:.0f}% - '대부분 4문장 이하' 위반")
    else:
        notes.append(f"문단 길이 정상 (5문장+ {over4 + over5}/{total_paras}, {long_ratio:.0f}%)")

    # 짧은 문장 비율 (리듬)
    sentences = [s.strip() for s in re.split(r"(?<=다\.)\s+|(?<=요\.)\s+", body) if s.strip()]
    short = [s for s in sentences if len(s) <= 15]
    ratio = len(short) / len(sentences) * 100 if sentences else 0
    notes.append(f"15자 이하 짧은 문장 {len(short)}/{len(sentences)} ({ratio:.0f}%)")
    if sentences and ratio < 8:
        problems.append(f"짧은 문장 비율 {ratio:.0f}% - 리듬이 단조로움 (권장 10%+)")

    print(f"\n=== TONE 검사: {path} ===\n")
    for n in notes:
        print(f"  OK   {n}")
    if problems:
        print()
        for p in problems:
            print(f"  FAIL {p}")
        print(f"\n{len(problems)}건 위반\n")
        return 1
    print("\n위반 없음\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "글_1회차.md"))
