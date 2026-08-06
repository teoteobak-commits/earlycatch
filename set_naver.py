# -*- coding: utf-8 -*-
"""네이버 데이터랩 API 키를 안전하게 저장하고 바로 검증한다.

입력한 Secret 은 화면에 표시되지 않고 .secrets/naver.json 에만 저장된다.
저장 직후 실제 API 를 한 번 호출해서 키가 살아있는지 확인한다.

사용:
    python set_naver.py
"""
import getpass
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


def main():
    print()
    print("네이버 개발자센터에서 발급받은 값을 넣어주세요.")
    print("Client ID 는 공개해도 되는 값이라 화면에 보입니다.")
    print("Client Secret 은 비밀번호처럼 가려집니다. (입력해도 안 보이는 게 정상입니다)")
    print()

    cid = input("Client ID: ").strip()
    if not cid:
        print("\n입력이 없습니다. 취소했습니다.")
        return 1

    secret = getpass.getpass("Client Secret: ").strip()
    if not secret:
        print("\n입력이 없습니다. 취소했습니다.")
        return 1

    # 실제로 되는지 먼저 확인하고 나서 저장한다
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=30)
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "timeUnit": "week",
        "keywordGroups": [{"groupName": "확인용", "keywords": ["유튜브"]}],
    }

    print("\n키가 살아있는지 실제로 한 번 불러봅니다...")
    try:
        res = call(cid, secret, body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        print(f"\n실패했습니다. HTTP {e.code}")
        print(f"응답: {detail}")
        print()
        if e.code == 401:
            print("401 은 대개 ID/Secret 오타이거나 앞뒤에 공백·따옴표가 붙은 경우입니다.")
        elif e.code == 403:
            print("403 은 대개 애플리케이션에 '데이터랩(검색어 트렌드)' API 가")
            print("추가되지 않은 경우입니다. 개발자센터에서 사용 API 를 확인해 주세요.")
        print("\n저장하지 않았습니다.")
        return 1
    except Exception as e:
        print(f"\n호출 중 오류: {e}")
        print("저장하지 않았습니다.")
        return 1

    points = res.get("results", [{}])[0].get("data", [])
    print(f"성공했습니다. '유튜브' 최근 한 달 데이터 {len(points)}개 구간을 받았습니다.")

    CONF.parent.mkdir(exist_ok=True)
    CONF.write_text(
        json.dumps({"client_id": cid, "client_secret": secret}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"저장했습니다: {CONF}")
    print(f"(Secret 확인용 앞 3자리: {secret[:3]}...  전체는 파일에만 있습니다)")
    print()
    print("다음 순서:")
    print("  python naver_age_test.py    연령대별로 실제로 갈리는지 검증")
    return 0


if __name__ == "__main__":
    sys.exit(main())
