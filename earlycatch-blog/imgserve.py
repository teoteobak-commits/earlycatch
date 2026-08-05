# -*- coding: utf-8 -*-
"""이미지 임시 서버 (CORS 허용).

티스토리 편집기(https)에서 로컬 이미지를 fetch로 가져오려면 CORS 헤더가 필요하다.
Vite 개발 서버는 이 헤더를 안 보내므로 이 서버를 대신 쓴다.

사용법:
    python imgserve.py            # images/ 를 http://localhost:8899 로 서빙
    python imgserve.py 9000       # 포트 지정

브라우저 콘솔(또는 자동화)에서:
    const b = await (await fetch('http://localhost:8899/00-thumb-sm.png')).blob();

작업 끝나면 Ctrl+C 로 종료할 것. 로컬 전용이며 외부에 노출되지 않는다.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

IMAGES = Path(__file__).parent / "images"


class CORSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, fmt, *args):
        print("  " + fmt % args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    handler = partial(CORSHandler, directory=str(IMAGES))
    # 루프백에만 바인딩 — 외부에서 접근 불가
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"이미지 서버: http://localhost:{port}  (폴더: {IMAGES})")
    print("종료하려면 Ctrl+C")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n종료")
        srv.shutdown()


if __name__ == "__main__":
    main()
