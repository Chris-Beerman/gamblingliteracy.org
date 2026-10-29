"""Research charts, built as HTML and CSS so they use the site's fonts at real sizes.

Used in pages with the shortcode  {{ chart <name> }}.

Rules (see /style-guide/#charts): one series, one hue (teal), values labeled
directly, bars anchored to a zero baseline, every chart says what is measured,
in whom, where and when, and carries its source and a table of the numbers.
"""
from __future__ import annotations

import html



def _hbar(rows, max_value, unit=""):
    """Horizontal bars built in HTML and CSS rather than SVG, so the text keeps
    its real size at every screen width. Label above each bar, value at the
    bar's end, bars anchored to a shared baseline. rows = [(label, value, value_label)]."""
    out = ['<div class="hbars" aria-hidden="true">']
    for label, value, vlabel in rows:
        pct = max(0.5, 100 * value / max_value)
        out.append(
            f'<div class="hbar" title="{html.escape(label)}: {html.escape(vlabel)}">'
            f'<span class="hbar-label">{html.escape(label)}</span>'
            f'<span class="hbar-track"><span class="hbar-fill" style="width:{pct:.1f}%"></span>'
            f'<span class="hbar-value">{html.escape(vlabel)}</span></span></div>'
        )
    out.append("</div>")
    return "".join(out)


def _figure(name, title, subtitle, svg, table_head, table_rows, source_html, note):
    rows = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>" for r in table_rows)
    head = "".join(f"<th scope=\"col\">{html.escape(h)}</th>" for h in table_head)
    return (
        f'<figure class="chart" id="chart-{name}" aria-labelledby="chart-{name}-t">'
        f'<p class="chart-title" id="chart-{name}-t">{title}</p>'
        f'<p class="chart-sub">{subtitle}</p>'
        f'{svg}'
        f'<details class="chart-table"><summary>Show the numbers as a table</summary>'
        f'<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></details>'
        f'<figcaption><span class="chart-note">{note}</span> <span class="chart-source">Source: {source_html}</span></figcaption>'
        f'</figure>'
    )


def keen_funnel():
    rows = [("Studies reviewed", 19, "19"), ("Measured gambling behavior", 9, "9"), ("Found a behavior change", 5, "5")]
    return _figure(
        "keen",
        "Most school programs have never been tested on behavior",
        "Evaluations of school-based gambling education programs, systematic review, 2017",
        _hbar(rows, 19),
        ["Step", "Number of studies"],
        [(r[0], r[1]) for r in rows],
        'Keen, Blaszczynski &amp; Anjoul, <em>Journal of Gambling Studies</em>, 2017. <a href="https://doi.org/10.1007/s10899-016-9641-7">doi:10.1007/s10899-016-9641-7</a>',
        "Every study found changes in knowledge or beliefs. The five behavior changes were measured over short follow-up periods.",
    )


def minnesota_grades():
    rows = [("8th grade", 32, "about 32%"), ("9th grade", 29, "about 29%"), ("11th grade", 28, "about 28%")]
    return _figure(
        "minnesota",
        "Gambling starts before high school",
        "Share of Minnesota public school students who gambled in the past year, by grade, 2019 Minnesota Student Survey",
        _hbar(rows, 40),
        ["Grade", "Gambled in the past year"],
        [(r[0], r[2]) for r in rows],
        'Park E, <em>Gambling Behaviors of MN Students: Findings from the 2019 Minnesota Student Survey</em>, Minnesota Department of Human Services, October 2020. <a href="https://www.developtoolmn.org/dhs/assets/gambling-behavior-mn-students_tcm1053-450190.pdf">PDF</a>',
        "“Gambling” here includes playing cards and betting on games of skill (such as video games, pool or bowling) as well as the lottery, casinos and online gambling, so most of it is informal. One state, one year.",
    )


CHARTS = {"keen-funnel": keen_funnel, "minnesota-grades": minnesota_grades}
