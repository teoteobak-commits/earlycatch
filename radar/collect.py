# -*- coding: utf-8 -*-
"""전 세계 화제 레이더 — 여러 공개 소스에서 지금 뜨는 것을 모은다.

한 소스만 보면 그 바닥 얘기고, 여러 소스에 동시에 걸리면 진짜 화제다.
그래서 이 스크립트가 하는 일은 수집보다 **교차 확인**에 가깝다.

사용:
    python radar/collect.py            전체 수집 + 다이제스트 생성
    python radar/collect.py --fast     레딧 빼고 (레딧은 느리다)
    python radar/collect.py --list     소스 목록만 확인

결과:
    radar/data/YYYY-MM-DD.json     원자료
    radar/digest/YYYY-MM-DD.md     읽을 것
"""
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}
ATOM = {"a": "http://www.w3.org/2005/Atom"}

# 레딧은 짧은 간격으로 때리면 429 를 던진다. 60초는 둬야 안전하다.
REDDIT_GAP = 60


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


# ─────────────────────────────────────────────── 소스별 수집기

def from_rss(url, source, kind, limit=15):
    """일반 RSS 2.0 (구글뉴스·BBC·Techmeme·ProductHunt)."""
    root = ET.fromstring(fetch(url))
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        if not title:
            continue
        out.append({
            "source": source, "kind": kind, "title": title,
            "url": (it.findtext("link") or "").strip(),
            "when": (it.findtext("pubDate") or "")[:16],
        })
        if len(out) >= limit:
            break
    return out


def from_atom(url, source, kind, limit=15):
    """일반 Atom 피드 (ProductHunt)."""
    root = ET.fromstring(fetch(url))
    out = []
    for e in root.findall("a:entry", ATOM):
        title = (e.findtext("a:title", "", ATOM) or "").strip()
        if not title:
            continue
        link = e.find("a:link", ATOM)
        out.append({
            "source": source, "kind": kind, "title": title,
            "url": link.get("href") if link is not None else "",
            "when": (e.findtext("a:published", "", ATOM) or "")[:10],
        })
        if len(out) >= limit:
            break
    return out


# 4chan 상설 스레드(제너럴) 패턴 — 매일 같은 제목으로 다시 선다
GENERAL = re.compile(r"^/\w+/", re.I)   # 4chan 관례상 /xxx/ 로 시작하면 상설 스레드다


def from_4chan(board, limit=12):
    """4chan 은 공식 읽기 전용 JSON API 가 있다. 답글 많은 순으로 본다.

    /pol/ 은 넣지 않는다. 극단 정치판이라 화제 신호 대비 잡음이 너무 크다.
    """
    d = json.loads(fetch(f"https://a.4cdn.org/{board}/catalog.json"))
    th = [x for page in d for x in page.get("threads", [])]
    th.sort(key=lambda x: -(x.get("replies") or 0))
    out = []
    for x in th:
        if len(out) >= limit:
            break
        raw = x.get("sub") or x.get("com") or ""
        # /smg/ - Stock Market General 처럼 매일 반복되는 상설 스레드는 그날의 화제가 아니다
        if GENERAL.match(re.sub(r"<[^>]+>", " ", raw).strip()):
            continue
        title = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        title = re.sub(r"\s+", " ", title).strip()
        if len(title) < 5:
            continue
        out.append({
            "source": f"4chan /{board}/", "kind": "커뮤니티", "title": title[:120],
            "url": f"https://boards.4chan.org/{board}/thread/{x.get('no')}",
            "when": "", "score": x.get("replies"),
        })
    return out


def from_lemmy(community, limit=10):
    """레딧 대체재. 커뮤니티를 지정하지 않으면 밈만 올라와서 신호가 안 된다."""
    url = ("https://lemmy.world/api/v3/post/list?sort=TopDay&limit=%d&community_name=%s"
           % (limit, community))
    d = json.loads(fetch(url))
    return [{
        "source": f"Lemmy {community}", "kind": "커뮤니티",
        "title": p["post"]["name"], "url": p["post"].get("url") or "",
        "when": (p["post"].get("published") or "")[:10],
        "score": p["counts"]["score"],
    } for p in d.get("posts", [])[:limit]]


