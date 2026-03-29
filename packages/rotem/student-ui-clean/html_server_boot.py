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
import urllib.parse
from http.cookies import SimpleCookie
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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

        # Let the default handler serve static files
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/contact":
            self._handle_contact_form()
            return

        self.send_error(404, "Not Found")

    def _serve_file(self, filename, lang="en"):
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
