#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261127 entry.

Copies the rendered front page (entry.png, produced by build_27nov.py in
this same directory) to /output/entry.png, verifying size and sha256
before and after the copy so the output is provably the same file.
Runs with no network. Deterministic.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found (run build_27nov.py first)",
              file=sys.stderr)
        sys.exit(1)

    src_size = os.path.getsize(SRC)
    src_sha = sha256_of(SRC)
    print(f"source: {SRC}")
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