# 공지·안내 글은 화제가 아니다
DEAL = re.compile(r"^\[(네이버|쿠팡|11번가|G마켓|지마켓|옥션|위메프|티몬|SSG|인터파크|알리|아마존|하이마트|롯데|신세계|CJ|GS|홈플러스|이마트)")

NOTICE = re.compile(r"이용\s*안내|공지|이벤트 안내|운영원칙|자료안내|패치 자동설치")


def from_html_titles(url, pattern, source, encoding="utf-8", limit=15):
    """API 가 없는 커뮤니티는 목록 페이지에서 제목만 긁는다.

    본문을 가져오지 않고 제목만 본다. 재배포가 아니라 무엇이 화제인지 세는 용도다.
    """
    h = fetch(url).decode(encoding, "replace")
    out = []
    for m in re.findall(pattern, h, re.S):
        title = html.unescape(re.sub(r"<[^>]+>", " ", m))
        title = re.sub(r"\[\d+\]\s*$", "", title).strip()   # 꼬리 댓글수
        title = re.sub(r"\s+", " ", title)
        if not (4 < len(title) < 80) or NOTICE.search(title) or DEAL.match(title):
            continue
        out.append({"source": source, "kind": "커뮤니티", "title": title,
                    "url": "", "when": ""})
        if len(out) >= limit:
            break
    return out


def from_reddit(path, source, limit=15):
    """레딧은 Atom 이고 JSON API 는 403 이라 RSS 만 쓴다.

    클라우드는 공용 IP 라 남과 한도를 나눠 쓴다. 429 가 나면 한 번 더 기다렸다 재시도한다.
    """
    url = "https://www.reddit.com/" + path
    try:
        raw = fetch(url)
    except urllib.error.HTTPError as e:
        if e.code != 429:
            raise
        time.sleep(90)
        raw = fetch(url)
    root = ET.fromstring(raw)
    out = []
    for e in root.findall("a:entry", ATOM):
        title = (e.findtext("a:title", "", ATOM) or "").strip()
        if not title:
            continue
        cat = e.find("a:category", ATOM)
        link = e.find("a:link", ATOM)
        out.append({
            "source": source, "kind": "커뮤니티", "title": title,
            "url": link.get("href") if link is not None else "",
            "when": (e.findtext("a:updated", "", ATOM) or "")[:10],
            "sub": cat.get("label") if cat is not None else "",
        })
        if len(out) >= limit:
            break
    return out


def from_hn(limit=15):
    """해커뉴스 — 만드는 사람들이 지금 뭘 보고 있나."""
    d = json.loads(fetch("https://hn.algolia.com/api/v1/search?tags=front_page"))
    return [{
        "source": "해커뉴스", "kind": "기술", "title": h.get("title") or "",
        "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
        "when": (h.get("created_at") or "")[:10],
        "score": h.get("points"),
    } for h in d.get("hits", [])[:limit] if h.get("title")]


def from_trends(geo, label, limit=12):
    """구글 트렌드 실시간 인기 검색어. 검색량 추정치가 같이 온다."""
    root = ET.fromstring(fetch(f"https://trends.google.com/trending/rss?geo={geo}"))
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        if not title:
            continue
        traffic = ""
        for ch in it:
            if ch.tag.endswith("approx_traffic"):
                traffic = (ch.text or "").strip()
        out.append({
            "source": f"구글트렌드 {label}", "kind": "검색", "title": title,
            "url": "", "when": "", "traffic": traffic,
        })
        if len(out) >= limit:
            break
    return out


