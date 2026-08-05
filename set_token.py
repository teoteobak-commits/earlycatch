# -*- coding: utf-8 -*-
"""텔레그램 봇 토큰을 안전하게 저장한다.

입력한 토큰은 화면에 표시되지 않고, .secrets/telegram.json 에만 저장된다.

사용:
    python set_token.py
"""
import getpass
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CONF = Path(__file__).parent / ".secrets" / "telegram.json"
PATTERN = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{30,}$")


def main():
    print()
    print("텔레그램 봇 토큰을 붙여넣고 Enter 를 누르세요.")
    print("(입력해도 화면에는 아무것도 안 보입니다. 정상입니다.)")
    print("붙여넣기: 마우스 오른쪽 클릭 또는 Ctrl+V")
    print()

    token = getpass.getpass("토큰: ").strip()

    if not token:
        print("\n입력이 없습니다. 취소했습니다.")
        return 1

    if not PATTERN.match(token):
        print("\n토큰 형식이 아닌 것 같습니다.")
        print("BotFather가 준 형태여야 합니다: 숫자:영문숫자 (예: 1234567890:AAxxxxxxxx...)")
        print("앞뒤 공백이나 따옴표가 같이 붙었는지 확인해 주세요.")
        return 1

    CONF.parent.mkdir(exist_ok=True)
    conf = {}
    if CONF.exists():
        try:
            conf = json.loads(CONF.read_text(encoding="utf-8"))
        except Exception:
            conf = {}

    old = conf.get("bot_token")
    conf["bot_token"] = token
    # 토큰이 바뀌면 chat_id 도 다시 잡아야 한다
    if old and old != token:
        conf["chat_id"] = None

    CONF.write_text(json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n저장했습니다: {CONF}")
    print(f"토큰 확인용 앞 4자리: {token[:4]}...  (전체는 파일에만 있습니다)")
    print()
    print("다음 순서:")
    print("  1) 텔레그램에서 봇을 찾아 아무 말이나 한 번 보내기")
    print("  2) python notify_telegram.py --setup")
    print("  3) python notify_telegram.py --test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
