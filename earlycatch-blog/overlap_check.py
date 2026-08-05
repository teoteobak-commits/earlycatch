# -*- coding: utf-8 -*-
"""새 글이 이전 글과 얼마나 겹치는지 검사.

주간 발행에서 제일 큰 위험은 지난주와 거의 같은 글이 나가는 것이다.
검색엔진에 중복·얇은 콘텐츠로 잡히면 SEO와 애드센스 양쪽에 타격이라
발행 전에 반드시 돌린다.

사용법:
    python overlap_check.py drafts/2026-08-12.md
    python overlap_check.py drafts/2026-08-12.md --gaps snapshots/2026-08-12-gaps.json

두 가지를 본다.
  1) 갭 변화  — 지난주 스냅샷 대비 신규/유지/제외된 갭과 수치 변동
  2) 본문 중복 — published/ 안의 이전 글과 문자 5-gram 유사도 + 그대로 반복된 문장

방법론 설명("어떻게 찾나" 절)은 매주 반복되는 게 정상이므로 판정에서 제외한다.
"""
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
PUBLISHED = HERE / "published"
SNAPSHOTS = HERE / "snapshots"

# 매주 반복돼도 괜찮은 절(방법론 등) — 판정에서 제외
BOILERPLATE_HEADINGS = ["어떻게 찾나", "미리 말해둘 것"]


def strip_markup(text: str) -> str:
    text = re.sub(r"^>.*$", "", text, flags=re.M)          # 인용 메타
    text = re.sub(r"^\*\*\[.*?\]\*\*$", "", text, flags=re.M)  # 이미지 표시자
    text = re.sub(r"\[\[IMG-[^\]]*\]\]", "", text)
    text = re.sub(r"[#*`>|\-]", " ", text)
    return text


def sections(text: str) -> dict:
    """H2 기준으로 절을 나눈다. 제목 없는 앞부분은 '(도입)'."""
    out, cur, buf = {}, "(도입)", []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            out[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out[cur] = "\n".join(buf)
    return out


def norm(text: str) -> str:
    text = strip_markup(text)
    text = re.sub(r"[^0-9A-Za-z가-힣]", "", text)
    return text


def shingles(text: str, n: int = 5) -> set:
    t = norm(text)
    return {t[i:i + n] for i in range(max(0, len(t) - n + 1))}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def sentences(text: str) -> list:
    text = strip_markup(text)
    parts = re.split(r"(?<=다\.)\s+|(?<=요\.)\s+|(?<=지\.)\s+|\n", text)
    return [p.strip() for p in parts if len(p.strip()) >= 12]


def content_only(text: str) -> str:
    """방법론 등 반복 허용 절을 뺀 본문."""
    secs = sections(text)
    keep = [v for k, v in secs.items()
            if not any(b in k for b in BOILERPLATE_HEADINGS)]
    return "\n".join(keep)


def compare_gaps(new_path: Path):
    snaps = sorted(SNAPSHOTS.glob("*-gaps.json"))
    if len(snaps) == 0:
        return None, "이전 스냅샷 없음"
    prev_path = snaps[-1]
    if new_path and new_path.resolve() == prev_path.resolve() and len(snaps) >= 2:
        prev_path = snaps[-2]
    try:
        prev = {g["id"]: g for g in json.loads(prev_path.read_text(encoding="utf-8"))["gaps"]}
        cur = {g["id"]: g for g in json.loads(new_path.read_text(encoding="utf-8"))["gaps"]}
    except Exception as e:
        return None, f"스냅샷 읽기 실패: {e}"

    def vph(g):
        ev = g.get("overseasEvidence", {})
        return ev.get("maxVph") or ev.get("maxOutlierMultiple") or 0

    added = [k for k in cur if k not in prev]
    dropped = [k for k in prev if k not in cur]
    kept = []
    for k in cur:
        if k in prev:
            a, b = vph(prev[k]), vph(cur[k])
            pct = ((b - a) / a * 100) if a else 0
            kept.append((cur[k].get("topic", k), a, b, pct))
    return {"prev_file": prev_path.name, "added": [cur[k].get("topic", k) for k in added],
            "dropped": [prev[k].get("topic", k) for k in dropped], "kept": kept}, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("사용법: python overlap_check.py <새글.md> [--gaps <새 스냅샷.json>]")
        return 2
    draft = Path(args[0])
    text = draft.read_text(encoding="utf-8")

    gaps_arg = None
    if "--gaps" in sys.argv:
        gaps_arg = Path(sys.argv[sys.argv.index("--gaps") + 1])

    print(f"\n=== 중복 검사: {draft.name} ===\n")

    # 1) 갭 변화
    new_count = None
    if gaps_arg and gaps_arg.exists():
        diff, err = compare_gaps(gaps_arg)
        if err:
            print(f"[갭 변화] {err}\n")
        else:
            print(f"[갭 변화] {diff['prev_file']} 대비")
            print(f"  신규   : {', '.join(diff['added']) if diff['added'] else '없음'}")
            for topic, a, b, pct in diff["kept"]:
                arrow = "+" if pct >= 0 else ""
                print(f"  유지   : {topic} ({a/10000:.1f}만 -> {b/10000:.1f}만, {arrow}{pct:.0f}%)")
            print(f"  제외됨 : {', '.join(diff['dropped']) if diff['dropped'] else '없음'}")
            new_count = len(diff["added"])
            print()
    else:
        print("[갭 변화] --gaps 인자 없음, 건너뜀\n")

    # 2) 본문 중복
    prior = [p for p in sorted(PUBLISHED.glob("*.md")) if p.name != draft.name]
    if not prior:
        print("[본문 유사도] 비교할 이전 글 없음 (첫 글)\n")
        print("[판정] 발행 가능\n")
        return 0

    body = content_only(text)
    my_sh = shingles(body)
    scored = []
    for p in prior:
        other = content_only(p.read_text(encoding="utf-8"))
        scored.append((jaccard(my_sh, shingles(other)), p, other))
    scored.sort(reverse=True, key=lambda x: x[0])
    top_ratio, top_path, top_text = scored[0]

    print(f"[본문 유사도] 최고 일치: {top_path.name}")
    print(f"  방법론 절 제외 유사도 {top_ratio*100:.0f}%")

    prev_sents = {norm(s) for s in sentences(top_text)}
    repeated = [s for s in sentences(body) if norm(s) in prev_sents]
    if repeated:
        print(f"  그대로 반복되는 문장 {len(repeated)}개:")
        for s in repeated[:6]:
            print(f"    - {s[:60]}")
        if len(repeated) > 6:
            print(f"    ... 외 {len(repeated)-6}개")
    else:
        print("  그대로 반복되는 문장 없음")
    print()

    # 3) 판정
    print("[판정]", end=" ")
    if top_ratio >= 0.5 or (new_count == 0 and top_ratio >= 0.35):
        print("스킵 또는 각도 변경 권장")
        print(f"  이유: 신규 갭 {new_count if new_count is not None else '?'}건 + 본문 {top_ratio*100:.0f}% 중복.")
        print("  같은 리스트를 다시 쓰지 말고 4주 로테이션의 '검증편' 또는")
        print("  '포맷 활용법'으로 전환할 것.")
        rc = 1
    elif top_ratio >= 0.35:
        print("부분 중복 — 겹치는 대목만 고쳐서 발행")
        rc = 0
    else:
        print("충분히 다름 — 발행 가능")
        rc = 0
    print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