def from_wiki(limit=20):
    """위키백과 조회수 상위 — 전 세계가 지금 뭘 찾아보는가.

    특수문서(메인페이지·검색)는 항상 1위라 의미가 없어서 걸러낸다.
    """
    d = (date.today() - timedelta(days=2)).strftime("%Y/%m/%d")
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
           f"en.wikipedia/all-access/{d}")
    data = json.loads(fetch(url))
    skip = re.compile(r"^(Main_Page|Special:|Wikipedia:|Portal:|-$)")
    out = []
    for a in data["items"][0]["articles"]:
        name = a["article"]
        if skip.match(name):
            continue
        out.append({
            "source": "위키백과 조회수", "kind": "관심", "url": "",
            "title": name.replace("_", " "),
            "when": d.replace("/", "-"), "views": a["views"],
        })
        if len(out) >= limit:
            break
    return out


SOURCES = [
    ("위키백과 조회수", lambda: from_wiki()),
    ("해커뉴스", lambda: from_hn()),
    ("구글트렌드 미국", lambda: from_trends("US", "미국")),
    ("구글트렌드 한국", lambda: from_trends("KR", "한국")),
    ("구글트렌드 영국", lambda: from_trends("GB", "영국")),
    ("구글트렌드 일본", lambda: from_trends("JP", "일본")),
    ("구글뉴스 세계", lambda: from_rss(
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en", "구글뉴스 세계", "뉴스")),
    ("구글뉴스 한국", lambda: from_rss(
        "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko", "구글뉴스 한국", "뉴스")),
    ("BBC 월드", lambda: from_rss(
        "https://feeds.bbci.co.uk/news/world/rss.xml", "BBC 월드", "뉴스")),
    ("Techmeme", lambda: from_rss(
        "https://www.techmeme.com/feed.xml", "Techmeme", "기술")),
    ("ProductHunt", lambda: from_atom(
        "https://www.producthunt.com/feed", "ProductHunt", "신제품")),

    # 익명·투표 기반 커뮤니티 — 화제가 제일 먼저 뜨는 곳
    ("4chan /g/", lambda: from_4chan("g")),
    ("4chan /biz/", lambda: from_4chan("biz")),
    ("4chan /v/", lambda: from_4chan("v")),
    ("Lemmy 기술", lambda: from_lemmy("technology")),
    ("디시 실베", lambda: from_html_titles(
        "https://gall.dcinside.com/board/lists/?id=dcbest",
        r'class="gall_tit[^"]*"[^>]*>\s*<a[^>]*>(.*?)</a>', "디시 실베")),
    ("에펨코리아", lambda: from_html_titles(
        "https://www.fmkorea.com/best", r"<h3[^>]*>(.*?)</h3>", "에펨코리아")),
    ("뽐뿌 인기", lambda: from_html_titles(
        "https://www.ppomppu.co.kr/hot.php",
        r'<a href="[^"]*view\.php[^"]*"[^>]*>(.*?)</a>', "뽐뿌 인기", encoding="euc-kr")),
]

REDDIT_FEEDS = [
    ("r/all/top/.rss?t=day", "레딧 전체"),
    ("r/OutOfTheLoop/hot/.rss", "레딧 무슨일이야"),
    ("r/worldnews/top/.rss?t=day", "레딧 세계뉴스"),
]


# ─────────────────────────────────────────────── 교차 신호

# 구글뉴스는 BBC 기사를 실어 나른다. 같은 계열끼리 겹친 건 같은 기사를 두 번 센 것뿐이라
# 독립 확인이 아니다. 계열이 다를 때만 신호로 친다.
FAMILY = {
    "BBC 월드": "뉴스", "구글뉴스 세계": "뉴스", "구글뉴스 한국": "뉴스",
    "해커뉴스": "기술", "Techmeme": "기술",
    "구글트렌드 미국": "검색", "구글트렌드 한국": "검색",
    "구글트렌드 영국": "검색", "구글트렌드 일본": "검색",
    "위키백과 조회수": "관심",
    "ProductHunt": "신제품",
    "레딧 전체": "커뮤니티(서구)", "레딧 무슨일이야": "커뮤니티(서구)",
    "레딧 세계뉴스": "커뮤니티(서구)",
    "4chan /g/": "커뮤니티(서구)", "4chan /biz/": "커뮤니티(서구)",
    "4chan /v/": "커뮤니티(서구)", "Lemmy technology": "커뮤니티(서구)",
    "디시 실베": "커뮤니티(한국)", "에펨코리아": "커뮤니티(한국)",
    "뽐뿌 인기": "커뮤니티(한국)",
}

# 매체 이름은 제목 꼬리표로 붙을 뿐이라 화제가 아니다
PUBLISHERS = set("""BBC CNN Reuters Bloomberg Guardian Times Post News Al Jazeera NPR
AP Yahoo Forbes Wired Verge TechCrunch Engadget Axios Politico Newsweek CNBC
연합뉴스 뉴시스 조선일보 중앙일보 한겨레 경향신문 매일경제 한국경제 서울신문 동아일보""".split())

STOP = set("""the a an and or but for of to in on at by with from as is are was were be been
this that these those it its his her their our your my he she they we you i not no if then
than so such can could will would should may might must do does did have has had here there
what which who whom when where why how all any both each few more most other some only own
same too very just now new news says say said after before over under about into up down out
off again once during while because until against among between through above below
그리고 그러나 하지만 그런데 이제 지금 오늘 내일 어제 우리 저희 관련 대한 위해 통해 대해
""".split())


def key_terms(title):
    """제목에서 비교 가능한 낱말을 뽑는다. 영문은 대문자 고유명사 위주, 한글은 2자 이상."""
    terms = set()
    for m in re.findall(r"[A-Z][a-zA-Z0-9'’\-]{2,}(?:\s+[A-Z][a-zA-Z0-9'’\-]{2,})?", title):
        w = m.strip()
        if w.lower() not in STOP and len(w) > 2:
            terms.add(w)
    for m in re.findall(r"[가-힣]{2,}", title):
        if m not in STOP and len(m) >= 2:
            terms.add(m)
    return terms


def history_streak(term, days=7):
    """이 낱말이 최근 며칠 동안 며칠이나 걸렸는지 센다.

    하루 반짝인지 계속 오르는지는 이걸로만 갈린다. 하루치 목록은
    "오늘 뭐가 시끄럽나"까지고, 그 이상은 누적이 있어야 나온다.
    """
    hit = []
    for f in sorted((ROOT / "data").glob("*.json"), reverse=True)[:days]:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if any(term in it.get("title", "") for it in d.get("items", [])):
            hit.append(f.stem)
    return sorted(hit)


def cross_signals(items, min_families=2):
    """서로 다른 *계열* 몇 곳에 같은 낱말이 걸렸는지 센다."""
    hits = defaultdict(lambda: {"fams": set(), "srcs": set(), "titles": []})
    for it in items:
        fam = FAMILY.get(it["source"], it["source"])
        for term in key_terms(it["title"]):
            if term in PUBLISHERS:
                continue
            h = hits[term]
            h["fams"].add(fam)
            h["srcs"].add(it["source"])
            if len(h["titles"]) < 4:
                h["titles"].append(f"[{it['source']}] {it['title'][:70]}")
    rows = [(t, v) for t, v in hits.items() if len(v["fams"]) >= min_families]
    rows.sort(key=lambda x: (-len(x[1]["fams"]), -len(x[1]["srcs"]), x[0]))
    return rows


# ─────────────────────────────────────────────── 실행

def collect(skip_reddit=False):
    items, failed = [], []
    for name, fn in SOURCES:
        try:
            got = fn()
            items += got
            print(f"  {name:<18} {len(got):>3}건")
        except Exception as e:
            failed.append(f"{name}: {type(e).__name__} {e}")
            print(f"  {name:<18} 실패 — {type(e).__name__}")

    if not skip_reddit:
        for i, (path, label) in enumerate(REDDIT_FEEDS):
            if i:
                time.sleep(REDDIT_GAP)
            try:
                got = from_reddit(path, label)
                items += got
                print(f"  {label:<18} {len(got):>3}건")
            except Exception as e:
                failed.append(f"{label}: {type(e).__name__} {e}")
                print(f"  {label:<18} 실패 — {type(e).__name__}")
    return items, failed


def write_digest(items, failed, today):
    rows = cross_signals(items)
    by_src = defaultdict(list)
    for it in items:
        by_src[it["source"]].append(it)

    L = [f"# 세계 화제 레이더 — {today}", ""]
    L.append(f"소스 {len(by_src)}곳에서 {len(items)}건 수집.")
    if failed:
        L.append(f"실패 {len(failed)}곳: " + ", ".join(f.split(':')[0] for f in failed))
    L += ["", "---", "", "## 여러 곳에 동시에 걸린 것", ""]
    L.append("뉴스·검색·커뮤니티·기술처럼 **성격이 다른 계열**에 동시에 걸린 것만 남긴다.")
    L.append("구글뉴스는 BBC 기사를 실어 나르므로 그 둘이 겹치는 건 확인이 아니다.")
    L.append("")
    if rows:
        for term, v in rows[:20]:
            days = history_streak(term)
            if len(days) <= 1:
                mark = "새로 등장"
            elif len(days) >= 3:
                mark = f"**{len(days)}일 연속**"
            else:
                mark = f"{len(days)}일째"
            L.append(f"**{term}** — {mark} · {len(v['fams'])}계열 "
                     f"({' / '.join(sorted(v['fams']))}) · {len(v['srcs'])}개 소스")
            for t in v["titles"][:3]:
                L.append(f"  - {t}")
            L.append("")
    else:
        L += ["교차로 걸린 낱말이 없다. 오늘은 소스마다 딴 얘기를 하고 있다는 뜻이다.", ""]

    fresh = [(term, v) for term, v in rows if len(history_streak(term)) <= 1]
    lasting = [(term, v) for term, v in rows if len(history_streak(term)) >= 3]
    if fresh or lasting:
        L += ["---", "", "## 한눈에", ""]
        if fresh:
            L.append("**오늘 새로 뜬 것**: " + ", ".join(t for t, _ in fresh[:10]))
        if lasting:
            L.append("**사흘 넘게 버티는 것**: " + ", ".join(t for t, _ in lasting[:10]))
        L.append("")

    L += ["---", "", "## 소스별", ""]
    for src in sorted(by_src):
        L.append(f"### {src}")
        for it in by_src[src][:10]:
            extra = ""
            if it.get("views"):
                extra = f"  ({it['views']:,}회)"
            elif it.get("traffic"):
                extra = f"  ({it['traffic']})"
            elif it.get("score"):
                extra = f"  ({it['score']}점)"
            elif it.get("sub"):
                extra = f"  ({it['sub']})"
            L.append(f"- {it['title'][:95]}{extra}")
        L.append("")

    if failed:
        L += ["---", "", "## 실패한 소스", ""] + [f"- {f}" for f in failed] + [""]
    return "\n".join(L)


def main():
    args = sys.argv[1:]
    if "--list" in args:
        for n, _ in SOURCES:
            print(" ", n)
        for _, l in REDDIT_FEEDS:
            print(" ", l)
        return 0

    today = date.today().isoformat()
    print(f"\n=== 세계 화제 레이더 {today} ===\n")
    items, failed = collect(skip_reddit="--fast" in args)

    (ROOT / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "digest").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / f"{today}.json").write_text(
        json.dumps({"collectedAt": datetime.now(timezone.utc).isoformat(),
                    "items": items, "failed": failed}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    digest = write_digest(items, failed, today)
    (ROOT / "digest" / f"{today}.md").write_text(digest, encoding="utf-8")

    n = len(cross_signals(items))
    print(f"\n총 {len(items)}건, 교차 신호 {n}개")
    print(f"→ radar/digest/{today}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
