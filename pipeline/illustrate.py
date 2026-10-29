"""Draw the Gambling Literacy illustration set as SVG files.

    python -m pipeline.illustrate        # writes static/illustrations/*.svg

Every scene is built from the same parts (the palette, the cast, the
background blob, the props), so the set stays consistent and new scenes
can be added without drawing from scratch. The rules these functions
encode are written up for people at /style-guide/.
"""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "illustrations"

# ------------------------------------------------------------------ palette
C = {
    "paper": "#FBF7F0",
    "navy": "#1B2A41",
    "navy2": "#33445E",
    "teal": "#2F7F7A",
    "teal2": "#5FA39C",
    "tealtint": "#D5EAE6",
    "orange": "#E0855A",
    "orangetint": "#F8DCCB",
    "sand": "#F1E4CF",
    "mustard": "#E9B95E",
    "sage": "#A9C6A8",
    "white": "#FFFFFF",
    "blush": "#F0A487",
}
SKIN = ["#F3D0AE", "#E3AC84", "#C98A5E", "#9C6340", "#6F432B"]
HAIR = {"black": "#24202A", "brown": "#6B4128", "dark": "#3A2A26", "grey": "#9A9AA3", "auburn": "#8A4A2E"}

# ------------------------------------------------------------------ the cast
# Each character keeps the same colours, hair and accessories in every scene.
CAST = {
    "maya":   {"name": "Maya",       "role": "student, 13", "kind": "teen",  "skin": SKIN[3], "hair": "puff",  "hair_c": HAIR["black"], "top": C["teal"],    "pants": C["navy"]},
    "theo":   {"name": "Theo",       "role": "student, 16", "kind": "teen",  "skin": SKIN[0], "hair": "swoop", "hair_c": HAIR["auburn"], "top": C["orange"], "pants": C["navy2"]},
    "amira":  {"name": "Amira",      "role": "student, 15", "kind": "teen",  "skin": SKIN[2], "hair": "hijab", "hair_c": C["teal2"],     "top": C["navy2"],  "pants": C["mustard"]},
    "rivera": {"name": "Ms. Rivera", "role": "teacher",     "kind": "adult", "skin": SKIN[2], "hair": "bob",   "hair_c": HAIR["dark"],  "top": C["navy"],   "pants": C["navy2"], "glasses": True},
    "coach":  {"name": "Coach Ben",  "role": "coach",       "kind": "adult", "skin": SKIN[4], "hair": "cap",   "hair_c": C["orange"],    "top": C["teal"],   "pants": C["navy"], "whistle": True},
    "sam":    {"name": "Sam",        "role": "parent",      "kind": "adult", "skin": SKIN[1], "hair": "bun",   "hair_c": HAIR["brown"], "top": C["sage"],   "pants": C["navy"]},
}

STROKE = 2.6  # the one line weight for faces and details at scale 1


def f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ------------------------------------------------------------------ primitives
def blob(cx, cy, rx, ry, fill, seed=0, opacity=1.0):
    """A soft, irregular rounded shape: the background behind every scene."""
    pts = []
    n = 8
    for i in range(n):
        a = 2 * math.pi * i / n
        wob = 1 + 0.07 * math.sin(3 * a + seed) + 0.05 * math.cos(2 * a + seed * 1.7)
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    d = []
    for i in range(n):
        p0 = pts[i - 1]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        m1 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        m2 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        if i == 0:
            d.append(f"M{f(m1[0])},{f(m1[1])}")
        d.append(f"Q{f(p1[0])},{f(p1[1])} {f(m2[0])},{f(m2[1])}")
    op = f' opacity="{opacity}"' if opacity != 1 else ""
    return f'<path d="{" ".join(d)}Z" fill="{fill}"{op}/>'


def dots(points, fill, r=4):
    return "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}"/>' for x, y in points)


def sparkle(x, y, s, fill):
    return (f'<path d="M{f(x)},{f(y - s)} Q{f(x)},{f(y)} {f(x + s)},{f(y)} Q{f(x)},{f(y)} {f(x)},{f(y + s)} '
            f'Q{f(x)},{f(y)} {f(x - s)},{f(y)} Q{f(x)},{f(y)} {f(x)},{f(y - s)}Z" fill="{fill}"/>')


def bubble(x, y, w, h, fill, tail="left", content=""):
    """Speech bubble with a rounded tail. (x, y) is the top-left corner."""
    r = min(h / 2, 22)
    if tail == "left":
        t = f'<path d="M{f(x + 18)},{f(y + h - 4)} L{f(x + 6)},{f(y + h + 16)} L{f(x + 36)},{f(y + h - 4)}Z" fill="{fill}"/>'
    elif tail == "right":
        t = f'<path d="M{f(x + w - 36)},{f(y + h - 4)} L{f(x + w - 6)},{f(y + h + 16)} L{f(x + w - 18)},{f(y + h - 4)}Z" fill="{fill}"/>'
    else:
        t = ""
    return f'<g><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(r)}" fill="{fill}"/>{t}{content}</g>'


def shadow(cx, y, rx):
    return f'<ellipse cx="{f(cx)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(rx * 0.12)}" fill="{C["navy"]}" opacity=".08"/>'


# ------------------------------------------------------------------ props
def die(x, y, s, face=5, fill=None, rot=0):
    fill = fill or C["white"]
    pips = {
        1: [(0.5, 0.5)], 2: [(0.27, 0.27), (0.73, 0.73)], 3: [(0.27, 0.27), (0.5, 0.5), (0.73, 0.73)],
        4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
        5: [(0.27, 0.27), (0.73, 0.27), (0.5, 0.5), (0.27, 0.73), (0.73, 0.73)],
        6: [(0.27, 0.25), (0.73, 0.25), (0.27, 0.5), (0.73, 0.5), (0.27, 0.75), (0.73, 0.75)],
    }[face]
    p = "".join(f'<circle cx="{f(s * a)}" cy="{f(s * b)}" r="{f(s * 0.09)}" fill="{C["navy"]}"/>' for a, b in pips)
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({rot} {f(s / 2)} {f(s / 2)})">'
            f'<rect width="{f(s)}" height="{f(s)}" rx="{f(s * 0.22)}" fill="{fill}"/>{p}</g>')


