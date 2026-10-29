# gamblingliteracy.org

Gambling Literacy: youth gambling education and advocacy for the adults who reach young people. A small static site built the same way as [gambling-research.com](https://github.com/Chris-Beerman/gambling-research.com): Markdown pages rendered with Jinja2 by a short Python script, built and deployed by GitHub Actions to GitHub Pages, with the domains kept at Squarespace.

## How it works

```
config/site.yml          names, contact address, navigation, the three-site footer, helplines
content/pages/*.md       every page: YAML front matter + Markdown
templates/               base.html (masthead, footer), page.html, home.html, sitemap.xml
static/                  style.css, mark.svg, og.png, illustrations/*.svg
pipeline/build.py        renders _site/ from content/ and templates/
pipeline/illustrate.py   draws the illustration set from code (python -m pipeline.illustrate)
tests/test_site.py       links, anchors, images, alt text, titles; runs on every deploy
.github/workflows/       on every push to main: build, test, deploy to GitHub Pages
```

A push to `main` rebuilds and publishes the site in about a minute. If a test fails (a broken internal link, an image without alt text), nothing is published.

## Editing a page

Each page is one Markdown file in `content/pages/`. The front matter sets the title, the SEO title and description, the hero illustration, and the review dates:

```
---
title: Understanding risk
slug: educators/understanding-risk      # the URL
description: For search results and link previews.
deck: The sentence under the title.
hero: understanding-risk                # a file in static/illustrations/
hero_alt: What the illustration shows.
reviewed: 2026-10-25                    # shown on the page; update when you recheck it
next_review: 2027-04-01
---
```

Two shortcodes keep the editorial labels and the illustrations consistent:

```
::: research                 Research finding (teal)
::: clinical                 Clinical perspective (navy)
::: advocacy                 Advocacy recommendation (orange)
::: practical                Practical suggestion (mustard)
::: open                     Open question (dashed)
::: proposed                 Proposed work (dashed orange)
::: try "Custom title"       Activity box
::: review                   Flagged for editorial review (red; never publish one)
Text in Markdown.
:::

{{ figure social-influence | Alt text describing the scene | Optional caption }}
```

Citations are Markdown footnotes (`[^dowling2017]` in the text, `[^dowling2017]: Full citation. [DOI](https://doi.org/...)` at the bottom) and render as a numbered source list. `{{CONTACT}}` is replaced with `contact_email` from `config/site.yml`.

## Illustrations

`python -m pipeline.illustrate` redraws every scene into `static/illustrations/`. The palette, the six recurring characters and the props are defined once at the top of `pipeline/illustrate.py`, so a change there changes every scene. The rules are written up for people at [/style-guide/](https://gamblingliteracy.org/style-guide/).

## Local use

```
pip install -r requirements.txt pytest html5lib
python -m pipeline.build
python -m pytest -q
python -m http.server -d _site 8000
```

## Handoff: domains and mail

1. GitHub Pages: Settings → Pages → Source "GitHub Actions"; custom domain `gamblingliteracy.org`; tick "Enforce HTTPS" once the certificate is issued.
2. DNS at Squarespace for `gamblingliteracy.org`: A records for `@` to 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; CNAME for `www` to `chris-beerman.github.io`. Remove any Squarespace default records that conflict.
3. `gamblingliteracy.com`: forward (301, permanent) to `https://gamblingliteracy.org` in Squarespace's domain settings.
4. Mail: `hello@gamblingliteracy.org` is the contact address on the site; set up forwarding for it in Squarespace (Domains → gamblingliteracy.org → Email → Email forwarding) and change `contact_email` in `config/site.yml` if a different address is used.

## Review schedule

Every page shows a "Reviewed" date. At each review, recheck: helpline numbers and text codes (`config/site.yml` and `/get-help/`), legal gambling ages, every statistic against its source, and the links in the source lists.

## Licences

Code MIT; editorial content and illustrations CC BY 4.0. See `LICENSE`.
