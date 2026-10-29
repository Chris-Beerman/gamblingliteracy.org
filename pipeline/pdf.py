"""Print the downloadable PDFs from the built site.

    python -m pipeline.build && python -m pipeline.pdf

Any page whose front matter has `pdf: <name>` is printed to
_site/downloads/<name>.pdf using the site's own print stylesheet, so the PDF
and a printout from the browser always match. Needs Playwright with Chromium
(`pip install playwright && python -m playwright install chromium`).
"""
from __future__ import annotations

import functools
import http.server
import re
import sys
import threading
from pathlib import Path

import yaml

from .build import CONTENT, SITE


def pdf_pages() -> list[tuple[str, str]]:
    """(url path, pdf name) for every page that asks for a PDF."""
    out = []
    for path in sorted(CONTENT.glob("*.md")):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", path.read_text(encoding="utf-8"), re.S)
        meta = yaml.safe_load(m.group(1)) if m else {}
        if meta and meta.get("pdf"):
            slug = meta.get("slug", path.stem)
            out.append(("/" if slug == "home" else f"/{slug}/", meta["pdf"]))
    return out


def make_pdfs(site_dir: Path = SITE) -> dict[str, int]:
    from playwright.sync_api import sync_playwright

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(site_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    (site_dir / "downloads").mkdir(exist_ok=True)
    counts = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            for url, name in pdf_pages():
                page.goto(base + url, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                dest = site_dir / "downloads" / f"{name}.pdf"
                page.pdf(path=str(dest), prefer_css_page_size=True, print_background=True)
                counts[name] = dest.read_bytes().count(b"/Type /Page") - dest.read_bytes().count(b"/Type /Pages")
            browser.close()
    finally:
        server.shutdown()
    return counts


def main() -> int:
    for name, n in make_pdfs().items():
        print(f"{name}.pdf: {n} page{'s' if n != 1 else ''}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