def coin(x, y, r, fill=None):
    fill = fill or C["mustard"]
    return (f'<g><circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 0.66)}" fill="none" stroke="{C["paper"]}" stroke-width="{f(r * 0.12)}" opacity=".7"/></g>')


def phone(x, y, w, h, screen=None, rot=0, body=None):
    body = body or C["navy"]
    screen = screen or C["white"]
    return (f'<g transform="rotate({rot} {f(x + w / 2)} {f(y + h / 2)})">'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(w * 0.18)}" fill="{body}"/>'
            f'<rect x="{f(x + w * 0.1)}" y="{f(y + h * 0.08)}" width="{f(w * 0.8)}" height="{f(h * 0.84)}" rx="{f(w * 0.1)}" fill="{screen}"/></g>')


def ball(x, y, r):
    """A plain sports ball: no league markings."""
    return (f'<g><circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{C["orange"]}"/>'
            f'<path d="M{f(x - r)},{f(y)} H{f(x + r)} M{f(x)},{f(y - r)} V{f(y + r)} '
            f'M{f(x - r * 0.7)},{f(y - r * 0.7)} Q{f(x - r * 0.15)},{f(y)} {f(x - r * 0.7)},{f(y + r * 0.7)} '
            f'M{f(x + r * 0.7)},{f(y - r * 0.7)} Q{f(x + r * 0.15)},{f(y)} {f(x + r * 0.7)},{f(y + r * 0.7)}" '
            f'stroke="{C["navy"]}" stroke-width="{f(r * 0.09)}" fill="none" stroke-linecap="round"/></g>')


def book(x, y, w, h, fill):
    return (f'<g><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="4" fill="{fill}"/>'
            f'<rect x="{f(x + w * 0.12)}" y="{f(y)}" width="{f(w * 0.08)}" height="{f(h)}" fill="{C["navy"]}" opacity=".18"/></g>')


def plant(x, y, s=1.0):
    return (f'<g transform="translate({f(x)} {f(y)}) scale({s})">'
            f'<path d="M0,-30 Q-26,-60 -8,-86 Q4,-60 0,-30Z" fill="{C["teal2"]}"/>'
            f'<path d="M2,-28 Q30,-54 22,-80 Q4,-62 2,-28Z" fill="{C["sage"]}"/>'
            f'<path d="M-18,-30 H18 L13,0 H-13Z" fill="{C["orange"]}"/></g>')


# ------------------------------------------------------------------ people
def _hair_back(st, cx, hy, r, col):
    if st == "puff":
        return (f'<circle cx="{f(cx)}" cy="{f(hy - r * 0.35)}" r="{f(r * 1.12)}" fill="{col}"/>'
                f'<circle cx="{f(cx + r * 0.2)}" cy="{f(hy - r * 1.35)}" r="{f(r * 0.5)}" fill="{col}"/>')
    if st == "bob":
        return f'<path d="M{f(cx - r * 1.12)},{f(hy + r * 0.75)} Q{f(cx - r * 1.3)},{f(hy - r * 1.25)} {f(cx)},{f(hy - r * 1.18)} Q{f(cx + r * 1.3)},{f(hy - r * 1.25)} {f(cx + r * 1.12)},{f(hy + r * 0.75)}Z" fill="{col}"/>'
    if st == "bun":
        return f'<circle cx="{f(cx - r * 0.1)}" cy="{f(hy - r * 1.18)}" r="{f(r * 0.42)}" fill="{col}"/>'
    if st == "hijab":
        return (f'<path d="M{f(cx - r * 1.2)},{f(hy + r * 1.55)} Q{f(cx - r * 1.38)},{f(hy - r * 1.3)} {f(cx)},{f(hy - r * 1.22)} '
                f'Q{f(cx + r * 1.38)},{f(hy - r * 1.3)} {f(cx + r * 1.2)},{f(hy + r * 1.55)}Z" fill="{col}"/>')
    return ""


