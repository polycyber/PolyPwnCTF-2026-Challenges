from __future__ import annotations

import base64
import struct
from typing import Iterable, List, Tuple, Optional

from volatility3.framework import interfaces, exceptions
from volatility3.framework.configuration import requirements
from volatility3.framework.renderers import TreeGrid
from volatility3.framework.renderers import format_hints


MAGIC = b"CAPV2\x00\x00\x00"


def _find_all_in_layer(layer: interfaces.layers.DataLayerInterface, needle: bytes) -> Iterable[int]:
    # Scan the whole layer linearly; for CTF-sized images this is fine.
    # Volatility will handle unmapped reads by raising exceptions; we skip those pages.
    step = 0x1000
    max_addr = layer.maximum_address
    nlen = len(needle)
    buf = b""
    base = 0

    addr = 0
    while addr <= max_addr:
        try:
            chunk = layer.read(addr, step, pad=True)
        except exceptions.InvalidAddressException:
            chunk = b"\x00" * step
        buf = buf[-(nlen - 1) :] + chunk
        base = addr - (len(buf) - len(chunk))
        start = 0
        while True:
            j = buf.find(needle, start)
            if j < 0:
                break
            yield base + j
            start = j + 1
        addr += step


def _decode_packets(blob: bytes, base: int) -> Optional[List[bytes]]:
    if base + 20 > len(blob):
        return None
    if blob[base : base + 8] != MAGIC:
        return None
    count, blob_len = struct.unpack_from("<II", blob, base + 8)
    xormask = blob[base + 16]
    if count <= 0 or count > 512:
        return None

    entries_off = base + 20
    blob_off = entries_off + count * 8
    if blob_off > len(blob):
        return None

    if blob_len == 0:
        max_end = 0
        for i in range(count):
            off, ln = struct.unpack_from("<II", blob, entries_off + i * 8)
            max_end = max(max_end, off + ln)
        blob_len = max_end

    if blob_off + blob_len > len(blob):
        return None

    packets: List[bytes] = []
    for i in range(count):
        off, ln = struct.unpack_from("<II", blob, entries_off + i * 8)
        if ln == 0 or ln > 512:
            return None
        if off + ln > blob_len:
            return None
        ob = blob[blob_off + off : blob_off + off + ln]
        plain = bytearray(ln)
        for j in range(ln):
            k = (i * 131 + j) & 0xFF
            plain[j] = ob[j] ^ xormask ^ k
        packets.append(bytes(plain))
    return packets


def _parse_qname_labels(pkt: bytes) -> List[bytes]:
    if len(pkt) < 16:
        raise ValueError("short")
    i = 12
    labels: List[bytes] = []
    while True:
        ln = pkt[i]
        i += 1
        if ln == 0:
            break
        if ln > 63 or i + ln > len(pkt):
            raise ValueError("bad label")
        labels.append(pkt[i : i + ln])
        i += ln
    if i + 4 > len(pkt) or pkt[i : i + 4] != b"\x00\x01\x00\x01":
        raise ValueError("not query")
    return labels


def _recover_flag_from_packets(pkts: List[bytes]) -> Optional[str]:
    parts = {}
    total = None
    for pkt in pkts:
        labs = _parse_qname_labels(pkt)
        if len(labs) < 3:
            return None
        chunk, seqb, totalb = labs[0], labs[1], labs[2]
        if not (len(seqb) == 3 and seqb.startswith(b"s")):
            return None
        if not (len(totalb) == 3 and totalb.startswith(b"t")):
            return None
        seq = int(seqb[1:3])
        total = int(totalb[1:3])
        parts[seq] = chunk
    if not total or len(parts) != total:
        return None
    b64url = b"".join(parts[i] for i in range(total))
    pad = b"=" * ((4 - (len(b64url) % 4)) % 4)
    return base64.urlsafe_b64decode(b64url + pad).decode("utf-8", errors="replace")


class CAPV2Flag(interfaces.plugins.PluginInterface):
    """Scans a memory layer for CAPV2 blobs and prints the recovered flag."""
    _required_framework_version = (2, 0, 0)
    _version = (1, 0, 0)

    @classmethod
    def get_requirements(cls):
        return [
            requirements.TranslationLayerRequirement(
                name="primary", description="Memory layer to scan (FileLayer/Elf64Layer/etc.)"
            )
        ]

    def _generator(self):
        layer = self.context.layers[self.config["primary"]]

        # Read whole layer into memory (CTF-sized). Keeps plugin simple/reliable.
        size = layer.maximum_address + 1
        try:
            data = layer.read(0, size, pad=True)
        except exceptions.InvalidAddressException:
            # fall back to incremental scan if needed
            data = b""

        if data:
            hits = [i for i in range(0, len(data)) if data.startswith(MAGIC, i)]
        else:
            hits = list(_find_all_in_layer(layer, MAGIC))

        for off in hits:
            if data:
                pkts = _decode_packets(data, off)
            else:
                # carve a reasonable window around the hit
                try:
                    window = layer.read(off, 0x20000, pad=True)
                except exceptions.InvalidAddressException:
                    continue
                pkts = _decode_packets(window, 0)
            if not pkts:
                continue
            flag = _recover_flag_from_packets(pkts)
            if not flag:
                continue
            yield (0, (format_hints.Hex(off), flag))

    def run(self):
        return TreeGrid([("Offset", format_hints.Hex), ("Flag", str)], self._generator())


