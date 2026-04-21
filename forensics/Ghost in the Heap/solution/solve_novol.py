from __future__ import annotations

import argparse
import base64
import struct


MAGIC = b"CAPV2\x00\x00\x00"


def find_all(data: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    i = 0
    while True:
        j = data.find(needle, i)
        if j < 0:
            return out
        out.append(j)
        i = j + 1


def decode_packets(data: bytes, base: int) -> list[bytes] | None:
    # capv2_hdr_t:
    #  magic[8], count(u32le), blob_len(u32le), xormask(u8), rsv[3]
    if base + 20 > len(data):
        return None
    if data[base : base + 8] != MAGIC:
        return None

    count, blob_len = struct.unpack_from("<II", data, base + 8)
    xormask = data[base + 16]

    if count <= 0 or count > 512:
        return None

    entries_off = base + 20
    blob_off = entries_off + count * 8
    if blob_off > len(data):
        return None

    if blob_len == 0:
        # best-effort: reconstruct from max(entry.off+entry.len)
        max_end = 0
        for i in range(count):
            off, ln = struct.unpack_from("<II", data, entries_off + i * 8)
            max_end = max(max_end, off + ln)
        blob_len = max_end

    if blob_len <= 0 or blob_len > 512 * 512:
        return None
    if blob_off + blob_len > len(data):
        return None

    packets: list[bytes] = []
    for i in range(count):
        off, ln = struct.unpack_from("<II", data, entries_off + i * 8)
        if ln == 0 or ln > 512:
            return None
        if off + ln > blob_len:
            return None
        ob = data[blob_off + off : blob_off + off + ln]
        plain = bytearray(ln)
        for j in range(ln):
            k = (i * 131 + j) & 0xFF
            plain[j] = ob[j] ^ xormask ^ k
        packets.append(bytes(plain))
    return packets


def parse_qname_labels(pkt: bytes) -> list[bytes]:
    # minimal DNS query parsing: header (12 bytes) then QNAME labels
    if len(pkt) < 16:
        raise ValueError("dns packet too short")
    i = 12
    labels: list[bytes] = []
    while True:
        if i >= len(pkt):
            raise ValueError("qname truncated")
        ln = pkt[i]
        i += 1
        if ln == 0:
            break
        if ln > 63 or i + ln > len(pkt):
            raise ValueError("bad label")
        labels.append(pkt[i : i + ln])
        i += ln
    # Expect QTYPE/QCLASS A/IN
    if i + 4 > len(pkt) or pkt[i : i + 4] != b"\x00\x01\x00\x01":
        raise ValueError("not A/IN query")
    return labels


def recover_flag_from_packets(pkts: list[bytes]) -> str | None:
    parts: dict[int, bytes] = {}
    total = None
    for pkt in pkts:
        labs = parse_qname_labels(pkt)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("memdump", help="Path to challenge/dist/memdump.raw")
    args = ap.parse_args()

    data = open(args.memdump, "rb").read()
    hits = find_all(data, MAGIC)
    if not hits:
        raise SystemExit("CAPV2 magic not found")

    for h in hits:
        pkts = decode_packets(data, h)
        if not pkts:
            continue
        flag = recover_flag_from_packets(pkts)
        if flag:
            print(flag)
            return 0

    raise SystemExit("CAPV2 found, but no valid flag recovered")


if __name__ == "__main__":
    raise SystemExit(main())


