#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liquidity State — Icosahedron logo generator (geometrically computed).

The mark is a true icosahedron built from the golden ratio:
    - 12 vertices at (0, ±1, ±phi) and cyclic permutations
    - 20 triangular faces
Oriented "vertex up" and viewed down a 3-fold axis so the outer
silhouette is a regular hexagon (per brand spec, rx = 54deg apex).
Faces are shaded with a metallic silver ramp driven by the light
direction; edges are stroked in #54687a.

No simplified / flat-icon fallback is ever produced — this is the
only approved way to draw the logo.

Usage:
    python3 generate_logo.py            # -> icosahedron.svg (light/metal)
    python3 generate_logo.py --dark     # -> icosahedron-dark.svg (cover glow)
"""
import math
import sys

PHI = (1.0 + math.sqrt(5.0)) / 2.0

# --- 12 vertices of a unit-ish icosahedron -------------------------------
VERTS = [
    (-1,  PHI, 0), ( 1,  PHI, 0), (-1, -PHI, 0), ( 1, -PHI, 0),
    ( 0, -1,  PHI), ( 0,  1,  PHI), ( 0, -1, -PHI), ( 0,  1, -PHI),
    ( PHI, 0, -1), ( PHI, 0,  1), (-PHI, 0, -1), (-PHI, 0,  1),
]

# --- 20 triangular faces (standard icosahedron topology) -----------------
FACES = [
    (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
    (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
    (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
    (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
]


def normalize(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return (v[0] / m, v[1] / m, v[2] / m)


def matmul(m, v):
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def hexstr(rgb):
    return "#%02X%02X%02X" % rgb


def build(dark=False):
    size = 512
    cx = cy = size / 2.0

    # Orientation: view down a 3-fold face axis (hexagonal silhouette),
    # then tilt so an apex vertex sits at the top. rx=54deg per spec.
    # A 3-fold axis passes through a face centroid; aligning it to Z
    # yields the hexagonal outline. The extra Z spin points a vertex up.
    face_c = normalize(
        tuple(sum(VERTS[i][k] for i in FACES[0]) / 3.0 for k in range(3))
    )
    # Build a rotation that maps face_c -> +Z (view axis).
    z_axis = (0, 0, 1)
    axis = cross(face_c, z_axis)
    ax_len = math.sqrt(dot(axis, axis))
    ang = math.acos(max(-1.0, min(1.0, dot(face_c, z_axis))))
    if ax_len < 1e-9:
        align = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    else:
        u = (axis[0] / ax_len, axis[1] / ax_len, axis[2] / ax_len)
        c, s = math.cos(ang), math.sin(ang)
        C = 1 - c
        align = [
            [c + u[0] * u[0] * C, u[0] * u[1] * C - u[2] * s, u[0] * u[2] * C + u[1] * s],
            [u[1] * u[0] * C + u[2] * s, c + u[1] * u[1] * C, u[1] * u[2] * C - u[0] * s],
            [u[2] * u[0] * C - u[1] * s, u[2] * u[1] * C + u[0] * s, c + u[2] * u[2] * C],
        ]
    # Spin about Z so a vertex is at 12 o'clock, plus the spec apex tilt.
    R = mmul(rot_z(math.radians(90)), align)
    R = mmul(rot_x(math.radians(180 - 54)), R)  # rx=54deg apex-up

    tv = [matmul(R, v) for v in VERTS]

    # Orthographic projection with a scale that fits the silhouette.
    span = max(max(abs(p[0]), abs(p[1])) for p in tv)
    scale = (size * 0.42) / span
    proj = [(cx + p[0] * scale, cy - p[1] * scale, p[2]) for p in tv]

    light = normalize((-0.35, 0.65, 0.72))  # upper-left key light

    drawn = []
    for f in FACES:
        a, b, c = (tv[i] for i in f)
        n = normalize(cross((b[0] - a[0], b[1] - a[1], b[2] - a[2]),
                            (c[0] - a[0], c[1] - a[1], c[2] - a[2])))
        # Ensure outward normal (points roughly toward viewer if front).
        centroid = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3)
        if dot(n, centroid) < 0:
            n = (-n[0], -n[1], -n[2])
        facing = n[2]  # +Z toward viewer
        if facing <= 0.02:
            continue  # backface cull
        lam = max(0.0, dot(n, light))
        drawn.append((centroid[2], f, lam, facing))

    # Painter's order: far first.
    drawn.sort(key=lambda d: d[0])

    if dark:
        lo, mid, hi = (0x1E, 0x2E, 0x3A), (0x5A, 0x74, 0x82), (0xBF, 0xE9, 0xEC)
        edge = "#0B3C46"
        bg = None
    else:
        lo, mid, hi = (0x6B, 0x7C, 0x87), (0xAF, 0xBC, 0xC4), (0xF3, 0xF7, 0xF9)
        edge = "#54687A"
        bg = None

    def shade(lam):
        if lam < 0.5:
            return hexstr(lerp_color(lo, mid, lam / 0.5))
        return hexstr(lerp_color(mid, hi, (lam - 0.5) / 0.5))

    parts = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d" role="img" aria-label="Liquidity State icosahedron">'
        % (size, size, size, size)
    )
    parts.append("<defs>")
    parts.append(
        '<radialGradient id="lsSpec" cx="38%%" cy="30%%" r="80%%">'
        '<stop offset="0%%" stop-color="#FFFFFF" stop-opacity="%s"/>'
        '<stop offset="55%%" stop-color="#FFFFFF" stop-opacity="0"/>'
        "</radialGradient>" % ("0.55" if not dark else "0.35")
    )
    if dark:
        parts.append(
            '<filter id="lsGlow" x="-40%" y="-40%" width="180%" height="180%">'
            '<feGaussianBlur stdDeviation="9" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
            "</filter>"
        )
    parts.append("</defs>")

    grp_open = '<g filter="url(#lsGlow)">' if dark else "<g>"
    parts.append(grp_open)
    for _z, f, lam, _fac in drawn:
        pts = " ".join("%.2f,%.2f" % (proj[i][0], proj[i][1]) for i in f)
        parts.append(
            '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4" '
            'stroke-linejoin="round"/>' % (pts, shade(lam), edge)
        )
    # Specular sheen overlay following the silhouette convex hull-ish center.
    parts.append(
        '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#lsSpec)"/>'
        % (cx, cy, size * 0.46)
    )
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    dark = "--dark" in sys.argv
    svg = build(dark=dark)
    out = "icosahedron-dark.svg" if dark else "icosahedron.svg"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote", out)


if __name__ == "__main__":
    main()