def _hair_front(st, cx, hy, r, col, facing):
    sh = facing * r * 0.12
    if st == "puff":
        return f'<path d="M{f(cx - r)},{f(hy - r * 0.05)} A{f(r)},{f(r)} 0 0 1 {f(cx + r)},{f(hy - r * 0.05)} Q{f(cx + sh + r * 0.3)},{f(hy - r * 0.62)} {f(cx + sh)},{f(hy - r * 0.5)} Q{f(cx + sh - r * 0.4)},{f(hy - r * 0.58)} {f(cx - r)},{f(hy - r * 0.05)}Z" fill="{col}"/>'
    if st == "swoop":
        return (f'<path d="M{f(cx - r * 1.04)},{f(hy + r * 0.05)} Q{f(cx - r * 1.15)},{f(hy - r * 1.25)} {f(cx + r * 0.2)},{f(hy - r * 1.12)} '
                f'Q{f(cx + r * 1.2)},{f(hy - r * 1.05)} {f(cx + r * 1.04)},{f(hy - r * 0.05)} '
                f'Q{f(cx + sh + r * 0.4)},{f(hy - r * 0.7)} {f(cx + sh - r * 0.5)},{f(hy - r * 0.42)} Q{f(cx - r * 0.8)},{f(hy - r * 0.3)} {f(cx - r * 1.04)},{f(hy + r * 0.05)}Z" fill="{col}"/>')
    if st == "bob":
        return f'<path d="M{f(cx - r * 1.02)},{f(hy + r * 0.1)} A{f(r * 1.02)},{f(r * 1.02)} 0 0 1 {f(cx + r * 1.02)},{f(hy + r * 0.1)} Q{f(cx + sh + r * 0.2)},{f(hy - r * 0.62)} {f(cx + sh - r * 0.55)},{f(hy - r * 0.38)} Q{f(cx - r * 0.85)},{f(hy - r * 0.25)} {f(cx - r * 1.02)},{f(hy + r * 0.1)}Z" fill="{col}"/>'
    if st == "bun":
        return f'<path d="M{f(cx - r)},{f(hy)} A{f(r)},{f(r)} 0 0 1 {f(cx + r)},{f(hy)} Q{f(cx + sh + r * 0.1)},{f(hy - r * 0.68)} {f(cx + sh - r * 0.2)},{f(hy - r * 0.6)} Q{f(cx - r * 0.7)},{f(hy - r * 0.45)} {f(cx - r)},{f(hy)}Z" fill="{col}"/>'
    if st == "cap":
        brim_x = cx + facing * r * 0.55 if facing else cx
        return (f'<path d="M{f(cx - r * 1.02)},{f(hy - r * 0.2)} A{f(r * 1.02)},{f(r * 1.02)} 0 0 1 {f(cx + r * 1.02)},{f(hy - r * 0.2)}Z" fill="{col}"/>'
                f'<ellipse cx="{f(brim_x)}" cy="{f(hy - r * 0.22)}" rx="{f(r * 0.85)}" ry="{f(r * 0.17)}" fill="{col}"/>'
                f'<circle cx="{f(cx)}" cy="{f(hy - r * 1.02)}" r="{f(r * 0.1)}" fill="{C["navy"]}" opacity=".5"/>')
    if st == "hijab":  # a band of fabric framing the face
        return (f'<circle cx="{f(cx)}" cy="{f(hy + r * 0.06)}" r="{f(r * 0.9)}" fill="none" stroke="{col}" stroke-width="{f(r * 0.26)}"/>'
                f'<path d="M{f(cx - r * 0.9)},{f(hy - r * 0.1)} A{f(r * 0.9)},{f(r * 0.9)} 0 0 1 {f(cx + r * 0.9)},{f(hy - r * 0.1)} Q{f(cx)},{f(hy - r * 0.62)} {f(cx - r * 0.9)},{f(hy - r * 0.1)}Z" fill="{col}"/>')
    return ""


def face(cx, hy, r, facing=0, mood="smile", glasses=False, blush=True):
    ex = r * 0.36
    sh = facing * r * 0.2
    ey = hy + r * 0.08
    out = []
    if mood == "happy":  # closed, smiling eyes
        for sx in (-1, 1):
            x = cx + sh + sx * ex
            out.append(f'<path d="M{f(x - r * 0.12)},{f(ey + r * 0.02)} Q{f(x)},{f(ey - r * 0.14)} {f(x + r * 0.12)},{f(ey + r * 0.02)}" stroke="{C["navy"]}" stroke-width="{STROKE}" fill="none" stroke-linecap="round"/>')
    else:
        for sx in (-1, 1):
            out.append(f'<circle cx="{f(cx + sh + sx * ex)}" cy="{f(ey)}" r="{f(r * 0.085)}" fill="{C["navy"]}"/>')
    if glasses:
        for sx in (-1, 1):
            out.append(f'<circle cx="{f(cx + sh + sx * ex)}" cy="{f(ey)}" r="{f(r * 0.24)}" fill="none" stroke="{C["navy"]}" stroke-width="{STROKE * 0.8}"/>')
        out.append(f'<path d="M{f(cx + sh - ex + r * 0.24)},{f(ey)} H{f(cx + sh + ex - r * 0.24)}" stroke="{C["navy"]}" stroke-width="{STROKE * 0.8}"/>')
    if blush:
        for sx in (-1, 1):
            out.append(f'<ellipse cx="{f(cx + sh + sx * ex * 1.45)}" cy="{f(ey + r * 0.3)}" rx="{f(r * 0.15)}" ry="{f(r * 0.09)}" fill="{C["blush"]}" opacity=".55"/>')
    my = hy + r * 0.48
    mx = cx + sh
    if mood in ("smile", "happy"):
        out.append(f'<path d="M{f(mx - r * 0.2)},{f(my - r * 0.05)} Q{f(mx)},{f(my + r * 0.16)} {f(mx + r * 0.2)},{f(my - r * 0.05)}" stroke="{C["navy"]}" stroke-width="{STROKE}" fill="none" stroke-linecap="round"/>')
    elif mood == "talk":
        out.append(f'<path d="M{f(mx - r * 0.17)},{f(my - r * 0.06)} Q{f(mx)},{f(my + r * 0.26)} {f(mx + r * 0.17)},{f(my - r * 0.06)}Z" fill="{C["navy"]}"/>')
    elif mood == "think":
        out.append(f'<path d="M{f(mx - r * 0.13)},{f(my)} H{f(mx + r * 0.13)}" stroke="{C["navy"]}" stroke-width="{STROKE}" stroke-linecap="round"/>')
    elif mood == "wow":
        out.append(f'<ellipse cx="{f(mx)}" cy="{f(my)}" rx="{f(r * 0.09)}" ry="{f(r * 0.12)}" fill="{C["navy"]}"/>')
    return "".join(out)


