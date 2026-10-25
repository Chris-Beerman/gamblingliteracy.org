"""Render the static site from content/ and templates/ into _site/.

    python -m pipeline.build

Pages are Markdown files in content/pages/ with YAML front matter. Two
shortcodes keep the editorial labels and illustrations consistent:

    ::: research            a labelled box: research, clinical, advocacy,
    Text in Markdown.       practical, open, proposed, try, review
    :::

    ::: practical "Try this in class"     (an optional custom title)
    :::

    {{ figure social-influence | Alt text describing the scene | Optional caption }}

Citations use Markdown footnotes ([^key]) and render as a numbered source list.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "pages"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
SITE = ROOT / "_site"

MD_EXT = ["tables", "attr_list", "footnotes", "sane_lists", "md_in_html", "toc", "def_list", "smarty"]
MD_CFG = {"footnotes": {"BACKLINK_TEXT": "↩", "BACKLINK_TITLE": "Back to the text"}, "toc": {"permalink": False}}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# The labels that tell a reader what kind of statement they are reading.
NOTE_LABELS = {
    "research": "Research finding",
    "clinical": "Clinical perspective",
    "advocacy": "Advocacy recommendation",
    "practical": "Practical suggestion",
    "open": "Open question",
    "proposed": "Proposed",
    "try": "Try this",
    "review": "Flagged for editorial review",
}


def fmt_date(value, style="long"):
    if not value:
        return ""
    if isinstance(value, str):
        value = dt.date.fromisoformat(value[:10])
    if style == "month":
        return f"{MONTHS[value.month - 1]} {value.year}"
    return f"{MONTHS[value.month - 1]} {value.day}, {value.year}"


FIG_RE = re.compile(r"^\{\{\s*figure\s+([a-z0-9-]+)\s*\|\s*(.*?)\s*(?:\|\s*(.*?)\s*)?\}\}\s*$", re.M)
NOTE_OPEN = re.compile(r'^:::\s*([a-z]+)(?:\s+"(.*?)")?\s*$')


def figure_html(name: str, alt: str, caption: str | None, cls: str = "figure") -> str:
    svg = STATIC / "illustrations" / f"{name}.svg"
    if not svg.exists():
        raise SystemExit(f"figure '{name}' has no file at {svg}")
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg.read_text(encoding="utf-8"))
    w, h = (m.group(1), m.group(2)) if m else ("760", "440")
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (f'<figure class="{cls}"><img src="/static/illustrations/{name}.svg" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">{cap}</figure>')


def preprocess(text: str, site: dict) -> str:
    text = text.replace("{{CONTACT}}", site["contact_email"])
    text = FIG_RE.sub(lambda m: "\n" + figure_html(m.group(1), m.group(2), m.group(3)) + "\n", text)
    out, stack = [], []
    for line in text.split("\n"):
        m = NOTE_OPEN.match(line)
        if m and m.group(1) in NOTE_LABELS:
            kind, title = m.group(1), m.group(2)
            label = title or NOTE_LABELS[kind]
            out += ["", f'<aside class="note note-{kind}" markdown="1">', f'<p class="note-label">{label}</p>', ""]
            stack.append(kind)
        elif line.strip() == ":::" and stack:
            stack.pop()
            out += ["", "</aside>", ""]
        else:
            out.append(line)
    if stack:
        raise SystemExit(f"unclosed ::: {stack[-1]} block")
    return "\n".join(out)


def read_page(path: Path, site: dict) -> tuple[dict, str, list]:
    text = path.read_text(encoding="utf-8")
    meta: dict = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        text = text[m.end():]
    md = markdown.Markdown(extensions=MD_EXT, extension_configs=MD_CFG, output_format="html5")
    html = md.convert(preprocess(text, site))
    # Footnotes become a titled source list.
    html = html.replace('<div class="footnote">', '<section class="sources" aria-labelledby="sources-h"><h2 id="sources-h">Sources</h2>', 1)
    if '<section class="sources"' in html:
        html = re.sub(r'</ol>\s*</div>\s*$', '</ol>\n</section>', html)
        html = html.replace('<hr>\n<ol>', '<ol>', 1)
    toc = [t for t in md.toc_tokens if t["level"] == 2] if hasattr(md, "toc_tokens") else []
    return meta, html, toc


class Builder:
    def __init__(self):
        self.site = yaml.safe_load((ROOT / "config" / "site.yml").read_text(encoding="utf-8"))
        self.env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "xml"]), trim_blocks=True, lstrip_blocks=True)
        self.env.filters["fmt_date"] = fmt_date
        self.env.globals["figure"] = figure_html
        self.urls: list[tuple[str, str]] = []
        self.today = dt.date.today().isoformat()

    def render(self, template: str, out: str, **ctx):
        path = "/" + out.removesuffix("index.html")
        html = self.env.get_template(template).render(site=self.site, path=path, nav=self.site["nav"], today=self.today, **ctx)
        dest = SITE / out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        page = ctx.get("page") or {}
        if out.endswith("index.html") and not page.get("noindex"):
            self.urls.append((path, str(page.get("reviewed") or self.today)))

    def build(self):
        if SITE.exists():
            shutil.rmtree(SITE)
        SITE.mkdir()
        shutil.copytree(STATIC, SITE / "static")
        pages = []
        for path in sorted(CONTENT.glob("*.md")):
            meta, html, toc = read_page(path, self.site)
            meta.setdefault("slug", path.stem)
            pages.append((meta, html, toc))
        by_slug = {m["slug"]: m for m, _, _ in pages}
        for meta, html, toc in pages:
            slug = meta["slug"]
            out = "index.html" if slug == "home" else f"{slug}/index.html"
            if slug == "404":
                out = "404.html"
            self.render(meta.get("template", "page") + ".html", out, page=meta, body=html, toc=toc, pages=by_slug)
        self.render("sitemap.xml", "sitemap.xml", urls=sorted(self.urls))
        (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {self.site['url']}/sitemap.xml\n", encoding="utf-8")
        (SITE / "CNAME").write_text(self.site["canonical_domain"] + "\n", encoding="utf-8")
        (SITE / ".nojekyll").write_text("", encoding="utf-8")
        print(f"built {len(pages)} pages into {SITE}", file=sys.stderr)


def main() -> int:
    Builder().build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
