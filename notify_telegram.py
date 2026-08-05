# -*- coding: utf-8 -*-
"""텔레그램 알림 전송.

토큰은 이 파일에 절대 적지 않는다. `.secrets/telegram.json` 에서 읽기만 한다.

준비 (한 번만):
  1) .secrets/telegram.json 을 만들고 아래 형태로 저장
       { "bot_token": "여기에_붙여넣기", "chat_id": null }
  2) 텔레그램에서 만든 봇을 찾아 아무 말이나 한 번 보낸다 (예: 안녕)
  3) python notify_telegram.py --setup      → chat_id 자동으로 채워짐
  4) python notify_telegram.py --test       → 테스트 메시지 발송

사용:
  python notify_telegram.py "보낼 내용"
  python notify_telegram.py --file report.txt
  echo "내용" | python notify_telegram.py
"""
import io
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
CONF = HERE / ".secrets" / "telegram.json"
API = "https://api.telegram.org/bot{token}/{method}"
LIMIT = 4096  # 텔레그램 메시지 길이 제한


def load_conf() -> dict:
    if not CONF.exists():
        print(f"설정 파일이 없습니다: {CONF}")
        print('아래 내용으로 만들어 주세요:')
        print('  { "bot_token": "BotFather에서_받은_토큰", "chat_id": null }')
        sys.exit(2)
    conf = json.loads(CONF.read_text(encoding="utf-8"))
    if not conf.get("bot_token") or "여기에" in str(conf.get("bot_token")):
        print("bot_token 이 비어 있습니다. .secrets/telegram.json 을 확인하세요.")
        sys.exit(2)
    return conf


def save_conf(conf: dict):
    CONF.write_text(json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8")


def call(token: str, method: str, params: dict) -> dict:
    url = API.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=20) as r:
        return json.loads(r.read().decode())


def setup():
    """봇에게 보낸 최근 메시지에서 chat_id 를 찾아 저장한다."""
    conf = load_conf()
    url = API.format(token=conf["bot_token"], method="getUpdates")
    with urllib.request.urlopen(url, timeout=20) as r:
        res = json.loads(r.read().decode())
    if not res.get("ok"):
        print("토큰이 잘못됐거나 폐기된 것 같습니다:", res.get("description"))
        return 1
    updates = res.get("result", [])
    if not updates:
        print("받은 메시지가 없습니다.")
        print("텔레그램에서 봇을 찾아 아무 말이나 한 번 보낸 뒤 다시 실행하세요.")
        return 1
    chat = updates[-1].get("message", {}).get("chat", {})
    conf["chat_id"] = chat.get("id")
    save_conf(conf)
    name = chat.get("first_name") or chat.get("title") or ""
    print(f"chat_id 저장 완료 ({name})")
    return 0


def send(text: str) -> int:
    conf = load_conf()
    if not conf.get("chat_id"):
        print("chat_id 가 없습니다. 먼저 --setup 을 실행하세요.")
        return 2
    # 길면 잘라서 나눠 보낸다
    chunks, cur = [], ""
    for line in text.splitlines(keepends=True):
        if len(cur) + len(line) > LIMIT - 100:
            chunks.append(cur)
            cur = line
        else:
            cur += line
    chunks.append(cur)

    for i, chunk in enumerate(chunks, 1):
        head = f"({i}/{len(chunks)})\n" if len(chunks) > 1 else ""
        res = call(conf["bot_token"], "sendMessage", {
            "chat_id": conf["chat_id"],
            "text": head + chunk,
            "disable_web_page_preview": "true",
        })
        if not res.get("ok"):
            print("전송 실패:", res.get("description"))
            return 1
    print(f"전송 완료 ({len(chunks)}건)")
    return 0


def main():
    args = sys.argv[1:]
    if args and args[0] == "--setup":
        return setup()
    if args and args[0] == "--test":
        return send("Early Catch 알림 연결 테스트입니다. 이 메시지가 보이면 설정 완료.")
    if args and args[0] == "--file":
        return send(Path(args[1]).read_text(encoding="utf-8"))
    if args:
        return send(" ".join(args))
    if not sys.stdin.isatty():
        return send(sys.stdin.read())
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