def person(who, cx, base, s=1.0, pose="stand", arms=("down", "down"), facing=0, mood="smile", hold=None, flip_hold=False):
    """Draw a cast member standing or sitting with feet (or seat) at `base`.

    arms: a pair for (left, right) from the viewer's side, each one of
    down, wave, hip, hold, point, talk, up, lap, chin.
    hold: SVG snippet drawn at the right hand (or left with flip_hold).
    Returns (svg, hand_positions).
    """
    p = CAST[who]
    adult = p["kind"] == "adult"
    r = (27 if adult else 29) * s
    torso_h = (88 if adult else 74) * s
    tw = (66 if adult else 60) * s
    leg_h = (66 if adult else 56) * s
    out = []
    if pose == "stand":
        hip = base - leg_h
        for sx in (-1, 1):
            lx = cx + sx * tw * 0.2
            out.append(f'<path d="M{f(lx)},{f(hip)} V{f(base - 6 * s)}" stroke="{p["pants"]}" stroke-width="{f(19 * s)}" stroke-linecap="round"/>')
            out.append(f'<ellipse cx="{f(lx + sx * 3 * s + facing * 4 * s)}" cy="{f(base - 3 * s)}" rx="{f(12 * s)}" ry="{f(6 * s)}" fill="{C["navy"]}"/>')
    else:  # sit: thighs forward toward `facing` (or toward viewer when 0), shins down
        hip = base - leg_h * 0.82
        d = facing if facing else 0
        for sx in (-1, 1):
            lx = cx + sx * tw * 0.2
            kx = lx + d * 50 * s
            ky = hip + (0 if d else 8 * s)
            out.append(f'<path d="M{f(lx)},{f(hip)} L{f(kx)},{f(ky)} L{f(kx)},{f(base - 4 * s)}" stroke="{p["pants"]}" stroke-width="{f(19 * s)}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
            out.append(f'<ellipse cx="{f(kx + d * 6 * s)}" cy="{f(base - 3 * s)}" rx="{f(12 * s)}" ry="{f(6 * s)}" fill="{C["navy"]}"/>')
    top = hip - torso_h
    hy = top - r * 0.62
    out.append(_hair_back(p["hair"], cx, hy, r, p["hair_c"]))
    # torso: rounded shoulders, slightly wider at the hem
    rr = tw * 0.42
    out.append(
        f'<path d="M{f(cx - tw / 2 - 3 * s)},{f(hip + 4 * s)} L{f(cx - tw / 2)},{f(top + rr)} Q{f(cx - tw / 2)},{f(top)} {f(cx - tw / 2 + rr)},{f(top)} '
        f'H{f(cx + tw / 2 - rr)} Q{f(cx + tw / 2)},{f(top)} {f(cx + tw / 2)},{f(top + rr)} L{f(cx + tw / 2 + 3 * s)},{f(hip + 4 * s)} '
        f'Q{f(cx)},{f(hip + 10 * s)} {f(cx - tw / 2 - 3 * s)},{f(hip + 4 * s)}Z" fill="{p["top"]}"/>'
    )
    if p.get("whistle"):
        out.append(f'<path d="M{f(cx - 12 * s)},{f(top + 2 * s)} Q{f(cx)},{f(top + 34 * s)} {f(cx + 12 * s)},{f(top + 2 * s)}" stroke="{C["paper"]}" stroke-width="{f(2 * s)}" fill="none"/>'
                   f'<rect x="{f(cx - 5 * s)}" y="{f(top + 26 * s)}" width="{f(12 * s)}" height="{f(8 * s)}" rx="{f(3 * s)}" fill="{C["mustard"]}"/>')
    if who == "rivera":  # cardigan opening
        out.append(f'<path d="M{f(cx)},{f(top + 6 * s)} V{f(hip + 6 * s)}" stroke="{C["paper"]}" stroke-width="{f(2.4 * s)}" opacity=".55"/>')
    # head
    out.append(f'<circle cx="{f(cx)}" cy="{f(hy)}" r="{f(r)}" fill="{p["skin"]}"/>')
    # ears
    for sx in (-1, 1):
        if p["hair"] not in ("hijab", "bob"):
            out.append(f'<circle cx="{f(cx + sx * r * 0.98 - facing * r * 0.12)}" cy="{f(hy + r * 0.12)}" r="{f(r * 0.17)}" fill="{p["skin"]}"/>')
    out.append(_hair_front(p["hair"], cx, hy, r, p["hair_c"], facing))
    out.append(face(cx, hy, r, facing, mood, p.get("glasses", False)))
    # arms
    hands = []
    sy = top + 15 * s
    al = (52 if adult else 46) * s
    for i, kind in enumerate(arms):
        sx = -1 if i == 0 else 1
        x0 = cx + sx * (tw / 2 - 7 * s)
        if kind == "down":
            hx, hy2, mx_, my_ = x0 + sx * 7 * s, sy + al, x0 + sx * 9 * s, sy + al * 0.5
        elif kind == "wave":
            hx, hy2, mx_, my_ = x0 + sx * 30 * s, sy - al * 0.8, x0 + sx * 30 * s, sy + 2 * s
        elif kind == "up":
            hx, hy2, mx_, my_ = x0 + sx * 10 * s, sy - al * 0.95, x0 + sx * 14 * s, sy - al * 0.4
        elif kind == "hip":
            hx, hy2, mx_, my_ = x0 + sx * 4 * s, sy + al * 0.75, x0 + sx * 24 * s, sy + al * 0.42
        elif kind == "hold":
            hx, hy2, mx_, my_ = cx + sx * 8 * s, sy + al * 0.55, x0 + sx * 6 * s, sy + al * 0.62
        elif kind == "point":
            hx, hy2, mx_, my_ = x0 + sx * al * 1.05, sy + 4 * s, x0 + sx * al * 0.5, sy + 8 * s
        elif kind == "talk":
            hx, hy2, mx_, my_ = x0 + sx * 34 * s, sy + al * 0.25, x0 + sx * 14 * s, sy + al * 0.55
        elif kind == "lap":
            hx, hy2, mx_, my_ = cx + sx * 10 * s + facing * 22 * s, hip - 2 * s, x0 + sx * 4 * s, sy + al * 0.6
        elif kind == "chin":
            hx, hy2, mx_, my_ = cx + sx * r * 0.45, hy + r * 1.05, x0 + sx * 16 * s, sy + al * 0.45
        else:
            continue
        out.append(f'<path d="M{f(x0)},{f(sy)} Q{f(mx_)},{f(my_)} {f(hx)},{f(hy2)}" stroke="{p["top"]}" stroke-width="{f(15 * s)}" stroke-linecap="round" fill="none"/>')
        out.append(f'<circle cx="{f(hx)}" cy="{f(hy2)}" r="{f(7.5 * s)}" fill="{p["skin"]}"/>')
        hands.append((hx, hy2))
    if hold:
        hx, hy2 = hands[0] if flip_hold else hands[-1]
        out.append(f'<g transform="translate({f(hx)} {f(hy2)})">{hold}</g>')
    return "".join(out), hands


# ------------------------------------------------------------------ scenes
def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-hidden="true">'
            f'<title>{title}</title>{body}</svg>\n')


