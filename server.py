"""
Local server: serves the app and proxies Anthropic API using ANTHROPIC_API_KEY from .env.
Run: pip install python-dotenv  (if needed), then  python server.py
Open: http://localhost:8765
"""
import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _is_api_messages(path):
    base = (path.split("?")[0] or "").strip().rstrip("/")
    return base == "/api/messages" or base.startswith("/api/messages/")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if _is_api_messages(self.path):
            self.send_json(200, {"ok": True, "message": "API proxy is running. Open http://localhost:8765 in the browser."})
            return
        super().do_GET()

    def do_POST(self):
        if _is_api_messages(self.path):
            try:
                print("POST /api/messages -> proxying to Anthropic")
                self.proxy_anthropic()
            except Exception as e:
                print("Proxy error:", e)
                self.send_json(500, {"error": {"message": "Server error: " + str(e)}})
        else:
            self.send_json(404, {"error": {"message": "Not found. Run: python server.py then open http://localhost:8765"}})

    def proxy_anthropic(self):
        if not ANTHROPIC_API_KEY or not ANTHROPIC_API_KEY.strip():
            self.send_json(400, {"error": {"message": "ANTHROPIC_API_KEY is not set in .env"}})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        req = urllib.request.Request(
            ANTHROPIC_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY.strip(),
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                # Always respond with JSON so the frontend never sees HTML
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "replace")
            try:
                err_json = json.loads(err_body) if err_body.strip() else {}
            except json.JSONDecodeError:
                err_json = {}
            if "error" not in err_json:
                err_json = {"error": {"message": err_body[:500] or str(e)}}
            self.send_json(e.code, err_json)
        except Exception as e:
            self.send_json(500, {"error": {"message": str(e)}})

    def send_json(self, status, obj):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        body = json.dumps(obj).encode("utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if _is_api_messages(self.path):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
        else:
            super().do_OPTIONS()

    def log_message(self, format, *args):
        print("[%s] %s" % (self.log_date_time_string(), format % args))


def main():
    port = int(os.environ.get("PORT", 8765))
    server = HTTPServer(("", port), Handler)
    print(f"Serving at http://localhost:{port}")
    if not ANTHROPIC_API_KEY or not ANTHROPIC_API_KEY.strip():
        print("Warning: ANTHROPIC_API_KEY not set in .env — add it or enter the key in the app UI.")
    server.serve_forever()


if __name__ == "__main__":
    main()
