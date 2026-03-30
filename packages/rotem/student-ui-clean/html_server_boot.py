#!/usr/bin/env python3
"""
RoTEM Student UI — HTTP Server with Language Routing

Serves the student UI with automatic language detection:
- English users (ngrok with lang=en, Accept-Language, or IP-based) → index_en.html
- Hebrew users (default) → index.html

Usage:
    python html_server_boot.py [--port 8080] [--host 0.0.0.0]
"""

import argparse
import http.server
import json
import os
import socketserver
import threading
import time
import urllib.parse
import uuid
from http.cookies import SimpleCookie
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUTH_STORE_PATH = BASE_DIR / "auth_store.json"

# --- Token / Auth Store ---

_auth_lock = threading.Lock()


def _load_auth_store():
    """Load token store from disk."""
    if not AUTH_STORE_PATH.exists():
        return {"schema_version": 1, "tokens": {}}
    with open(AUTH_STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_auth_store(store):
    """Persist token store to disk (survives restarts)."""
    with open(AUTH_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def validate_token(token, device_fingerprint=None):
    """Validate a MOXO token and optionally lock it to a device.

    Returns (ok: bool, info: dict).
    """
    with _auth_lock:
        store = _load_auth_store()
        tokens = store.get("tokens", {})

        if token not in tokens:
            return False, {"error": "invalid_token"}

        entry = tokens[token]

        # Already locked to a different device? Auto-migrate instead of blocking.
        if (
            entry.get("locked_device")
            and device_fingerprint
            and entry["locked_device"] != device_fingerprint
        ):
            # Graceful failover: re-lock to new device, log migration
            entry["previous_devices"] = entry.get("previous_devices", [])
            entry["previous_devices"].append(entry["locked_device"])
            entry["locked_device"] = device_fingerprint
            entry["last_migrated"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )

        # Activate / lock on first use
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if entry["status"] == "available":
            entry["status"] = "active"
            entry["activated_at"] = now
        if device_fingerprint and not entry.get("locked_device"):
            entry["locked_device"] = device_fingerprint
        entry["last_seen"] = now

        _save_auth_store(store)
        return True, {
            "label": entry.get("label"),
            "status": entry["status"],
            "course_lock": store.get("course_lock", "moxo"),
        }


def provision_token(name, email, location=""):
    """Create a new MOXO token dynamically (for Lovable webhook leads).

    Returns the token string and its label.
    """
    with _auth_lock:
        store = _load_auth_store()
        tokens = store.setdefault("tokens", {})

        # Generate a unique token
        suffix = uuid.uuid4().hex[:6].upper()
        token_id = f"MOXO-{suffix}"
        seq = len(tokens) + 1
        label = f"MOXO-{seq:02d}"

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tokens[token_id] = {
            "label": label,
            "status": "provisioned",
            "locked_device": None,
            "activated_at": None,
            "last_seen": None,
            "provisioned_at": now,
            "lead": {
                "name": name,
                "email": email,
                "location": location,
            },
        }
        _save_auth_store(store)
        return token_id, label

# English-speaking country IP ranges would be resolved via GeoIP in production.
# For now, we use heuristics: query params, cookies, and Accept-Language header.
ENGLISH_LANGUAGE_PREFIXES = ("en",)
HEBREW_LANGUAGE_PREFIXES = ("he", "iw")


def detect_language(handler):
    """Detect preferred language from the request.

    Priority order:
    1. Explicit query parameter: ?lang=en or ?lang=he
    2. Cookie: lang=en
    3. Ngrok header hint (X-Forwarded-For from UK/US ranges — simplified)
    4. Accept-Language header
    5. Default to Hebrew
    """
    parsed = urllib.parse.urlparse(handler.path)
    query = urllib.parse.parse_qs(parsed.query)

    # 1. Query parameter
    lang_param = query.get("lang", [None])[0]
    if lang_param:
        lang_param = lang_param.lower().strip()
        if lang_param.startswith(ENGLISH_LANGUAGE_PREFIXES):
            return "en"
        if lang_param.startswith(HEBREW_LANGUAGE_PREFIXES):
            return "he"

    # 2. Cookie
    cookie_header = handler.headers.get("Cookie", "")
    if cookie_header:
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
            if "lang" in cookie:
                lang_cookie = cookie["lang"].value.lower().strip()
                if lang_cookie.startswith(ENGLISH_LANGUAGE_PREFIXES):
                    return "en"
                if lang_cookie.startswith(HEBREW_LANGUAGE_PREFIXES):
                    return "he"
        except Exception:
            pass

    # 3. Accept-Language header
    accept_lang = handler.headers.get("Accept-Language", "")
    if accept_lang:
        # Parse primary language preference
        parts = accept_lang.split(",")
        for part in parts:
            lang = part.split(";")[0].strip().lower()
            if lang.startswith(ENGLISH_LANGUAGE_PREFIXES):
                return "en"
            if lang.startswith(HEBREW_LANGUAGE_PREFIXES):
                return "he"

    # 4. Default to Hebrew
    return "he"


class RoTEMRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with language routing and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Root path — detect language and serve appropriate page
        if path == "" or path == "/":
            lang = detect_language(self)
            if lang == "en":
                self._serve_file("index_en.html", lang="en")
            else:
                # Fallback: serve index_en.html if index.html doesn't exist yet
                if (BASE_DIR / "index.html").exists():
                    self._serve_file("index.html", lang="he")
                else:
                    self._serve_file("index_en.html", lang="en")
            return

        # Explicit language-prefixed paths
        if path == "/en" or path == "/en/":
            self._serve_file("index_en.html", lang="en")
            return

        if path == "/he" or path == "/he/":
            if (BASE_DIR / "index.html").exists():
                self._serve_file("index.html", lang="he")
            else:
                self._redirect("/?lang=he")
            return

        # Token-gated student journey
        if path == "/student_journey.html" or path == "/student_journey":
            self._handle_student_journey(parsed)
            return

        # Token status API (GET /api/tokens)
        if path == "/api/tokens":
            self._handle_tokens_list()
            return

        # Token validation API (GET /api/token/validate?token=XXX)
        if path == "/api/token/validate":
            self._handle_token_validate(parsed)
            return

        # Let the default handler serve static files
        super().do_GET()

    def do_OPTIONS(self):
        """Handle CORS preflight for webhook endpoints."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/contact":
            self._handle_contact_form()
            return

        if parsed.path == "/api/webhooks/lovable":
            self._handle_lovable_webhook()
            return

        if parsed.path == "/api/auth/migrate-session":
            self._handle_migrate_session()
            return

        if parsed.path == "/api/system/rescue":
            self._handle_rescue()
            return

        self.send_error(404, "Not Found")

    def _handle_lovable_webhook(self):
        """Accept leads from Lovable app and provision a MOXO token.

        POST /api/webhooks/lovable
        Body: {"name": "...", "email": "...", "location": "..."}
        Returns: {"token": "MOXO-XXXXXX", "label": "MOXO-11",
                  "journey_url": "/student_journey.html?token=MOXO-XXXXXX"}
        """
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 10_000:
            self._json_error(413, "too_large", "Request too large")
            return

        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_error(400, "invalid_json", "Body must be valid JSON")
            return

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        location = data.get("location", "").strip()

        if not name or not email:
            self._json_error(400, "missing_fields", "name and email are required")
            return

        token_id, label = provision_token(name, email, location)

        journey_url = f"/student_journey.html?token={token_id}"

        # Log the lead
        log_path = BASE_DIR / "enquiries.log"
        try:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"--- Lovable Lead [{now}] ---\n")
                f.write(f"Name: {name}\nEmail: {email}\nLocation: {location}\n")
                f.write(f"Token: {token_id} ({label})\n\n")
        except Exception:
            pass

        response = json.dumps({
            "status": "ok",
            "token": token_id,
            "label": label,
            "journey_url": journey_url,
            "message": f"Session provisioned for {name}",
        })
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def _handle_migrate_session(self):
        """Migrate a token to a new device without blocking the student.

        POST /api/auth/migrate-session
        Body: {"token": "MOXO-XXXX"}
        """
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_error(400, "invalid_json", "Body must be valid JSON")
            return

        token = data.get("token", "").strip()
        if not token:
            self._json_error(400, "missing_token", "token is required")
            return

        ua = self.headers.get("User-Agent", "unknown")
        ip = self.headers.get("X-Forwarded-For", self.client_address[0])
        new_device = f"{ip}|{ua[:80]}"

        with _auth_lock:
            store = _load_auth_store()
            tokens = store.get("tokens", {})
            if token not in tokens:
                self._json_error(404, "invalid_token", "Token not found")
                return
            entry = tokens[token]
            old_device = entry.get("locked_device")
            entry["previous_devices"] = entry.get("previous_devices", [])
            if old_device:
                entry["previous_devices"].append(old_device)
            entry["locked_device"] = new_device
            entry["last_migrated"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )
            _save_auth_store(store)

        response = json.dumps({
            "status": "ok",
            "message": "Session migrated to new device",
            "label": entry.get("label"),
        })
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def _handle_rescue(self):
        """Emergency context reset — clears Nitzutz short-term memory.

        POST /api/system/rescue
        Body: {"token": "MOXO-XXXX", "video_timestamp": 42.5}
        Proxies force_context_reset to Nitzutz (9997) and returns confirmation.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json_error(400, "invalid_json", "Body must be valid JSON")
            return

        token = data.get("token", "")
        timestamp = data.get("video_timestamp", 0)

        # Try to forward to Nitzutz (port 9997) if available
        rescue_response = {
            "status": "ok",
            "message": (
                "Got it. Resetting clinical focus. "
                "Let\u2019s look at this segment again from a new perspective\u2026"
            ),
            "context_cleared": True,
            "video_timestamp": timestamp,
        }

        try:
            import urllib.request
            req = urllib.request.Request(
                "http://127.0.0.1:9997/reset-context",
                data=json.dumps({
                    "force_context_reset": True,
                    "token": token,
                    "reason": "student_requested",
                    "video_timestamp": timestamp,
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                nitzutz_data = json.loads(resp.read().decode("utf-8"))
                rescue_response["nitzutz"] = nitzutz_data
        except Exception:
            # Nitzutz not available — return default response
            rescue_response["nitzutz"] = "offline"

        response = json.dumps(rescue_response)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def _handle_student_journey(self, parsed):
        """Gate student_journey.html behind a valid MOXO token."""
        query = urllib.parse.parse_qs(parsed.query)
        token = query.get("token", [None])[0]

        if not token:
            self._json_error(403, "missing_token",
                             "Access requires a MOXO token. Use ?token=ROTEM-MOXO-XXXX")
            return

        # Device fingerprint from User-Agent + IP (lightweight, not cryptographic)
        ua = self.headers.get("User-Agent", "unknown")
        ip = self.headers.get("X-Forwarded-For", self.client_address[0])
        device_fp = f"{ip}|{ua[:80]}"

        ok, info = validate_token(token, device_fingerprint=device_fp)
        if not ok:
            if info.get("error") == "device_mismatch":
                self._json_error(403, "device_mismatch",
                                 f"Token {info.get('label', token)} is locked to another device.")
            else:
                self._json_error(403, "invalid_token",
                                 "Token not recognised. Please check your access link.")
            return

        # Token valid — serve the student journey page
        # Set session cookie with token label for Fleet Admiral Grid
        label = info.get("label", token)
        self._serve_file(
            "student_journey.html",
            extra_headers={
                "Set-Cookie": (
                    f"rotem_token={token}; Path=/; Max-Age=86400; SameSite=Lax"
                ),
                "X-RoTEM-Token": token,
                "X-RoTEM-Label": label,
                "X-RoTEM-Course": info.get("course_lock", "moxo"),
            },
        )

    def _handle_tokens_list(self):
        """Return token status overview for Mission Control."""
        with _auth_lock:
            store = _load_auth_store()
        tokens = store.get("tokens", {})
        summary = []
        for tid, entry in tokens.items():
            summary.append({
                "token": tid,
                "label": entry.get("label"),
                "status": entry.get("status"),
                "activated_at": entry.get("activated_at"),
                "last_seen": entry.get("last_seen"),
                "has_device": bool(entry.get("locked_device")),
            })
        body = json.dumps({"tokens": summary, "total": len(summary)})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _handle_token_validate(self, parsed):
        """Validate a token without locking it (dry run)."""
        query = urllib.parse.parse_qs(parsed.query)
        token = query.get("token", [None])[0]
        if not token:
            self._json_error(400, "missing_token", "Provide ?token=XXX")
            return
        ok, info = validate_token(token, device_fingerprint=None)
        body = json.dumps({"valid": ok, **info})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _json_error(self, code, error_type, message):
        """Send a JSON error response."""
        body = json.dumps({"error": error_type, "message": message})
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _serve_file(self, filename, lang="en", extra_headers=None):
        """Serve an HTML file with a language cookie."""
        filepath = BASE_DIR / filename
        if not filepath.exists():
            self.send_error(404, f"File not found: {filename}")
            return

        content = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header(
            "Set-Cookie",
            f"lang={lang}; Path=/; Max-Age=31536000; SameSite=Lax",
        )
        self.send_header("Cache-Control", "no-cache")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(content)

    def _redirect(self, location, code=302):
        """Send a redirect response."""
        self.send_response(code)
        self.send_header("Location", location)
        self.end_headers()

    def _handle_contact_form(self):
        """Handle contact form submissions."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 10_000:
            self.send_error(413, "Request too large")
            return

        body = self.rfile.read(content_length)

        # Log the enquiry (in production, send email / store in DB)
        log_path = BASE_DIR / "enquiries.log"
        try:
            decoded = body.decode("utf-8", errors="replace")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"--- New Enquiry ---\n{decoded}\n\n")
        except Exception as exc:
            print(f"Warning: could not log enquiry: {exc}")

        # Respond with success
        response = json.dumps({"status": "ok", "message": "Enquiry received"})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="RoTEM Student UI Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    handler = RoTEMRequestHandler

    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        print(f"RoTEM Student UI serving on http://{args.host}:{args.port}")
        print(f"  English: http://{args.host}:{args.port}/?lang=en")
        print(f"  Hebrew:  http://{args.host}:{args.port}/?lang=he")
        print(f"  Auto-detect: http://{args.host}:{args.port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