def hold_phone(s=1.0, rot=-10):
    return phone(-11 * s, -34 * s, 24 * s, 42 * s, rot=rot)


def scene_hero():
    b = [blob(380, 250, 330, 190, C["tealtint"], 1), blob(600, 120, 70, 60, C["orangetint"], 3)]
    b.append(shadow(200, 412, 70))
    b.append(shadow(395, 412, 60))
    b.append(shadow(560, 412, 60))
    p, _ = person("rivera", 200, 410, 1.12, arms=("hip", "talk"), facing=1, mood="talk")
    b.append(p)
    p, _ = person("maya", 395, 410, 1.0, arms=("down", "chin"), facing=-1, mood="think")
    b.append(p)
    p, _ = person("theo", 560, 410, 1.0, arms=("down", "hold"), facing=-1, mood="smile", hold=hold_phone())
    b.append(p)
    # speech bubbles: a die, a question mark
    b.append(bubble(250, 60, 120, 78, C["white"], "left", die(287, 72, 46, 3, C["orangetint"], -8)))
    b.append(bubble(430, 52, 96, 72, C["white"], "left",
                    f'<text x="478" y="104" text-anchor="middle" font-family="Georgia, serif" font-size="50" font-weight="700" fill="{C["teal"]}">?</text>'))
    b.append(sparkle(640, 70, 12, C["orange"]))
    b.append(dots([(90, 150), (668, 300), (120, 330)], C["orange"], 5))
    b.append(dots([(700, 200), (60, 250)], C["teal2"], 4))
    return svg(760, 440, "".join(b), "A teacher talks with two students; speech bubbles hold a die and a question mark")


def scene_ecosystem():
    """Understanding risk: one young person in the middle of everything around them."""
    b = [blob(330, 230, 300, 200, C["sand"], 2)]
    rings = [(330, 230, 190, C["tealtint"]), (330, 230, 128, C["orangetint"])]
    for x, y, r, col in rings:
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity=".8"/>')
    b.append(shadow(330, 332, 46))
    p, _ = person("amira", 330, 330, 0.95, arms=("down", "hold"), facing=0, mood="smile", hold=hold_phone(0.95))
    b.append(p)
    # around her: home, friends, school, screens, sport — small icons on the outer ring
    def icon_bg(x, y, col):
        return f'<circle cx="{x}" cy="{y}" r="30" fill="{C["white"]}"/><circle cx="{x}" cy="{y}" r="30" fill="{col}" opacity=".15"/>'
    # home
    b.append(icon_bg(160, 150, C["teal"]))
    b.append(f'<path d="M144,154 L160,139 L176,154 V170 H144Z" fill="{C["teal"]}"/><rect x="155" y="158" width="10" height="12" fill="{C["white"]}"/>')
    # friends (two heads)
    b.append(icon_bg(500, 140, C["orange"]))
    b.append(f'<circle cx="490" cy="134" r="8" fill="{C["orange"]}"/><circle cx="510" cy="134" r="8" fill="{C["teal"]}"/>'
             f'<path d="M478,156 Q490,140 502,156Z" fill="{C["orange"]}"/><path d="M498,156 Q510,140 522,156Z" fill="{C["teal"]}"/>')
    # school (book)
    b.append(icon_bg(530, 300, C["navy"]))
    b.append(book(515, 287, 30, 26, C["navy2"]))
    # screen / ads
    b.append(icon_bg(130, 300, C["orange"]))
    b.append(phone(120, 282, 20, 36, C["orangetint"]))
    b.append(sparkle(146, 286, 6, C["orange"]))
    # sport
    b.append(icon_bg(330, 50, C["teal"]))
    b.append(ball(330, 50, 15))
    b.append(dots([(60, 120), (610, 230), (90, 420)], C["orange"], 4))
    return svg(660, 450, "".join(b), "A teenager stands at the centre of rings showing home, friends, school, screens and sport")


def scene_path():
    """When to start: a winding path with stepping stones and two walkers."""
    b = [blob(380, 240, 340, 190, C["tealtint"], 4)]
    path = "M30,380 C200,380 180,250 340,250 S520,140 730,130"
    b.append(f'<path d="{path}" stroke="{C["sand"]}" stroke-width="58" fill="none" stroke-linecap="round"/>')
    b.append(f'<path d="{path}" stroke="{C["white"]}" stroke-width="4" fill="none" stroke-dasharray="2 18" stroke-linecap="round"/>')
    # stones with icons: controller, ball, phone, cake (birthday), cap (graduation)
    stones = [(110, 372), (260, 300), (400, 236), (540, 176), (680, 134)]
    for x, y in stones:
        b.append(f'<ellipse cx="{x}" cy="{y + 22}" rx="34" ry="10" fill="{C["navy"]}" opacity=".07"/>')
        b.append(f'<circle cx="{x}" cy="{y - 18}" r="26" fill="{C["white"]}"/>')
    x, y = stones[0]
    b.append(f'<rect x="{x - 17}" y="{y - 27}" width="34" height="18" rx="9" fill="{C["teal"]}"/><circle cx="{x - 8}" cy="{y - 18}" r="3" fill="{C["white"]}"/><circle cx="{x + 8}" cy="{y - 18}" r="3" fill="{C["white"]}"/>')
    x, y = stones[1]
    b.append(ball(x, y - 18, 14))
    x, y = stones[2]
    b.append(phone(x - 10, y - 36, 20, 36, C["orangetint"]))
    x, y = stones[3]
    b.append(f'<rect x="{x - 15}" y="{y - 22}" width="30" height="16" rx="3" fill="{C["orange"]}"/><rect x="{x - 2}" y="{y - 34}" width="4" height="12" fill="{C["mustard"]}"/><circle cx="{x}" cy="{y - 37}" r="3" fill="{C["orange"]}"/>')
    x, y = stones[4]
    b.append(f'<path d="M{x - 20},{y - 22} L{x},{y - 31} L{x + 20},{y - 22} L{x},{y - 13}Z" fill="{C["navy"]}"/><path d="M{x - 10},{y - 18} V{y - 9} Q{x},{y - 4} {x + 10},{y - 9} V{y - 18}" fill="{C["navy2"]}"/>')
    b.append(shadow(300, 422, 50))
    b.append(shadow(410, 422, 44))
    p, _ = person("sam", 300, 420, 0.92, arms=("down", "point"), facing=1, mood="talk")
    b.append(p)
    p, _ = person("maya", 410, 420, 0.86, arms=("wave", "down"), facing=-1, mood="happy")
    b.append(p)
    b.append(sparkle(700, 60, 11, C["orange"]))
    return svg(760, 440, "".join(b), "A parent and child walk a winding path past stepping stones marked with a game controller, a ball, a phone, a birthday cake and a graduation cap")


