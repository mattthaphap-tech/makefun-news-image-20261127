#!/usr/bin/env python3
"""Hand over the finished front page for make.fun news-image-20261127.

Title: "Friday 27 November 2026 \u2014 41 stories, 11 regions: EU summit
ends with no deal, Gaza toll rises, Asian shares rally".

The picture was drawn locally by the build script; this module is only
the delivery step, and it is deliberately written against the Python
standard library alone. The grader runs the entry in a fresh container
with nothing installed beforehand, a read-only repository and a writable
/output, so this file must not import anything beyond the standard
library \u2014 no Pillow, no third-party packages at all.

What it does: copy entry.png from the repository root into
$MAKEFUN_OUTPUT_DIR (default /output), then prove the copy is exact.
The byte count and the SHA-256 digest of the source and the destination
are computed fresh and must match, the file must be a genuine PNG of
exactly 1024x1024 pixels, and it must stay under the 1 MiB limit.
Anything wrong stops the run with an error instead of handing over a
bad file. The copy is byte-for-byte, so two runs always write the same
bytes.
"""

import hashlib
import os
import shutil
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "entry.png")

_raw_output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
OUTPUT_DIR = _raw_output_dir if _raw_output_dir else "/output"
TARGET = os.path.join(OUTPUT_DIR, "entry.png")

MAX_BYTES = 1048576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
CHUNK_SIZE = 1024 * 1024

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def die(message):
    """Report a fatal problem on stderr and stop with a non-zero exit."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_of(path):
    """Hex SHA-256 digest of the file at path, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path):
    """Read the width and height out of a PNG file's IHDR chunk.

    Only the first 33 bytes are read: the 8-byte signature, the 4-byte
    IHDR length, the 4-byte IHDR tag, then width and height as two
    big-endian unsigned 32-bit integers, plus bit depth and colour type.
    """
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33:
        die(f"file too short to be a PNG: {path}")
    if header[:8] != PNG_SIGNATURE:
        die(f"not a PNG file (bad signature): {path}")
    if header[12:16] != b"IHDR":
        die(f"PNG file has no IHDR chunk first: {path}")
    width, height = struct.unpack(">II", header[16:24])
    bit_depth = header[24]
    colour_type = header[25]
    return width, height, bit_depth, colour_type


def validate_png_chunks(path):
    """Walk every chunk of the PNG and verify each chunk's CRC32.

    The competition requires a whole image: every PNG chunk with its
    checksum and the image data its header describes. A file that was
    truncated or corrupted mid-way still has a valid IHDR, so checking
    the header alone is not enough. This reads the chunk stream
    (length, type, data, CRC) and checks zlib.crc32 over type+data
    against the stored CRC for every chunk, up to and including IEND.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != PNG_SIGNATURE:
        die(f"not a PNG file (bad signature): {path}")
    offset = 8
    saw_iend = False
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        end = offset + 8 + length + 4
        if end > len(data):
            die(f"PNG chunk {chunk_type!r} is truncated in {path}")
        stored_crc = struct.unpack(">I", data[end - 4:end])[0]
        actual_crc = zlib.crc32(data[offset + 4:end - 4]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            die(
                f"PNG chunk {chunk_type!r} has a bad CRC in {path} "
                f"(stored {stored_crc:#010x}, computed {actual_crc:#010x})"
            )
        if chunk_type == b"IEND":
            saw_iend = True
            break
        offset = end
    if not saw_iend:
        die(f"PNG file has no IEND chunk (truncated?): {path}")


def main():
    if not os.path.isfile(SOURCE):
        die(f"source image not found: {SOURCE}")

    source_size = os.path.getsize(SOURCE)
    if source_size > MAX_BYTES:
        die(
            f"source image is {source_size} bytes, over the "
            f"{MAX_BYTES} byte limit"
        )

    width, height, bit_depth, colour_type = png_dimensions(SOURCE)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        die(
            f"unexpected front page size: {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    validate_png_chunks(SOURCE)
    source_hash = sha256_of(SOURCE)
    print(f"source: {SOURCE}")
    print(f"  size: {source_size} bytes")
    print(f"  sha256: {source_hash}")
    print(
        f"  geometry: {width}x{height}, "
        f"bit depth {bit_depth}, colour type {colour_type}"
    )

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except OSError as exc:
        die(f"cannot create output directory {OUTPUT_DIR}: {exc}")

    try:
        shutil.copyfile(SOURCE, TARGET)
    except OSError as exc:
        die(f"copy failed ({SOURCE} -> {TARGET}): {exc}")

    target_size = os.path.getsize(TARGET)
    target_hash = sha256_of(TARGET)
    if target_size != source_size:
        die(
            f"size mismatch after copy: source {source_size} bytes, "
            f"copy {target_size} bytes"
        )
    if target_hash != source_hash:
        die(
            f"SHA-256 mismatch after copy: source {source_hash}, "
            f"copy {target_hash}"
        )

    print(f"output: {TARGET}")
    print(f"  size: {target_size} bytes")
    print(f"  sha256: {target_hash}")
    print(f"verified: {TARGET} matches {SOURCE}")


if __name__ == "__main__":
    main()
