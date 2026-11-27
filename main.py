#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261127 entry.

Copies the rendered front page (entry.png, produced by build_27nov.py in
this same directory) to /output/entry.png, verifying that the source is a
genuine 1024x1024 PNG and that size and sha256 match before and after the
copy, so the output is provably the same file.
Runs with no network. Deterministic.
"""
import hashlib
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_png(path):
    """Check path is a genuine, fully decodable PNG of the expected size.

    Exits loudly on any failure: not a PNG, truncated or corrupt image
    data, or dimensions other than EXPECTED_WIDTH x EXPECTED_HEIGHT.
    Returns (format, (width, height)) on success.
    """
    try:
        with Image.open(path) as img:
            fmt = img.format
            size = img.size
            img.load()  # decode every scanline: catches truncated data
    except Exception as exc:  # corrupt file, unreadable header, bad CRC
        print(f"error: {path} is not a readable PNG: {exc}", file=sys.stderr)
        sys.exit(1)
    if fmt != "PNG":
        print(f"error: {path} is {fmt}, not a PNG", file=sys.stderr)
        sys.exit(1)
    if size != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        print(f"error: {path} is {size[0]}x{size[1]}, expected "
              f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}", file=sys.stderr)
        sys.exit(1)
    return fmt, size


def main():
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found (run build_27nov.py first)",
              file=sys.stderr)
        sys.exit(1)

    fmt, (width, height) = validate_png(SRC)

    src_size = os.path.getsize(SRC)
    src_sha = sha256_of(SRC)
    print(f"source: {SRC}")
    print(f"  format: {fmt} {width}x{height}")
    print(f"  size: {src_size} bytes")
    print(f"  sha256: {src_sha}")

    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)

    dst_size = os.path.getsize(DST)
    dst_sha = sha256_of(DST)
    print(f"output: {DST}")
    print(f"  size: {dst_size} bytes")
    print(f"  sha256: {dst_sha}")

    if dst_size != src_size or dst_sha != src_sha:
        print("error: output does not match source", file=sys.stderr)
        sys.exit(1)
    print("verified: /output/entry.png matches entry.png")


if __name__ == "__main__":
    main()