def scene_couch():
    """Starting a conversation: parent and teen on a couch, a phone between them."""
    b = [blob(360, 240, 320, 180, C["orangetint"], 5)]
    # couch
    b.append(f'<rect x="120" y="236" width="480" height="134" rx="40" fill="{C["teal"]}"/>')
    b.append(f'<rect x="150" y="334" width="420" height="40" rx="18" fill="{C["teal2"]}"/>')
    b.append(f'<rect x="100" y="300" width="60" height="76" rx="26" fill="{C["teal"]}"/><rect x="560" y="300" width="60" height="76" rx="26" fill="{C["teal"]}"/>')
    b.append(f'<rect x="140" y="368" width="14" height="22" rx="4" fill="{C["navy"]}"/><rect x="566" y="368" width="14" height="22" rx="4" fill="{C["navy"]}"/>')
    p, _ = person("sam", 250, 392, 0.95, pose="sit", arms=("lap", "talk"), facing=1, mood="talk")
    b.append(p)
    p, _ = person("theo", 470, 392, 0.92, pose="sit", arms=("hold", "lap"), facing=-1, mood="smile", hold=hold_phone(0.92, 12), flip_hold=True)
    b.append(p)
    b.append(bubble(300, 50, 130, 70, C["white"], "left",
                    f'<path d="M330,85 h70 M330,100 h46" stroke="{C["navy"]}" stroke-width="6" stroke-linecap="round" opacity=".5"/>'))
    b.append(plant(660, 390, 1.0))
    b.append(dots([(70, 160), (640, 120)], C["teal2"], 5))
    return svg(720, 420, "".join(b), "A parent and a teenager sit on a couch and talk about what is on the teenager's phone")


def scene_ads():
    """Digital advertising: a big phone screen full of offers, and a teen looking at it."""
    b = [blob(380, 230, 320, 190, C["tealtint"], 6)]
    # big phone
    b.append(f'<rect x="300" y="40" width="210" height="370" rx="34" fill="{C["navy"]}"/>')
    b.append(f'<rect x="314" y="62" width="182" height="326" rx="20" fill="{C["white"]}"/>')
    cards = [(330, 80, C["orangetint"], "+500"), (330, 168, C["tealtint"], "FREE"), (330, 256, C["sand"], "BOOST")]
    for x, y, col, label in cards:
        b.append(f'<rect x="{x}" y="{y}" width="150" height="74" rx="14" fill="{col}"/>')
        b.append(f'<text x="{x + 75}" y="{y + 47}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="26" fill="{C["navy"]}" letter-spacing="1">{label}</text>')
    b.append(sparkle(500, 92, 14, C["orange"]))
    b.append(sparkle(318, 236, 10, C["mustard"]))
    b.append(sparkle(490, 320, 9, C["orange"]))
    # notification dots streaming off the phone
    for i, (x, y) in enumerate([(540, 120), (575, 170), (600, 230)]):
        b.append(f'<rect x="{x}" y="{y}" width="{60 - i * 8}" height="22" rx="11" fill="{C["orange"] if i % 2 == 0 else C["teal2"]}"/>')
    b.append(shadow(190, 422, 52))
    p, _ = person("maya", 190, 420, 1.0, arms=("down", "chin"), facing=1, mood="wow")
    b.append(p)
    b.append(shadow(640, 422, 52))
    p, _ = person("rivera", 640, 420, 0.95, arms=("point", "down"), facing=-1, mood="talk")
    b.append(p)
    return svg(760, 440, "".join(b), "A student looks up at an oversized phone full of betting offers while a teacher points to it")


def scene_chance():
    """Understanding chance: a coach and students roll dice and chart the results."""
    b = [blob(380, 240, 330, 190, C["sand"], 7)]
    # table
    b.append(f'<rect x="200" y="300" width="360" height="22" rx="11" fill="{C["navy2"]}"/><rect x="230" y="320" width="14" height="90" rx="6" fill="{C["navy2"]}"/><rect x="516" y="320" width="14" height="90" rx="6" fill="{C["navy2"]}"/>')
    b.append(die(300, 262, 38, 6, C["white"], -12))
    b.append(die(350, 266, 34, 2, C["orangetint"], 9))
    b.append(coin(450, 284, 16))
    # chart board: six equal-ish bars
    b.append(f'<rect x="250" y="40" width="260" height="170" rx="18" fill="{C["white"]}"/>')
    heights = [62, 70, 58, 66, 74, 60]
    for i, hgt in enumerate(heights):
        x = 278 + i * 36
        b.append(f'<rect x="{x}" y="{180 - hgt}" width="24" height="{hgt}" rx="6" fill="{C["teal"] if i % 2 == 0 else C["teal2"]}"/>')
        b.append(dots([(x + 12, 196)], C["navy"], 3.2))
    b.append(f'<path d="M270,{180 - 65} H495" stroke="{C["orange"]}" stroke-width="3" stroke-dasharray="6 6"/>')
    b.append(shadow(120, 422, 58))
    p, _ = person("coach", 120, 420, 1.05, arms=("hip", "point"), facing=1, mood="talk")
    b.append(p)
    b.append(shadow(640, 422, 44))
    p, _ = person("theo", 640, 420, 0.95, arms=("up", "down"), facing=-1, mood="happy")
    b.append(p)
    return svg(760, 440, "".join(b), "A coach points at a chart of dice rolls that come out nearly even, while a student raises a hand")


