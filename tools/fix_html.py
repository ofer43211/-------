#!/usr/bin/env python3
"""
RoTEM HTML Fixer — copies and fixes 209 HTML pages.

Reads J:\\html\\rotem_index.html (JSON list of pages),
copies each to J:\\html\\rotem_fixed\\, applies fixes,
and writes a report to J:\\html\\fix_report.json.

Usage:
    python fix_html.py
"""

import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────

INDEX_FILE = r"J:\html\rotem_index.html"
OUTPUT_DIR = r"J:\html\rotem_fixed"
REPORT_FILE = r"J:\html\fix_report.json"

ROOTS = [
    r"J:\html", r"J:\file1s", r"J:\MOXO",
    r"J:\btl-gpt-production-suite",
    r"J:\rotem_complete1_learning_gifs_upgraded_package",
    r"C:\RoTEM_CL", r"C:\RoTEM-Local", r"C:\rotem_brain",
    r"C:\RotemOS", r"C:\RavMoach_Starter", r"C:\TheVortex",
    r"C:\MasterRotem", r"C:\AI_Tasks", r"C:\AI_GPT_Engine",
    r"C:\AIEmpire", r"C:\GeminiBiju_Unified",
    r"C:\rotem-v31-production", r"C:\rotem-v32-production",
    r"C:\rotem-suite", r"C:\rotem-digital-empire",
    r"C:\rotem-dashboard-enterprise", r"C:\rotem-dashboard-unified",
    r"C:\rotem_bar", r"C:\rotem_nachat",
    r"C:\Projects\RoTEM_Dashboard", r"C:\Projects\RoTEM_CL_CODE",
    r"C:\Projects\RoTEM_Git", r"C:\Projects\exposure-page",
    r"C:\Projects\Archives\RoTEM_Package",
    r"C:\Rotem_Empire_LIVE", r"C:\RoTEMcollective",
    r"C:\MasterRotem\tzomet_full_bundle", r"C:\Dev\RotemOS-Core",
]

# ── CSP meta tag ───────────────────────────────────────────────────────────────

CSP_META = (
    '<meta http-equiv="Content-Security-Policy" '
    'content="default-src * \'unsafe-inline\' \'unsafe-eval\' data: blob:;">'
)

# ── Compatibility shim ─────────────────────────────────────────────────────────

COMPAT_SHIM = """\
<script>
// RoTEM compatibility shim
if (typeof showTab === 'undefined') {
  window.showTab = function(id) {
    document.querySelectorAll('[data-tab]').forEach(function(t) { t.style.display='none'; });
    var el = document.getElementById(id) || document.querySelector('[data-tab="'+id+'"]');
    if (el) el.style.display='block';
  };
}
if (typeof switchTab === 'undefined') window.switchTab = window.showTab;
if (typeof openTab === 'undefined') window.openTab = window.showTab;
if (typeof toggleSection === 'undefined') {
  window.toggleSection = function(id) {
    var el = document.getElementById(id);
    if (el) el.style.display = el.style.display==='none' ? 'block' : 'none';
  };
}
</script>"""


# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(path_str: str) -> str:
    """Turn an arbitrary file path into a safe, unique filename slug."""
    # Normalise separators and strip drive letters
    s = path_str.replace("\\", "/").replace("://", "_")
    s = re.sub(r"^[A-Za-z]:", "", s)
    # Keep only alphanumerics, hyphens, underscores, dots
    s = re.sub(r"[^A-Za-z0-9._-]", "_", s)
    # Collapse repeated underscores
    s = re.sub(r"_+", "_", s).strip("_")
    # Ensure .html extension
    if not s.lower().endswith(".html"):
        s += ".html"
    return s


def find_file(relative_path: str) -> str | None:
    """Search ROOTS for a file matching *relative_path*. Return full path or None."""
    # First, check if the path itself is absolute and exists
    if os.path.isabs(relative_path) and os.path.isfile(relative_path):
        return relative_path

    # Normalise separators
    rel = relative_path.replace("/", os.sep).replace("\\", os.sep).lstrip(os.sep)

    for root in ROOTS:
        candidate = os.path.join(root, rel)
        if os.path.isfile(candidate):
            return candidate

    # Last resort: try matching just the filename in every root (recursive)
    basename = os.path.basename(rel)
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            if basename in files:
                return os.path.join(dirpath, basename)

    return None


