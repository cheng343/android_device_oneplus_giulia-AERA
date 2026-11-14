#!/usr/bin/env python3
"""Copy stock recovery vbmeta into a locally built image for experiments.

This does NOT give the new payload an OEM signature or valid AVB verification:
the copied hash descriptors still describe the stock image. Do not relock a
bootloader based on this output. Prefer the normal build image.

Layout produced (identical to how the vendor ships the partition):

    [ 0 .. original_image_size )        payload of the built image
    [ original_image_size .. +vbmeta )  official vbmeta blob (AVB0)
    [ ... zeros ... ]                   padding to the partition size
    [ size-64 .. size )                 AVBf footer pointing at that vbmeta

Usage:
    transplant_avb.py <official-vbmeta> <built-recovery.img> <output.img>

Exit codes: 0 ok, 1 check failed, 2 bad usage.
"""
import struct
import sys
from pathlib import Path

FOOTER_SIZE = 64
VB_META_HEADER_SIZE = 256


def be64(buf, off):
    return struct.unpack_from(">Q", buf, off)[0]


def be32(buf, off):
    return struct.unpack_from(">I", buf, off)[0]


def fail(msg):
    print(f"transplant_avb: {msg}", file=sys.stderr)
    raise SystemExit(1)


def build_footer(major, minor, original_size, vbmeta_size):
    return (
        b"AVBf"
        + struct.pack(">II", major, minor)
        + struct.pack(">QQQ", original_size, original_size, vbmeta_size)
        + b"\x00" * 28
    )


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    vbmeta_path, target_path, output_path = (Path(p) for p in argv[1:])

    vbmeta = vbmeta_path.read_bytes()
    if vbmeta[:4] != b"AVB0":
        fail(f"{vbmeta_path}: does not start with AVB0 (got {vbmeta[:4]!r})")
    auth_size = be64(vbmeta, 12)
    aux_size = be64(vbmeta, 20)
    if VB_META_HEADER_SIZE + auth_size + aux_size != len(vbmeta):
        fail(
            f"{vbmeta_path}: header says {VB_META_HEADER_SIZE + auth_size + aux_size} "
            f"bytes but file is {len(vbmeta)} bytes"
        )

    target = target_path.read_bytes()
    if len(target) < FOOTER_SIZE + len(vbmeta):
        fail(f"{target_path}: too small for a {len(vbmeta)}-byte vbmeta")
    footer_offset = len(target) - FOOTER_SIZE
    footer = target[footer_offset:]
    if footer[:4] != b"AVBf":
        fail(f"{target_path}: no AVBf footer at {footer_offset}")
    major, minor = be32(footer, 4), be32(footer, 8)
    original_size = be64(footer, 12)
    if original_size > footer_offset:
        fail(f"{target_path}: footer original_image_size {original_size} > {footer_offset}")
    if original_size + len(vbmeta) > footer_offset:
        fail(
            f"{target_path}: {len(vbmeta)}-byte vbmeta does not fit between "
            f"{original_size} and {footer_offset}"
        )
    padding = footer_offset - original_size - len(vbmeta)

    out = bytearray()
    out += target[:original_size]
    out += vbmeta
    out += b"\x00" * padding
    out += build_footer(major, minor, original_size, len(vbmeta))
    if len(out) != len(target):
        fail(f"output size {len(out)} != target size {len(target)}")

    # self-checks on the produced bytes
    if bytes(out[-FOOTER_SIZE:-FOOTER_SIZE + 4]) != b"AVBf":
        fail("output footer magic check failed")
    if bytes(out[original_size:original_size + 4]) != b"AVB0":
        fail("output vbmeta magic check failed")
    if bytes(out[original_size:original_size + len(vbmeta)]) != vbmeta:
        fail("output vbmeta content check failed")

    if output_path.exists() and output_path.read_bytes() == bytes(out):
        print(f"{output_path} already up to date ({len(out)} bytes)")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_name(output_path.name + ".tmp")
    tmp.write_bytes(bytes(out))
    tmp.replace(output_path)
    print(
        f"transplanted {len(vbmeta)}-byte vbmeta into {output_path}: "
        f"payload={original_size} padding={padding} size={len(out)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