def scene_watch_party():
    """Social influence: friends watching a game, one phone held out to the others."""
    b = [blob(380, 240, 340, 190, C["orangetint"], 8)]
    # TV
    b.append(f'<rect x="250" y="40" width="260" height="150" rx="18" fill="{C["navy"]}"/>')
    b.append(f'<rect x="264" y="54" width="232" height="122" rx="10" fill="{C["sage"]}"/>')
    b.append(f'<path d="M264,140 H496" stroke="{C["white"]}" stroke-width="3" opacity=".8"/><circle cx="380" cy="140" r="18" fill="none" stroke="{C["white"]}" stroke-width="3" opacity=".8"/>')
    b.append(ball(330, 110, 9))
    b.append(f'<rect x="372" y="190" width="16" height="20" fill="{C["navy"]}"/>')
    for x, who, arms, facing, mood, hold in [
        (170, "amira", ("up", "down"), 1, "happy", None),
        (330, "theo", ("down", "point"), 1, "talk", None),
        (500, "maya", ("chin", "down"), -1, "think", None),
    ]:
        b.append(shadow(x, 422, 46))
        p, hands = person(who, x, 420, 0.95, arms=arms, facing=facing, mood=mood)
        b.append(p)
    # Theo's phone held out toward Maya
    b.append(phone(400, 232, 26, 44, C["orangetint"], rot=14))
    b.append(sparkle(440, 230, 9, C["orange"]))
    b.append(shadow(650, 422, 46))
    p, _ = person("coach", 650, 420, 0.95, arms=("down", "down"), facing=-1, mood="smile")
    b.append(p)
    b.append(dots([(80, 120), (690, 110)], C["teal2"], 5))
    return svg(760, 440, "".join(b), "Friends watch a game on TV; one holds a phone out toward the others")


def scene_advocacy():
    """Advocacy: adults at a community meeting, one hand raised."""
    b = [blob(380, 240, 340, 190, C["tealtint"], 9)]
    # long table

    for x, who, arms, facing, mood, s in [
        (170, "coach", ("down", "talk"), 1, "talk", 0.92),
        (300, "rivera", ("up", "down"), 1, "smile", 0.92),
        (460, "sam", ("chin", "down"), -1, "think", 0.92),
        (590, "amira", ("down", "down"), -1, "smile", 0.88),
    ]:
        p, _ = person(who, x, 420, s, arms=arms, facing=facing, mood=mood)
        b.append(p)
    # cover the legs with the table front so people read as seated behind it
    b.append(f'<rect x="80" y="342" width="600" height="22" rx="11" fill="{C["navy2"]}"/>')
    b.append(f'<rect x="200" y="330" width="60" height="14" rx="3" fill="{C["white"]}"/><rect x="470" y="330" width="60" height="14" rx="3" fill="{C["white"]}"/>')
    b.append(book(350, 320, 44, 22, C["orange"]))
    b.append(f'<rect x="100" y="362" width="560" height="62" rx="10" fill="{C["teal"]}"/>')
    b.append(f'<text x="380" y="401" text-anchor="middle" font-family="Georgia, serif" font-size="26" fill="{C["white"]}">Prevention is on the agenda</text>')
    b.append(bubble(330, 40, 120, 64, C["white"], "left", f'<path d="M360,72 h60" stroke="{C["orange"]}" stroke-width="7" stroke-linecap="round"/>'))
    return svg(760, 440, "".join(b), "Adults around a community meeting table; one raises a hand. A banner reads: Prevention is on the agenda")


def scene_support():
    """Finding support: a counselor and a student talk; a heart between them."""
    b = [blob(330, 230, 290, 180, C["sand"], 10)]
    b.append(f'<rect x="96" y="344" width="110" height="48" rx="16" fill="{C["navy2"]}"/>')
    b.append(f'<rect x="454" y="344" width="110" height="48" rx="16" fill="{C["navy2"]}"/>')
    p, _ = person("rivera", 140, 392, 0.95, pose="sit", arms=("lap", "talk"), facing=1, mood="smile")
    b.append(p)
    p, _ = person("amira", 520, 392, 0.92, pose="sit", arms=("lap", "lap"), facing=-1, mood="talk")
    b.append(p)
    b.append(f'<path d="M330,170 C300,140 270,170 300,196 L330,222 L360,196 C390,170 360,140 330,170Z" fill="{C["orange"]}"/>')
    b.append(sparkle(380, 130, 10, C["mustard"]))
    b.append(plant(330, 392, 0.9))
    b.append(dots([(60, 140), (600, 120)], C["teal2"], 5))
    return svg(660, 420, "".join(b), "A school counselor and a student sit facing each other and talk; a heart floats between them")


def spot_who():
    b = [blob(100, 100, 82, 76, C["tealtint"], 11)]
    p, _ = person("maya", 70, 168, 0.5, arms=("down", "down"), facing=1)
    b.append(p)
    p, _ = person("theo", 112, 168, 0.5, arms=("down", "down"))
    b.append(p)
    p, _ = person("amira", 152, 168, 0.5, arms=("down", "down"), facing=-1)
    b.append(p)
    return svg(200, 200, "".join(b), "Three students")


def spot_when():
    b = [blob(100, 100, 82, 76, C["orangetint"], 12)]
    b.append(f'<rect x="50" y="56" width="100" height="92" rx="16" fill="{C["white"]}"/>')
    b.append(f'<rect x="50" y="56" width="100" height="26" rx="13" fill="{C["teal"]}"/><rect x="50" y="70" width="100" height="12" fill="{C["teal"]}"/>')
    for i in range(3):
        for j in range(3):
            fill = C["orange"] if (i, j) == (1, 1) else C["sand"]
            b.append(f'<rect x="{62 + i * 28}" y="{92 + j * 18}" width="20" height="12" rx="4" fill="{fill}"/>')
    b.append(f'<rect x="72" y="46" width="8" height="20" rx="4" fill="{C["navy"]}"/><rect x="120" y="46" width="8" height="20" rx="4" fill="{C["navy"]}"/>')
    return svg(200, 200, "".join(b), "A calendar with one day marked")


