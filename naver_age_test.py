# -*- coding: utf-8 -*-
"""데이터랩으로 연령대 분포를 뽑는 방법이 실제로 통하는지 검증한다.

왜 검증이 필요한가:
    데이터랩은 요청마다 그 안의 최댓값을 100으로 잡아 정규화한다.
    그래서 연령대별로 따로 요청하면 각자 100이 되어 서로 비교가 안 된다.
    여기서는 매 요청에 기준 키워드(날씨)를 같이 넣고 그 비율을 본다.
    한 요청 안의 키워드끼리는 같은 척도라서 비율은 의미가 있다.

    이 방법이 맞는지는 "정답을 아는 키워드"로 확인한다.
    로블록스는 10대, 국민연금은 50대 이상으로 갈려야 정상이다.
    안 갈리면 이 방법을 쓰면 안 된다.

사용:
    python naver_age_test.py            정답 아는 키워드로 방법 검증
    python naver_age_test.py 키워드      임의 키워드의 연령 분포
"""
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CONF = Path(__file__).parent / ".secrets" / "naver.json"
API = "https://openapi.naver.com/v1/datalab/search"
ANCHOR = "날씨"  # 전 연령이 고르게 검색하는 기준점

BANDS = [
    ("10대",    ["2"]),
    ("20대",    ["3", "4"]),
    ("30대",    ["5", "6"]),
    ("40대",    ["7", "8"]),
    ("50대이상", ["9", "10", "11"]),
]


def load_keys():
    if not CONF.exists():
        print(f"키 파일이 없습니다: {CONF}")
        print("먼저 python set_naver.py 를 실행해 주세요.")
        sys.exit(1)
    c = json.loads(CONF.read_text(encoding="utf-8"))
    return c["client_id"], c["client_secret"]


def call(cid, secret, body):
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-Naver-Client-Id": cid,
            "X-Naver-Client-Secret": secret,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def total(result_group):
    return sum(p["ratio"] for p in result_group.get("data", []))


def distribution(cid, secret, keyword):
    """연령대별로 (대상 / 기준) 비율을 구해 100 기준 분포로 만든다."""
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=90)
    raw = {}

    for label, ages in BANDS:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "timeUnit": "week",
            "keywordGroups": [
                {"groupName": "대상", "keywords": [keyword]},
                {"groupName": "기준", "keywords": [ANCHOR]},
            ],
            "ages": ages,
        }
        try:
            res = call(cid, secret, body)
        except urllib.error.HTTPError as e:
            print(f"  {label}: 실패 HTTP {e.code} — {e.read().decode('utf-8','replace')[:120]}")
            raw[label] = None
            continue

        groups = {g["title"]: g for g in res.get("results", [])}
        t, a = total(groups.get("대상", {})), total(groups.get("기준", {}))
        raw[label] = (t / a) if a else None

    vals = [v for v in raw.values() if v]
    if not vals:
        return None
    s = sum(vals)
    return {k: (round(v / s * 100, 1) if v else None) for k, v in raw.items()}


def show(keyword, dist):
    if not dist:
        print(f"  {keyword}: 데이터를 못 받았습니다")
        return
    print(f"  {keyword}")
    for label, pct in dist.items():
        if pct is None:
            print(f"    {label:8s} 측정 실패")
        else:
            print(f"    {label:8s} {pct:5.1f}%  {'█' * int(pct / 2)}")


def main():
    cid, secret = load_keys()

    if len(sys.argv) > 1:
        kw = sys.argv[1]
        print(f"\n'{kw}' 연령대 분포 (최근 90일, 기준 키워드 '{ANCHOR}' 대비)\n")
        show(kw, distribution(cid, secret, kw))
        print("\n주의: 절대 검색량이 아니라 상대 분포입니다. 네이버 검색 기준이라")
        print("유튜브·틱톡 시청자 분포와는 다를 수 있습니다.")
        return 0

    print("\n방법 검증 — 정답을 아는 키워드로 확인합니다.")
    print("로블록스는 어리게, 국민연금은 나이 많게 갈려야 정상입니다.\n")

    young = distribution(cid, secret, "로블록스")
    old = distribution(cid, secret, "국민연금")
    show("로블록스", young)
    print()
    show("국민연금", old)

    print()
    if not young or not old:
        print("판정: 데이터를 못 받아 검증 불가")
        return 1

    y_low = (young.get("10대") or 0) + (young.get("20대") or 0)
    o_high = (old.get("50대이상") or 0) + (old.get("40대") or 0)

    if y_low > 40 and o_high > 40:
        print(f"판정: 통과. 로블록스 10~20대 {y_low:.0f}%, 국민연금 40대이상 {o_high:.0f}%")
        print("      방향이 예상대로 갈립니다. 이 방법을 써도 됩니다.")
        return 0

    print(f"판정: 미흡. 로블록스 10~20대 {y_low:.0f}%, 국민연금 40대이상 {o_high:.0f}%")
    print("      기대만큼 안 갈립니다. 이 방법으로 연령을 단정하면 안 됩니다.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
