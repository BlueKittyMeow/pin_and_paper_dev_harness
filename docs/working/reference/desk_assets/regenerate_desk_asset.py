#!/usr/bin/env python3
"""Regenerates pin_and_paper's desk_executive.webp from DESKTRANS.png.

Source of truth for the desk-asset pipeline (2026-08-05 session; owner
Lara). Inputs live beside this script:
  DESKTRANS.png  — owner's background-removed desk render (RGBA, 1536x1024)
  FLOOR.png      — top-down floor backdrop (separately exported as
                   desk_void_backdrop.jpg, JPEG q82)
  DESK.png       — the original opaque desk photo (reference only)

Pipeline:
1. Perspective-warp the desk-top OUTER slab quad (alpha-traced corners) to
   a 2000x1500 rect at (64,64) in a padded canvas — 64px margin keeps the
   feathered glow.
2. Level the visible lip edge: the render carries a ~0.5deg roll; the lip
   shadow line (fit from luminance gradients, NOT alpha — alpha lies: glow,
   kneehole apron, pedestal columns all pollute it) tilts ~18.7px across
   the width. Fix = per-column rigid vertical shift, ramped over the first
   42 rows below the surface so the surface rect is untouched and drawers
   move as solid units.
3. De-shine (K=1.0, owner-approved "I love k1"): subtract the
   low-frequency luminance excess (Gaussian sigma 90 vs surface median),
   soft-masked to the surface rect — kills waxy specular bands, keeps
   grain.
4. Export WEBP q90.

App-side geometry (lib/spatial/spatial_desk_background.dart +
lib/screens/canvas_screen.dart):
  - Asset size: 2128 x 2264, displayed 1:1 logical px.
  - INNER BEVEL PANEL (the usable canvas; owner decision 2026-08-05):
    groove darkest-line rect (149,182)-(1982,1456) in asset px, +5px
    inset => panel (154,187)-(1977,1451) = 1823 x 1264 (aspect 1.442).
  - kCanvasScreenSize = Size(1823, 1264); canvas origin = panel top-left;
    image offset = (-154,-187).
  - DESK MATS / adornments: full-canvas art, 1823x1264 logical (make at
    2x = 3646x2528), square corners, drops exactly into the bevel.
"""
from PIL import Image, ImageFilter
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser(
    '~/Documents/Git/pin-and-paper/pin_and_paper/assets/images/spatial/desk_executive.webp')
W, H, M = 2000, 1500, 64
SURF = M + H
QUAD = [(187, 112), (1337, 112), (1389, 663), (143, 655)]  # TL TR BR BL, alpha-traced
K_DESHINE = 1.0
RAMP = 42


def persp_coeffs(sq, dq):
    A, b = [], []
    for (dx, dy), (sx, sy) in zip(dq, sq):
        A.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        A.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
        b += [sx, sy]
    return np.linalg.solve(np.array(A, float), np.array(b, float))


img = Image.open(os.path.join(HERE, 'DESKTRANS.png'))
warp = img.transform((W + 2 * M, H + M + 700), Image.PERSPECTIVE,
                     persp_coeffs(QUAD, [(M, M), (M + W, M), (M + W, M + H), (M, M + H)]),
                     Image.BICUBIC)
arr = np.array(warp, dtype=float)
Hh, Ww = arr.shape[:2]

# --- level the visible lip edge ---
lum0 = arr[:, :, :3].mean(axis=2)
grad = np.diff(lum0[SURF:SURF + 260], axis=0)
xs = np.arange(80, 2048)
ey = SURF + np.argmin(grad[:, 80:2048], axis=0)
for _ in range(3):
    fit = np.polyfit(xs, ey, 1)
    keep = np.abs(ey - np.polyval(fit, xs)) < 3 * np.std(ey - np.polyval(fit, xs))
    xs, ey = xs[keep], ey[keep]
shift = np.polyval(fit, Ww / 2) - np.polyval(fit, np.arange(Ww))
res = np.zeros((Hh, Ww, 4))
res[:SURF] = arr[:SURF]
ys = np.arange(SURF, Hh)
ramp = np.clip((ys - SURF) / RAMP, 0, 1)
for x in range(Ww):
    src_y = np.clip(ys - shift[x] * ramp, 0, Hh - 1.001)
    i0 = src_y.astype(int)
    frac = (src_y - i0)[:, None]
    res[SURF:, x] = arr[i0, x] * (1 - frac) + arr[i0 + 1, x] * frac
rows = np.where((res[:, :, 3] > 0).any(axis=1))[0]
res = res[:min(int(rows.max()) + 8, Hh)]

# --- de-shine the surface ---
rgb = res[:, :, :3]
lum = rgb.mean(axis=2)
low = np.array(Image.fromarray(np.uint8(np.clip(lum, 0, 255)))
               .filter(ImageFilter.GaussianBlur(90)), dtype=float)
surface = np.s_[M + 8:SURF - 8, M + 8:M + W - 8]
excess = np.clip(low - np.median(low[surface]), 0, None)
mask = np.zeros(res.shape[:2])
mask[surface] = 1.0
mask = np.array(Image.fromarray(np.uint8(mask * 255)).filter(ImageFilter.GaussianBlur(24))) / 255.0
scale = np.clip((lum - K_DESHINE * excess * mask) / np.maximum(lum, 1e-3), 0.3, 1.0)
res[:, :, :3] = rgb * scale[:, :, None]

final = Image.fromarray(np.uint8(np.clip(res, 0, 255)))
final.save(OUT, 'WEBP', quality=90)
print('wrote', OUT, final.size)