def spot_what():
    b = [blob(100, 100, 82, 76, C["sand"], 13)]
    b.append(bubble(36, 50, 92, 58, C["teal"], "left", f'<path d="M56,74 h52 M56,88 h32" stroke="{C["white"]}" stroke-width="6" stroke-linecap="round"/>'))
    b.append(bubble(88, 104, 76, 48, C["orange"], "right", f'<circle cx="110" cy="128" r="4" fill="{C["white"]}"/><circle cx="126" cy="128" r="4" fill="{C["white"]}"/><circle cx="142" cy="128" r="4" fill="{C["white"]}"/>'))
    return svg(200, 200, "".join(b), "Two speech bubbles")


def cast_sheet():
    b = [f'<rect width="980" height="300" fill="{C["paper"]}"/>']
    xs = [90, 250, 410, 570, 730, 890]
    for x, who in zip(xs, ["maya", "theo", "amira", "rivera", "coach", "sam"]):
        b.append(shadow(x, 262, 46))
        p, _ = person(who, x, 260, 0.95, arms=("down", "down"), mood="smile")
        b.append(p)
        b.append(f'<text x="{x}" y="288" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{C["navy"]}">{CAST[who]["name"]}</text>')
    return svg(980, 300, "".join(b), "The recurring cast: Maya, Theo, Amira, Ms. Rivera, Coach Ben and Sam")


def mark():
    """The Gambling Literacy mark: a rounded speech bubble holding one die pip."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{C["navy"]}"/>'
            f'<path d="M16,14 H48 Q54,14 54,20 V38 Q54,44 48,44 H30 L20,52 V44 H16 Q10,44 10,38 V20 Q10,14 16,14Z" fill="{C["paper"]}"/>'
            f'<circle cx="32" cy="29" r="6" fill="{C["orange"]}"/></svg>\n')


def mock_ad():
    """A made-up sportsbook welcome offer for the mock-ad worksheet. Fictional
    brand, generic design; the fine print is printed as text on the sheet."""
    b = [blob(380, 250, 330, 210, C["tealtint"], 14)]
    # phone
    b.append(f'<rect x="230" y="20" width="300" height="460" rx="40" fill="{C["navy"]}"/>')
    b.append(f'<rect x="246" y="44" width="268" height="412" rx="24" fill="{C["white"]}"/>')
    # header bar with fictional brand
    b.append(f'<rect x="246" y="44" width="268" height="54" rx="24" fill="{C["navy2"]}"/><rect x="246" y="74" width="268" height="24" fill="{C["navy2"]}"/>')
    b.append(f'<text x="380" y="79" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="17" fill="{C["white"]}" letter-spacing="2">SAMPLEBET</text>')
    b.append(f'<text x="380" y="94" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="{C["sand"]}" letter-spacing="1">A MADE-UP BRAND FOR TEACHING</text>')
    # offer
    b.append(f'<text x="380" y="140" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="15" fill="{C["teal"]}" letter-spacing="1.5">WELCOME OFFER</text>')
    b.append(f'<text x="380" y="190" text-anchor="middle" font-family="Arial, sans-serif" font-weight="800" font-size="34" fill="{C["navy"]}">BET $5</text>')
    b.append(f'<text x="380" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-weight="800" font-size="46" fill="{C["orange"]}">GET $200</text>')
    b.append(f'<text x="380" y="268" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="16" fill="{C["navy"]}">in Bonus Bets*</text>')
    b.append(sparkle(492, 168, 12, C["mustard"]))
    b.append(sparkle(266, 150, 9, C["orange"]))
    # boost chip
    b.append(f'<rect x="276" y="290" width="208" height="40" rx="20" fill="{C["orangetint"]}"/>')
    b.append(f'<text x="380" y="316" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="14" fill="{C["navy"]}">+ 50% PARLAY BOOST</text>')
    # button
    b.append(f'<rect x="286" y="352" width="188" height="48" rx="24" fill="{C["teal"]}"/>')
    b.append(f'<text x="380" y="382" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="17" fill="{C["white"]}">CLAIM NOW</text>')
    # fine print, deliberately tiny
    for i, w in enumerate((220, 236, 200)):
        b.append(f'<rect x="{380 - w / 2}" y="{418 + i * 9}" width="{w}" height="4" rx="2" fill="{C["navy"]}" opacity=".25"/>')
    b.append(f'<text x="268" y="425" font-family="Arial, sans-serif" font-size="9" fill="{C["navy"]}" opacity=".6">*</text>')
    b.append(dots([(130, 140), (640, 380), (110, 380)], C["orange"], 5))
    b.append(dots([(660, 150)], C["teal2"], 5))
    return svg(760, 500, "".join(b), "A made-up sportsbook ad on a phone: Bet $5, get $200 in bonus bets, with an asterisk and tiny fine print")


SCENES = {
    "mock-ad": mock_ad,
    "hero-conversation": scene_hero,
    "understanding-risk": scene_ecosystem,
    "when-to-start": scene_path,
    "conversation-couch": scene_couch,
    "digital-advertising": scene_ads,
    "understanding-chance": scene_chance,
    "social-influence": scene_watch_party,
    "advocacy-meeting": scene_advocacy,
    "finding-support": scene_support,
    "spot-who": spot_who,
    "spot-when": spot_when,
    "spot-what": spot_what,
    "cast": cast_sheet,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in SCENES.items():
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
    (OUT.parent / "mark.svg").write_text(mark(), encoding="utf-8")
    print(f"wrote {len(SCENES)} illustrations to {OUT}")


if __name__ == "__main__":
    main()
