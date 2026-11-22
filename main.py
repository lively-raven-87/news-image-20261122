#!/usr/bin/env python3
"""Deliver the entry image for 'The World — 22 November 2026'.

Stdlib only: reads entry.png beside this file, checks it is a whole PNG
(signature, every chunk's CRC, dimensions, size cap), then copies it to
/output/entry.png and re-reads the copy to prove the copy is complete.
Exits non-zero on any failure.
"""

import os
import shutil
import struct
import sys
import zlib

MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("FAIL:", msg, file=sys.stderr)
    sys.exit(1)


def check_magic(blob):
    if len(blob) < 8 or blob[:8] != PNG_MAGIC:
        fail("not a PNG (bad signature)")


def verify_png(blob):
    """Check every chunk's CRC; return (width, height) from IHDR."""
    pos = 8
    dims = None
    ended = False
    while pos < len(blob):
        if pos + 8 > len(blob):
            fail("chunk header cut off at %d" % pos)
        size = struct.unpack(">I", blob[pos:pos + 4])[0]
        kind = blob[pos + 4:pos + 8]
        stop = pos + 12 + size
        if stop > len(blob):
            fail("chunk %r cut off at %d" % (kind, pos))
        payload = blob[pos + 8:pos + 8 + size]
        want = struct.unpack(">I", blob[pos + 8 + size:stop])[0]
        got = zlib.crc32(payload, zlib.crc32(kind)) & 0xFFFFFFFF
        if got != want:
            fail("CRC mismatch in %r at %d" % (kind, pos))
        if kind == b"IHDR":
            if size != 13:
                fail("IHDR length %d, expected 13" % size)
            dims = struct.unpack(">II", payload[:8])
        elif kind == b"IEND":
            ended = True
            break
        pos = stop
    if dims is None:
        fail("no IHDR chunk")
    if not ended:
        fail("no IEND chunk")
    return dims


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(base, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png missing: %s" % src)
    nbytes = os.path.getsize(src)
    if nbytes > MAX_BYTES:
        fail("entry.png %d bytes, over 1 MiB" % nbytes)
    with open(src, "rb") as fh:
        blob = fh.read()
    if len(blob) != nbytes:
        fail("read %d bytes, expected %d" % (len(blob), nbytes))
    check_magic(blob)
    width, height = verify_png(blob)
    if width > MAX_SIDE or height > MAX_SIDE:
        fail("size %dx%d over %dx%d" % (width, height, MAX_SIDE, MAX_SIDE))
    if width <= 0 or height <= 0:
        fail("bad size %dx%d" % (width, height))

    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as fh:
        back = fh.read()
    if back != blob:
        fail("copy to %s differs from source" % dst)
    # Re-check the copy's dimensions too: the delivered file must be
    # the same valid image, not just the same bytes on disk.
    back_w, back_h = verify_png(back)
    if (back_w, back_h) != (width, height):
        fail("copy dimensions %dx%d differ from %dx%d"
             % (back_w, back_h, width, height))

    print("OK: entry.png %dx%d, %d bytes -> %s"
          % (width, height, nbytes, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
