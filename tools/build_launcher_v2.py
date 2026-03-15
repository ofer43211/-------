#!/usr/bin/env python3
"""
RoTEM Launcher Builder v2 — generates a single HTML launcher page
that links to all fixed HTML pages in a directory.

Usage:
    python build_launcher_v2.py --root J:\\html\\rotem_fixed --out J:\\html\\rotem_launcher_fixed.html

Options:
    --root DIR    Directory containing fixed HTML files (default: J:\\html\\rotem_fixed)
    --out FILE    Output launcher HTML file (default: J:\\html\\rotem_launcher_fixed.html)
    --report FILE Path to fix_report.json for metadata (default: J:\\html\\fix_report.json)
    --title STR   Page title (default: "RoTEM Launcher")
    --port INT    Local server port for links (default: 9999)
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

DEFAULT_ROOT = r"J:\html\rotem_fixed"
DEFAULT_OUT = r"J:\html\rotem_launcher_fixed.html"
DEFAULT_REPORT = r"J:\html\fix_report.json"
DEFAULT_TITLE = "RoTEM Launcher"
DEFAULT_PORT = 9999


def natural_sort_key(s: str):
    """Sort strings with embedded numbers in natural order."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", s)
    ]


def load_report(report_path: str) -> dict:
    """Load the fix report if available."""
    try:
        return json.loads(Path(report_path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def build_page_entry(filename: str, report_data: dict, root_dir: str, port: int) -> dict:
    """Build metadata for a single page."""
    # Find matching report entry
    report_info = None
    if "pages" in report_data:
        for p in report_data["pages"]:
            fixed_name = os.path.basename(p.get("fixed", ""))
            if fixed_name == filename:
                report_info = p
                break

    # Build relative URL for the local server
    rel_path = f"rotem_fixed/{filename}"
    url = f"http://localhost:{port}/{rel_path}"

    # Derive a human-readable title from the filename
    title = filename.replace(".html", "").replace("_", " ").replace("-", " ").strip()
    title = re.sub(r"\s+", " ", title).title()

    entry = {
        "filename": filename,
        "title": title,
        "url": url,
        "rel_path": rel_path,
    }

    if report_info:
        entry["original"] = report_info.get("original", "")
        entry["status"] = report_info.get("status", "unknown")
        entry["fixes"] = report_info.get("fixes_applied", [])

    return entry


def generate_html(entries: list[dict], title: str, report_data: dict) -> str:
    """Generate the launcher HTML page."""
    total = report_data.get("total", len(entries))
    copied = report_data.get("copied", len(entries))
    not_found = report_data.get("not_found", 0)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build page cards
    cards_html = []
    for i, e in enumerate(entries, 1):
        status_class = e.get("status", "ok")
        fixes = ", ".join(e.get("fixes", [])) or "none"
        original = e.get("original", e["filename"])

        cards_html.append(f"""\
      <div class="card {status_class}" onclick="window.open('{e['url']}','_blank')">
        <div class="card-num">{i}</div>
        <div class="card-body">
          <div class="card-title">{e['title']}</div>
          <div class="card-meta">{original}</div>
          <div class="card-fixes">Fixes: {fixes}</div>
        </div>
        <div class="card-arrow">&#8599;</div>
      </div>""")

    cards = "\n".join(cards_html)

    return f"""\
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #0a0a1a;
      --card-bg: #12122a;
      --card-hover: #1a1a3a;
      --accent: #4fc3f7;
      --accent2: #7c4dff;
      --text: #e0e0e0;
      --text-dim: #808090;
      --ok: #4caf50;
      --error: #f44336;
      --not-found: #ff9800;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 20px;
    }}
    .header {{
      text-align: center;
      padding: 30px 20px;
      margin-bottom: 20px;
    }}
    .header h1 {{
      font-size: 2.5rem;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 10px;
    }}
    .stats {{
      display: flex;
      justify-content: center;
      gap: 30px;
      margin: 20px 0;
      flex-wrap: wrap;
    }}
    .stat {{
      text-align: center;
      padding: 10px 20px;
      background: var(--card-bg);
      border-radius: 10px;
      min-width: 120px;
    }}
    .stat-num {{
      font-size: 2rem;
      font-weight: bold;
      color: var(--accent);
    }}
    .stat-label {{
      font-size: 0.85rem;
      color: var(--text-dim);
      margin-top: 4px;
    }}
    .search-box {{
      display: flex;
      justify-content: center;
      margin: 20px 0;
    }}
    .search-box input {{
      width: 100%;
      max-width: 500px;
      padding: 12px 20px;
      border: 1px solid #333;
      border-radius: 25px;
      background: var(--card-bg);
      color: var(--text);
      font-size: 1rem;
      outline: none;
      transition: border-color 0.3s;
    }}
    .search-box input:focus {{
      border-color: var(--accent);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 12px;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .card {{
      background: var(--card-bg);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      transition: background 0.2s, transform 0.15s;
      border-right: 4px solid var(--ok);
    }}
    .card:hover {{
      background: var(--card-hover);
      transform: translateY(-2px);
    }}
    .card.not_found {{
      border-right-color: var(--not-found);
      opacity: 0.6;
    }}
    .card.error {{
      border-right-color: var(--error);
      opacity: 0.6;
    }}
    .card-num {{
      font-size: 1.2rem;
      font-weight: bold;
      color: var(--accent);
      min-width: 36px;
      text-align: center;
    }}
    .card-body {{
      flex: 1;
      overflow: hidden;
    }}
    .card-title {{
      font-weight: 600;
      font-size: 0.95rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .card-meta {{
      font-size: 0.75rem;
      color: var(--text-dim);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 2px;
    }}
    .card-fixes {{
      font-size: 0.7rem;
      color: var(--accent2);
      margin-top: 2px;
    }}
    .card-arrow {{
      font-size: 1.3rem;
      color: var(--text-dim);
    }}
    .footer {{
      text-align: center;
      padding: 30px;
      color: var(--text-dim);
      font-size: 0.8rem;
    }}
    .hidden {{ display: none !important; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <p style="color:var(--text-dim)">Generated: {generated}</p>
    <div class="stats">
      <div class="stat">
        <div class="stat-num">{total}</div>
        <div class="stat-label">Total Pages</div>
      </div>
      <div class="stat">
        <div class="stat-num">{copied}</div>
        <div class="stat-label">Fixed &amp; Copied</div>
      </div>
      <div class="stat">
        <div class="stat-num">{not_found}</div>
        <div class="stat-label">Not Found</div>
      </div>
    </div>
    <div class="search-box">
      <input type="text" id="search" placeholder="Search pages..." oninput="filterCards(this.value)">
    </div>
  </div>

  <div class="grid" id="grid">
{cards}
  </div>

  <div class="footer">
    RoTEM Project &mdash; {len(entries)} pages loaded
  </div>

  <script>
    function filterCards(q) {{
      q = q.toLowerCase();
      document.querySelectorAll('.card').forEach(function(card) {{
        var text = card.textContent.toLowerCase();
        card.classList.toggle('hidden', q && text.indexOf(q) === -1);
      }});
    }}
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="RoTEM Launcher Builder v2")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Directory with fixed HTML files")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output launcher HTML file")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="Path to fix_report.json")
    parser.add_argument("--title", default=DEFAULT_TITLE, help="Launcher page title")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local server port")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: Root directory not found: {args.root}")
        print("Run fix_html.py first to create the fixed HTML files.")
        return 1

    # Collect HTML files
    html_files = sorted(
        [f.name for f in root.iterdir() if f.suffix.lower() == ".html"],
        key=natural_sort_key,
    )

    if not html_files:
        print(f"No HTML files found in {args.root}")
        return 1

    print(f"Found {len(html_files)} HTML files in {args.root}")

    # Load report data
    report_data = load_report(args.report)

    # Build entries
    entries = [
        build_page_entry(f, report_data, args.root, args.port)
        for f in html_files
    ]

    # Generate and write launcher
    html = generate_html(entries, args.title, report_data)
    Path(args.out).write_text(html, encoding="utf-8")

    print(f"Launcher written to {args.out}")
    print(f"Open: http://localhost:{args.port}/rotem_launcher_fixed.html")
    return 0


if __name__ == "__main__":
    exit(main() or 0)
