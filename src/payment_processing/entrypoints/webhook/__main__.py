import json
import os
from collections import Counter
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class WebhookServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, WebhookHandler)
        self.attempts: Counter[tuple[str, str]] = Counter()


class WebhookHandler(BaseHTTPRequestHandler):
    server: WebhookServer

    def do_get(self) -> None:
        if self.path == "/health":
            self.respond(status=200, payload={"status": "OK"})
            return

        self.respond(status=404, payload={"error": "not_found"})

    def do_post(self) -> None:
        if self.path not in {"/ok", "/flaky", "/fail"}:
            self.respond(status=404, payload={"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 65_536:
                self.respond(
                    status=400,
                    payload={"error": "invalid_body_size"},
                )
                return

            payload = json.loads(self.rfile.read(length))

            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object")

            payment_id = payload.get("payment_id")

            if not isinstance(payment_id, str) or not payment_id:
                raise ValueError("Expected payment_id")

        except (ValueError, UnicodeDecodeError):
            self.respond(status=400, payload={"error": "invalid_payload"})
            return

        key = (self.path, payment_id)
        self.server.attempts[key] += 1
        attempt = self.server.attempts[key]

        if self.path == "/fail":
            status = 503
        elif self.path == "/flaky" and attempt < 3:
            status = 503
        else:
            status = 200

        print(
            json.dumps(
                {
                    "time": datetime.now(UTC).isoformat(),
                    "path": self.path,
                    "attempt": attempt,
                    "http_status": status,
                    "payload": payload,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

        self.respond(
            status=status,
            payload={"attempt": attempt},
        )

    def respond(self, *, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *args: object) -> None:
        pass


def main() -> None:
    host = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.environ.get("WEBHOOK_PORT", "8080"))

    with WebhookServer((host, port)) as server:
        server.timeout = 5
        print(
            f"Test webhook receiver listening on {host}:{port}",
            flush=True,
        )

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
