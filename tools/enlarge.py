#!/usr/bin/env python3
"""Build YAMIS_ENLARGED from an upstream YAMIS checkout.

Every SVG outside SKIP_DIRS is enlarged by SCALE around the center of its
visible bounding box. Instead of rewriting the drawing (as `inkscape
transform-scale` did), only the root viewBox is shrunk around that center,
which is visually identical, keeps the files diffable and takes a second
for the whole set.

Usage: enlarge.py UPSTREAM_DIR OUT_DIR

Everything in OUT_DIR except KEEP is replaced by the fresh build.
"""
import os
import re
import shutil
import sys
from pathlib import Path

import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg  # noqa: E402

# === CONFIGURATION ===
SCALE = 1.2
THEME_NAME = "YAMIS_ENLARGED"

# Icon directories copied without enlarging (relative to theme root)
SKIP_DIRS = {
    "apps/scalable",
    "places/scalable",
    "places/scalable-outlined",
    "mimetypes/scalable",
    "mimetypes/scalable-outlined",
    "emblems/scalable",
    "devices/scalable",
}

# Upstream files not shipped with the enlarged theme
SKIP_FILES = {"readme.md", "changelog", ".gitignore"}

# Top-level entries of OUT_DIR that are not generated and must survive a rebuild
KEEP = {".git", ".github", ".gitattributes", ".gitignore", ".idea", "tools", "README.md"}

# === SVG HANDLING ===
SVG_TAG = re.compile(r"<svg\b[^>]*>", re.S)
NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
PLAIN_LENGTH = re.compile(r"\s*([-+]?(?:\d+\.?\d*|\.\d+))\s*(?:px)?\s*$")


def get_attr(tag, name):
    return re.search(rf'\s{name}\s*=\s*(["\'])(.*?)\1', tag, re.S)


def canvas(tag):
    """Return the root user-space rectangle (x, y, w, h) or None."""
    vb = get_attr(tag, "viewBox")
    if vb:
        nums = [float(n) for n in NUMBER.findall(vb.group(2))]
        return tuple(nums) if len(nums) == 4 and nums[2] > 0 and nums[3] > 0 else None
    size = []
    for name in ("width", "height"):
        m = get_attr(tag, name)
        length = m and PLAIN_LENGTH.match(m.group(2))
        if not length:
            return None
        size.append(float(length.group(1)))
    return (0.0, 0.0, *size)


def ink_center(path, rect):
    """Center of the visible bounding box in user units, as librsvg computes it."""
    x, y, w, h = rect
    handle = Rsvg.Handle.new_from_file(str(path))
    ok, pw, ph = handle.get_intrinsic_size_in_pixels()
    if not ok or pw <= 0 or ph <= 0:
        return None
    viewport = Rsvg.Rectangle()
    viewport.x, viewport.y, viewport.width, viewport.height = 0, 0, pw, ph
    ok, ink, _ = handle.get_geometry_for_layer(None, viewport)
    if not ok or ink.width <= 0 or ink.height <= 0:
        return None
    return x + (ink.x + ink.width / 2) * w / pw, y + (ink.y + ink.height / 2) * h / ph


def fmt(value):
    s = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def enlarge(src_path, text):
    """Return text with the root viewBox shrunk by SCALE, or None if not applicable."""
    m = SVG_TAG.search(text)
    rect = m and canvas(m.group(0))
    if not rect:
        return None
    x, y, w, h = rect
    cx, cy = ink_center(src_path, rect) or (x + w / 2, y + h / 2)
    view_box = f"{fmt(cx - (cx - x) / SCALE)} {fmt(cy - (cy - y) / SCALE)} {fmt(w / SCALE)} {fmt(h / SCALE)}"

    tag = m.group(0)
    vb = get_attr(tag, "viewBox")
    if vb:
        tag = tag[: vb.start(2)] + view_box + tag[vb.end(2):]
    else:
        tag = f'<svg viewBox="{view_box}"' + tag[4:]
    return text[: m.start()] + tag + text[m.end():]


# === BUILD ===
def clean_output(out_dir):
    """Remove previous build, refusing to touch directories that are not this theme."""
    if out_dir.exists() and any(p.name not in KEEP for p in out_dir.iterdir()):
        index = out_dir / "index.theme"
        if not index.is_file() or f"Name={THEME_NAME}" not in index.read_text():
            sys.exit(f"{out_dir} is not empty and does not look like {THEME_NAME}, refusing to overwrite")
    out_dir.mkdir(parents=True, exist_ok=True)
    for entry in out_dir.iterdir():
        if entry.name in KEEP:
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def read(path):
    with open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.write(text)


def build(src_dir, out_dir):
    clean_output(out_dir)
    stats = {"enlarged": 0, "copied": 0, "linked": 0}
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        rel_dir = Path(root).relative_to(src_dir)
        enlarge_here = rel_dir.as_posix() not in SKIP_DIRS
        for name in files:
            src, rel = Path(root) / name, rel_dir / name
            if rel.as_posix() in SKIP_FILES:
                continue
            dst = out_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)

            if src.is_symlink():
                os.symlink(os.readlink(src), dst)
                stats["linked"] += 1
                continue

            if rel.as_posix() == "index.theme":
                write(dst, re.sub(r"(?m)^Name=.*$", f"Name={THEME_NAME}", read(src), count=1))
                continue

            if enlarge_here and name.lower().endswith(".svg"):
                result = enlarge(src, read(src))
                if result is not None:
                    write(dst, result)
                    stats["enlarged"] += 1
                    continue
                print(f"[WARN] no usable size, copied as is: {rel}", file=sys.stderr)

            shutil.copy2(src, dst)
            stats["copied"] += 1
    return stats


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src_dir, out_dir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    if not (src_dir / "index.theme").is_file():
        sys.exit(f"{src_dir} is not an icon theme (no index.theme)")
    print(", ".join(f"{k}: {v}" for k, v in build(src_dir, out_dir).items()))
