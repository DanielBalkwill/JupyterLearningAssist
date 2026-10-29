#!/usr/bin/env python3
"""
AI Notebook — local launcher + CORS relay.

Run this, then open the printed URL. It does two things:
  1. Serves index.html over http://127.0.0.1:<port> (stable origin => localStorage
     for your keys/notebook persists reliably; file:// is flaky for that).
  2. Exposes POST /relay, a localhost-only pass-through so LLM API calls that a
     browser would normally block with CORS go through here instead. Enable it
     in the app under  (Keys) -> "Route calls through local proxy".

Security: binds to 127.0.0.1 ONLY. The relay forwards to whatever URL the page
sends it, so do NOT expose this port to a network or the internet.

Usage:
    python serve.py                # port 8787, opens your browser
    PORT=9000 python serve.py      # custom port   (set PORT in the environment)
    AINB_NOOPEN=1 python serve.py  # don't auto-open a browser
"""
import http.server
import socketserver
import json
import os
import sys
import threading
import webbrowser
import urllib.request
import urllib.error

PORT = int(os.environ.get("PORT", "8787"))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIRECTORY, **k)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") != "/relay":
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            url = payload["url"]
            method = payload.get("method", "POST")
            headers = payload.get("headers", {}) or {}
            body = payload.get("body")
            if isinstance(body, (dict, list)):
                data = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                data = body.encode("utf-8")
            else:
                data = None
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    out = resp.read().decode("utf-8", "replace")
                    status = resp.getcode()
            except urllib.error.HTTPError as e:
                out = e.read().decode("utf-8", "replace")
                status = e.code
            self._reply({"status": status, "body": out})
        except Exception as e:  # noqa: BLE001 - surface any relay failure to the page
            self._reply({"status": 0, "body": json.dumps({"error": str(e)})})

    def _reply(self, obj):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *a):  # keep the console quiet
        pass


def main():
    os.chdir(DIRECTORY)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}/index.html"
        print(f"\n  AI Notebook  ->  {url}")
        print("  CORS relay   ->  POST /relay  (localhost only)")
        print("  Ctrl+C to stop.\n")
        if not os.environ.get("AINB_NOOPEN"):
            threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  stopped.")


if __name__ == "__main__":
    sys.exit(main())
