import json
import os
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import config, battery, procs
from .battery import DATA, LOCK
from .template import HTML

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default Apache-style logs
        pass

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return

        if path.startswith("/static/"):
            filename = os.path.basename(path)
            filepath = os.path.join(STATIC_DIR, filename)
            if os.path.isfile(filepath):
                ctype = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
                with open(filepath, "rb") as f:
                    body = f.read()
                self._send(200, body, ctype)
            else:
                self._send(404, b"Not Found", "text/plain")
            return

        if path == "/api/battery":
            with LOCK:
                pts = list(DATA)
            points = [
                {"t": t, "pct": pct, "w": w, "status": st, "eta": eta}
                for (t, pct, w, st, eta) in pts
            ]
            latest = points[-1] if points else None
            payload = json.dumps({
                "battery": config.BAT,
                "sample_seconds": config.SAMPLE_SECONDS,
                "points": points,
                "latest": latest,
            }).encode("utf-8")
            self._send(200, payload, "application/json; charset=utf-8")
            return

        if path == "/api/conservation":
            enabled = battery.get_conservation_mode()
            if enabled is None:
                payload = json.dumps({"available": False}).encode()
            else:
                payload = json.dumps({"available": True, "enabled": enabled}).encode()
            self._send(200, payload, "application/json; charset=utf-8")
            return

        if path == "/api/procs":
            payload = json.dumps({"procs": procs.get_proc_stats()}).encode("utf-8")
            self._send(200, payload, "application/json; charset=utf-8")
            return

        if path == "/api/uptime":
            try:
                with open("/proc/uptime") as f:
                    seconds = float(f.read().split()[0])
            except Exception:
                seconds = 0.0
            payload = json.dumps({"seconds": seconds}).encode("utf-8")
            self._send(200, payload, "application/json; charset=utf-8")
            return

        self._send(404, b"Not Found", "text/plain; charset=utf-8")

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/conservation":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                want = bool(data.get("enabled", False))
                ok = battery.set_conservation_mode(want)
                enabled = battery.get_conservation_mode()
                payload = json.dumps({
                    "available": True,
                    "enabled": enabled,
                    "ok": ok,
                }).encode()
                self._send(200, payload, "application/json; charset=utf-8")
            except Exception as e:
                self._send(500, json.dumps({"error": str(e)}).encode(), "application/json")
            return

        self._send(404, b"Not Found", "text/plain; charset=utf-8")


def main():
    if not os.path.exists(config.CAPACITY_PATH):
        raise SystemExit(
            f"Battery path not found: {config.CAPACITY_PATH}\n"
            f"Set BATTERY_NAME=BAT0/BAT1/... via environment variable."
        )

    t = threading.Thread(target=battery.sampler, daemon=True)
    t.start()
    t2 = threading.Thread(target=procs.proc_sampler, daemon=True)
    t2.start()

    httpd = ThreadingHTTPServer((config.HOST, config.PORT), Handler)
    print(f"  Dashboard → http://{config.HOST}:{config.PORT}/")
    print(f"  Battery:    {config.BAT}")
    print(f"  Sampling:   every {config.SAMPLE_SECONDS}s")
    print(f"  Max points: {config.MAX_POINTS}  (~12h window)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")
