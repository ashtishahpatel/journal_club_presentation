#!/usr/bin/env python3
"""Crop figures out of a PDF page and draw highlight boxes on them.

All coordinates are FRACTIONS of the full page (0.0 = left/top, 1.0 = right/bottom),
so they can be read straight off the grid preview.

  # 1. Make a grid preview of a page to read coordinates from
  figure_tool.py grid paper.pdf 4 out/page4_grid.png

  # 2. Crop the figure and box the relevant part (box coords are also page fractions)
  figure_tool.py crop paper.pdf 4 out/fig1.png --crop 0.05 0.55 0.48 0.80 \
      --box 0.28 0.58 0.42 0.66 --label "84% / 80%"

Requires: pdftoppm (poppler) and Pillow.
"""
import argparse
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

RED = (220, 20, 20)


def render_page(pdf, page, dpi):
    tmpdir = tempfile.mkdtemp(prefix="jc_render_")
    prefix = os.path.join(tmpdir, "p")
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi), "-png", pdf, prefix],
        check=True,
    )
    files = [f for f in os.listdir(tmpdir) if f.endswith(".png")]
    if not files:
        sys.exit(f"Could not render page {page} of {pdf}")
    return Image.open(os.path.join(tmpdir, files[0])).convert("RGB")


def font(size):
    for path in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def cmd_grid(a):
    img = render_page(a.pdf, a.page, 110)
    w, h = img.size
    d = ImageDraw.Draw(img)
    f = font(14)
    for i in range(1, 20):
        frac = i / 20
        major = i % 2 == 0
        color = (0, 90, 255) if major else (150, 190, 255)
        x, y = int(frac * w), int(frac * h)
        d.line([(x, 0), (x, h)], fill=color, width=1)
        d.line([(0, y), (w, y)], fill=color, width=1)
        if major:
            d.text((x + 2, 2), f"{frac:.1f}", fill=(0, 60, 200), font=f)
            d.text((2, y + 2), f"{frac:.1f}", fill=(0, 60, 200), font=f)
    img.save(a.out)
    print(a.out)


def cmd_crop(a):
    img = render_page(a.pdf, a.page, a.dpi)
    w, h = img.size
    x0, y0, x1, y1 = a.crop
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        sys.exit("--crop must be x0 y0 x1 y1 fractions with x0<x1, y0<y1")
    cx0, cy0 = int(x0 * w), int(y0 * h)
    out = img.crop((cx0, cy0, int(x1 * w), int(y1 * h)))
    d = ImageDraw.Draw(out)
    stroke = max(3, a.dpi // 50)
    f = font(max(18, a.dpi // 8))
    labels = a.label or []
    positions = a.pos or []
    for i, box in enumerate(a.box or []):
        bx0, by0, bx1, by1 = box
        rect = (int(bx0 * w) - cx0, int(by0 * h) - cy0, int(bx1 * w) - cx0, int(by1 * h) - cy0)
        d.rectangle(rect, outline=RED, width=stroke)
        if i < len(labels) and labels[i]:
            tw, th = d.textsize(labels[i], font=f)
            pos = positions[i] if i < len(positions) else "above"
            tx, ty = {
                "above": (rect[0], rect[1] - th - 6),
                "below": (rect[0], rect[3] + 2),
                "left": (rect[0] - tw - 10, rect[1]),
                "right": (rect[2] + 2, rect[1]),
            }[pos]
            tx, ty = max(0, tx), max(0, ty)
            d.rectangle((tx, ty, tx + tw + 8, ty + th + 4), fill=RED)
            d.text((tx + 4, ty + 1), labels[i], fill="white", font=f)
    out.save(a.out)
    print(a.out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grid", help="render a page with a labeled 5%% coordinate grid")
    g.add_argument("pdf"); g.add_argument("page", type=int); g.add_argument("out")
    g.set_defaults(fn=cmd_grid)

    c = sub.add_parser("crop", help="crop a region and draw highlight boxes")
    c.add_argument("pdf"); c.add_argument("page", type=int); c.add_argument("out")
    c.add_argument("--crop", type=float, nargs=4, required=True, metavar=("X0", "Y0", "X1", "Y1"))
    c.add_argument("--box", type=float, nargs=4, action="append", metavar=("X0", "Y0", "X1", "Y1"),
                   help="highlight box in page fractions; repeatable")
    c.add_argument("--label", action="append", help="optional tag for the matching --box; repeatable")
    c.add_argument("--pos", action="append", choices=["above", "below", "left", "right"],
                   help="where to put the matching --label (default above); repeatable")
    c.add_argument("--dpi", type=int, default=220)
    c.set_defaults(fn=cmd_crop)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
