"""Checks run on every build: links, anchors, images, alt text, titles."""
import os
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from pipeline.build import Builder, SITE

DOMAIN = "https://gamblingliteracy.org"


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.ids, self.title, self.desc, self.h1 = [], [], set(), None, None, 0
        self._in_title = False
        self._svg = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "svg":
            self._svg += 1
        if tag == "title" and not self._svg:  # SVG <title> elements are tooltips, not the page title
            self._in_title = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag == "h1":
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag == "svg":
            self._svg -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


@pytest.fixture(scope="session")
def pages():
    # CI builds and prints the PDFs before the tests run (GL_SKIP_BUILD=1);
    # locally the fixture does both, so download links can be checked too.
    if not os.environ.get("GL_SKIP_BUILD"):
        Builder().build()
        from pipeline.pdf import make_pdfs
        make_pdfs()
    out = {}
    for f in SITE.rglob("*.html"):
        c = Collector()
        c.feed(f.read_text(encoding="utf-8"))
        out[f] = c
    return out


def resolve(href: str) -> tuple[Path | None, str]:
    path, _, frag = href.partition("#")
    if path.startswith(DOMAIN):
        path = path[len(DOMAIN):] or "/"
    if not path.startswith("/"):
        return None, frag
    target = SITE / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    return target, frag


def test_internal_links_and_anchors(pages, ):
    bad = []
    for f, c in pages.items():
        for href in c.links:
            if href.startswith(("mailto:", "tel:", "http://", "https://")) and not href.startswith(DOMAIN):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in c.ids:
                    bad.append(f"{f.relative_to(SITE)}: missing anchor {href}")
                continue
            target, frag = resolve(href)
            if target is None or not target.exists():
                bad.append(f"{f.relative_to(SITE)}: broken link {href}")
            elif frag and target.suffix == ".html" and frag not in pages[target].ids:
                bad.append(f"{f.relative_to(SITE)}: missing anchor {href}")
    assert not bad, "\n".join(bad)


def test_images_exist_and_have_alt(pages):
    bad = []
    for f, c in pages.items():
        for img in c.imgs:
            if "alt" not in img:
                bad.append(f"{f.relative_to(SITE)}: img without alt {img.get('src')}")
            target, _ = resolve(img.get("src", ""))
            if target is None or not target.exists():
                bad.append(f"{f.relative_to(SITE)}: missing image {img.get('src')}")
    assert not bad, "\n".join(bad)


def test_every_page_has_title_description_and_one_h1(pages):
    bad = [str(f.relative_to(SITE)) for f, c in pages.items() if not c.title or not c.desc or c.h1 != 1]
    assert not bad, bad


def test_no_unreplaced_placeholders():
    bad = [str(f) for f in SITE.rglob("*.html") if re.search(r"\{\{|\}\}|:::", re.sub(r"<script.*?</script>", "", f.read_text(encoding="utf-8"), flags=re.S))]
    assert not bad, bad


def test_html_parses_strictly(pages):
    """html5lib in strict mode raises on the parse errors a browser would
    silently recover from (an unescaped quote inside an attribute, say)."""
    import html5lib

    bad = []
    for f in pages:
        parser = html5lib.HTMLParser(strict=True)
        try:
            parser.parse(f.read_text(encoding="utf-8"))
        except Exception as e:  # html5lib.html5parser.ParseError
            bad.append(f"{f.relative_to(SITE)}: {e}")
    assert not bad, "\n".join(bad)


def test_titles_and_descriptions_fit_search_results(pages):
    long_titles = [f"{f.relative_to(SITE)} ({len(c.title)}): {c.title}" for f, c in pages.items() if c.title and len(c.title) > 62]
    long_descs = [f"{f.relative_to(SITE)} ({len(c.desc)})" for f, c in pages.items() if c.desc and len(c.desc) > 160]
    assert not long_titles, "titles over 62 characters:\n" + "\n".join(long_titles)
    assert not long_descs, "descriptions over 160 characters:\n" + "\n".join(long_descs)


def test_pdfs_exist_and_guide_fits_four_pages(pages):
    from pipeline.pdf import pdf_pages

    for _, name in pdf_pages():
        f = SITE / "downloads" / f"{name}.pdf"
        assert f.exists() and f.stat().st_size > 10_000, f"missing or empty PDF: {name}"
    guide = (SITE / "downloads" / "conversation-guide.pdf").read_bytes()
    n = guide.count(b"/Type /Page") - guide.count(b"/Type /Pages")
    assert n <= 4, f"the conversation guide prints to {n} pages; keep it to four"
    for name in ("conversation-guide-one-page", "parents-one-page"):
        one = (SITE / "downloads" / f"{name}.pdf").read_bytes()
        assert one.count(b"/Type /Page") - one.count(b"/Type /Pages") == 1, f"{name} must fit one page"