def load_pages(index_path: str) -> list[dict]:
    """Load the pages list from rotem_index.html.

    The file may be:
      - Pure JSON array
      - HTML with an embedded <script> containing a JSON array/object
      - JSON object with a 'pages' key
    """
    raw = Path(index_path).read_text(encoding="utf-8", errors="replace")

    # Try parsing as pure JSON first
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Look for common keys
            for key in ("pages", "items", "files", "entries"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If the dict itself looks like a single page, wrap it
            if "path" in data or "url" in data or "file" in data:
                return [data]
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from <script> tags or embedded JS
    json_patterns = [
        r"(?:var|let|const)\s+\w+\s*=\s*(\[[\s\S]*?\]);",
        r"(?:var|let|const)\s+\w+\s*=\s*(\{[\s\S]*?\});",
        r"(<script[^>]*>)([\s\S]*?)(</script>)",
    ]
    for pattern in json_patterns[:2]:
        m = re.search(pattern, raw)
        if m:
            try:
                data = json.loads(m.group(1))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    for key in ("pages", "items", "files", "entries"):
                        if key in data and isinstance(data[key], list):
                            return data[key]
            except json.JSONDecodeError:
                continue

    # Fallback: find all JSON arrays in the file
    for m in re.finditer(r"\[[\s\S]*?\]", raw):
        try:
            data = json.loads(m.group())
            if isinstance(data, list) and len(data) > 0:
                return data
        except json.JSONDecodeError:
            continue

    print(f"ERROR: Could not parse pages from {index_path}", file=sys.stderr)
    sys.exit(1)


def get_page_path(page) -> str:
    """Extract the file path from a page entry (string or dict)."""
    if isinstance(page, str):
        return page
    if isinstance(page, dict):
        for key in ("path", "file", "url", "src", "href", "location", "filepath"):
            if key in page:
                val = page[key]
                if isinstance(val, str):
                    return val
    return str(page)


# ── Fix functions ──────────────────────────────────────────────────────────────

def fix_csp(html: str) -> tuple[str, bool]:
    """Inject CSP meta tag into <head>."""
    if "Content-Security-Policy" in html:
        return html, False
    # Insert after <head> (or <head ...>)
    pattern = re.compile(r"(<head[^>]*>)", re.IGNORECASE)
    m = pattern.search(html)
    if m:
        pos = m.end()
        html = html[:pos] + "\n" + CSP_META + "\n" + html[pos:]
        return html, True
    # No <head> tag — prepend
    html = CSP_META + "\n" + html
    return html, True


def fix_module_scripts(html: str) -> tuple[str, bool]:
    """Remove type=\"module\" from script tags referencing .tsx files."""
    pattern = re.compile(
        r'<script\s+type\s*=\s*["\']module["\']\s+src\s*=\s*["\']([^"\']*\.tsx)["\']',
        re.IGNORECASE,
    )
    if not pattern.search(html):
        return html, False
    html = pattern.sub(r'<script src="\1"', html)
    return html, True


def fix_shim(html: str) -> tuple[str, bool]:
    """Add compatibility shim before </body>."""
    if "RoTEM compatibility shim" in html:
        return html, False
    idx = html.lower().rfind("</body>")
    if idx != -1:
        html = html[:idx] + COMPAT_SHIM + "\n" + html[idx:]
    else:
        html = html + "\n" + COMPAT_SHIM
    return html, True


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading pages from {INDEX_FILE} ...")
    pages = load_pages(INDEX_FILE)
    print(f"Found {len(pages)} pages.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report = {
        "total": len(pages),
        "copied": 0,
        "not_found": 0,
        "pages": [],
    }

    used_names: set[str] = set()

    for i, page in enumerate(pages, 1):
        original_path = get_page_path(page)
        slug = slugify(original_path)

        # Ensure unique name
        if slug in used_names:
            base, ext = os.path.splitext(slug)
            counter = 2
            while f"{base}_{counter}{ext}" in used_names:
                counter += 1
            slug = f"{base}_{counter}{ext}"
        used_names.add(slug)

        dest = os.path.join(OUTPUT_DIR, slug)

        # Find the source file
        source = find_file(original_path)
        if source is None:
            report["not_found"] += 1
            report["pages"].append({
                "original": original_path,
                "fixed": dest.replace("\\", "/"),
                "status": "not_found",
                "fixes_applied": [],
            })
            print(f"  [{i}/{len(pages)}] NOT FOUND: {original_path}")
            continue

        # Read source
        try:
            html = Path(source).read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            report["pages"].append({
                "original": original_path,
                "fixed": dest.replace("\\", "/"),
                "status": "error",
                "fixes_applied": [],
                "error": str(e),
            })
            print(f"  [{i}/{len(pages)}] ERROR reading: {source} — {e}")
            continue

        # Apply fixes
        fixes = []

        html, applied = fix_csp(html)
        if applied:
            fixes.append("csp")

        html, applied = fix_module_scripts(html)
        if applied:
            fixes.append("module_scripts")

        html, applied = fix_shim(html)
        if applied:
            fixes.append("shim")

        # Write fixed file
        try:
            Path(dest).write_text(html, encoding="utf-8")
            report["copied"] += 1
            report["pages"].append({
                "original": original_path,
                "fixed": dest.replace("\\", "/"),
                "status": "ok",
                "fixes_applied": fixes,
            })
            print(f"  [{i}/{len(pages)}] OK: {original_path} → {slug}  fixes={fixes}")
        except Exception as e:
            report["pages"].append({
                "original": original_path,
                "fixed": dest.replace("\\", "/"),
                "status": "error",
                "fixes_applied": fixes,
                "error": str(e),
            })
            print(f"  [{i}/{len(pages)}] ERROR writing: {dest} — {e}")

    # Write report
    Path(REPORT_FILE).write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print(f"DONE — Total: {report['total']}, "
          f"Copied: {report['copied']}, "
          f"Not found: {report['not_found']}")
    print(f"Report: {REPORT_FILE}")
    print(f"Fixed files: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
