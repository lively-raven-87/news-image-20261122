#!/usr/bin/env python3
"""Ship the entry image for 'The World — 22 November 2026'.

Stdlib only. It reads entry.png next to this file, walks its PNG chunks
checking each CRC, confirms the size caps, then copies it to
/output/entry.png and verifies the copy as well. Any failure exits
non-zero with a FAIL line on stderr.
"""

import os
import shutil
import struct
import sys
import zlib

BYTE_CAP = 1024 * 1024
SIDE_CAP = 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def abort(message):
    print("FAIL:", message, file=sys.stderr)
    sys.exit(1)


def iter_chunks(blob):
    """Yield (kind, payload) for each chunk, CRC-checked as it goes."""
    pos = 8
    while pos < len(blob):
        if pos + 8 > len(blob):
            abort("chunk header cut off at %d" % pos)
        (size,) = struct.unpack(">I", blob[pos:pos + 4])
        kind = blob[pos + 4:pos + 8]
        end = pos + 12 + size
        if end > len(blob):
            abort("chunk %r cut off at %d" % (kind, pos))
        payload = blob[pos + 8:pos + 8 + size]
        (stored,) = struct.unpack(">I", blob[pos + 8 + size:end])
        actual = zlib.crc32(payload, zlib.crc32(kind)) & 0xFFFFFFFF
        if actual != stored:
            abort("CRC mismatch in %r at %d" % (kind, pos))
        yield kind, payload
        pos = end


def dimensions_of(blob):
    """Return (width, height) after verifying the whole PNG."""
    if len(blob) < 8 or blob[:8] != SIGNATURE:
        abort("not a PNG (bad signature)")
    size = None
    saw_end = False
    for kind, payload in iter_chunks(blob):
        if kind == b"IHDR":
            if len(payload) != 13:
                abort("IHDR length %d, expected 13" % len(payload))
            size = struct.unpack(">II", payload[:8])
        elif kind == b"IEND":
            saw_end = True
            break
    if size is None:
        abort("no IHDR chunk")
    if not saw_end:
        abort("no IEND chunk")
    return size


def run():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        abort("entry.png missing: %s" % src)
    nbytes = os.path.getsize(src)
    if nbytes > BYTE_CAP:
        abort("entry.png %d bytes, over 1 MiB" % nbytes)
    with open(src, "rb") as handle:
        blob = handle.read()
    if len(blob) != nbytes:
        abort("read %d bytes, expected %d" % (len(blob), nbytes))
    width, height = dimensions_of(blob)
    if width > SIDE_CAP or height > SIDE_CAP:
        abort("size %dx%d over the %dx%d cap"
              % (width, height, SIDE_CAP, SIDE_CAP))
    if width <= 0 or height <= 0:
        abort("bad size %dx%d" % (width, height))

    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as handle:
        copied = handle.read()
    if copied != blob:
        abort("copy to %s differs from source" % dst)
    # The delivered file must be the same valid image, not merely the
    # same bytes on disk, so verify its dimensions too.
    if dimensions_of(copied) != (width, height):
        abort("copy dimensions differ from %dx%d" % (width, height))

    print("OK: entry.png %dx%d, %d bytes -> %s"
          % (width, height, nbytes, dst))
    return 0


if __name__ == "__main__":
    sys.exit(run())
