#!/usr/bin/env python3
"""
Generate DNS TXT payloads for the ARC-7 CTF (gzip+B64 chain + fragment records).
Run from repo root: python ctf-arc7-lab/tools/build_challenge_dns.py
Outputs zone snippets under ctf-arc7-lab/dns/
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import os
import random
import string

# --- Challenge constants (keep in sync with solution.md / terminal.html) ---
ZONE = "vault.arc7.lemaires.fr"
PARENT_ZONE = "lemaires.fr"  # OVH / Terraform zone name (FQDN suffix for all records)
CHAIN_HEAD = "XyQ2wLp9"  # 8 chars; must match hidden hint in player/terminal.html
DECOY_HEAD = "Qm9nVXM0"  # decoy chain → gzip "ACCESS_DENIED"
FLAG_PARTS = {
    "FRAG_C": b"polycyber{arc7_",
    "FRAG_A": b"vault_",
    "FRAG_B": b"txt_recovery}",
}
JUNK_LABELS = ("JUNK01", "JUNK02", "JUNK03")

# Per RFC 1035 each TXT <character-string> is at most 255 octets. Chained record payload
# must fit in one logical string after resolver concatenation: 8-byte pointer + chunk.
DNS_TXT_MAX_SEGMENT = 255
MAX_TXT_BODY = DNS_TXT_MAX_SEGMENT - 8  # room for next-label prefix on non-terminal hops


def rand_label8(rng: random.Random) -> str:
    # Lowercase + digits only so hop labels never collide with FRAG_*/JUNK* (uppercase tokens).
    alphabet = string.ascii_lowercase + string.digits
    return "".join(rng.choice(alphabet) for _ in range(8))


def chain_for_payload(
    zone: str, head: str, payload: bytes, rng: random.Random
) -> dict[str, str]:
    """Linked TXT chain compatible with gzip+b64 reassembly (8-char next + chunk)."""
    raw = base64.b64encode(gzip.compress(payload, compresslevel=9)).decode("ascii")
    chunks: list[str] = []
    for i in range(0, len(raw), MAX_TXT_BODY):
        chunks.append(raw[i : i + MAX_TXT_BODY])
    if not chunks:
        chunks = [""]

    labels = [head]
    while len(labels) < len(chunks):
        labels.append(rand_label8(rng))

    out: dict[str, str] = {}
    for i, chunk in enumerate(chunks):
        if i < len(chunks) - 1:
            nxt = labels[i + 1]
            if len(nxt) != 8:
                raise ValueError(nxt)
            val = nxt + chunk
        else:
            val = "END" + chunk
        fqdn = f"{labels[i]}.{zone}"
        out[fqdn] = val
    return out


def manifest_text() -> str:
    lines = [
        "ARC7-DEEP-MANIFEST/2.1 // recovered from silo telemetry — DO NOT TRUST SURFACE INDEX",
        "ENCODING=gzip+b64+pointer-chain // industry joke; real pull is below",
        "",
        "RECOVERY_PROCEDURE:",
        "  1) Each DATA line: DEPTH | TOKEN | CRC32(decoy)",
        "  2) Sort lines by DEPTH (numeric). Ignore lines where TOKEN starts with JUNK or NULL.",
        "  3) For each TOKEN in sorted order: TXT at <TOKEN>." + ZONE + " — payload is raw base64 (not gzip).",
        "  4) Concatenate decoded bytes in that order. No separators.",
        "",
        "DATA:",
        "07|NULLVOID|deadbeef",
        "01|FRAG_C|cafebabe",
        "04|JUNK01|00000000",
        "02|FRAG_A|b16b00b5",
        "05|JUNK02|11111111",
        "03|FRAG_B|feedface",
        "06|JUNK03|22222222",
        "",
        "NOTE: Surface operators cached a false root at Qm9nVXM0 — expect decoy payload.",
        "NOTE: If your resolver merges TXT, join strings in Answer order before parsing pointers.",
        "",
    ]
    return "\n".join(lines)


def fragment_txt(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def split_txt_segments(value: str, max_len: int = DNS_TXT_MAX_SEGMENT) -> list[str]:
    """Split a logical TXT payload into DNS character-strings (each ≤ max_len octets)."""
    if max_len < 1:
        raise ValueError(max_len)
    return [value[i : i + max_len] for i in range(0, len(value), max_len)]


def fqdn_to_ovh_subdomain(fqdn: str) -> str:
    if not fqdn.endswith("." + PARENT_ZONE):
        raise ValueError(f"FQDN must end with .{PARENT_ZONE}: {fqdn}")
    return fqdn[: -len("." + PARENT_ZONE)]


def terraform_resource_key(fqdn: str) -> str:
    safe = fqdn.replace(".", "_").replace("*", "star")
    if safe[0].isdigit():
        safe = "r_" + safe
    return "arc7_" + safe


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dns_dir = os.path.join(root, "dns")
    os.makedirs(dns_dir, exist_ok=True)

    records: dict[str, str] = {}
    rng_main = random.Random(0x413243375544)
    rng_decoy = random.Random(0x4445434F59)

    # Main manifest chain
    records.update(
        chain_for_payload(ZONE, CHAIN_HEAD, manifest_text().encode("utf-8"), rng_main)
    )

    # Decoy chain → ACCESS_DENIED
    records.update(
        chain_for_payload(
            ZONE,
            DECOY_HEAD,
            b"ACCESS_DENIED // ARC-7 surface cache invalid",
            rng_decoy,
        )
    )

    # Flag fragments + junk
    for label, part in FLAG_PARTS.items():
        records[f"{label}.{ZONE}"] = fragment_txt(part)
    for j in JUNK_LABELS:
        noise = hashlib.sha256(f"junk:{j}".encode()).digest()[:12]
        records[f"{j}.{ZONE}"] = fragment_txt(noise)

    # Optional: red herring TXT on zone apex (some resolvers allow)
    records[f"_arc7-note.{ZONE}"] = (
        "If you are reading this, you already guessed a name. "
        "The archive does not live on obvious hostnames."
    )

    # Write BIND-style snippet (concatenate quoted segments; each ≤255 octets)
    bind_path = os.path.join(dns_dir, "records.bind.snippet")
    with open(bind_path, "w", encoding="utf-8") as f:
        f.write(f"; ARC-7 CTF — zone {ZONE}\n")
        f.write(f"; TXT RDATA: multiple quoted strings concatenate (max 255 chars each)\n")
        for fqdn in sorted(records):
            val = records[fqdn]
            segs = split_txt_segments(val)
            for seg in segs:
                if len(seg) > DNS_TXT_MAX_SEGMENT:
                    raise ValueError((fqdn, len(seg)))
            escaped = '" "'.join(seg.replace("\\", "\\\\").replace('"', '\\"') for seg in segs)
            f.write(f'{fqdn}.\tIN\tTXT\t"{escaped}"\n')

    # Machine-readable: logical TXT (one line); segments column = JSON array for Terraform
    tsv_path = os.path.join(dns_dir, "records.tsv")
    json_path = os.path.join(dns_dir, "arc7_txt_records.json")
    tf_records: list[dict] = []
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("fqdn\ttxt_logical\tsegment_count\n")
        for fqdn in sorted(records):
            val = records[fqdn]
            segs = split_txt_segments(val)
            f.write(f"{fqdn}\t{val}\t{len(segs)}\n")
            tf_records.append(
                {
                    "key": terraform_resource_key(fqdn),
                    "subdomain": fqdn_to_ovh_subdomain(fqdn),
                    "segments": segs,
                }
            )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tf_records, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(records)} records to {bind_path}, {tsv_path}, {json_path}")
    print(f"Chain head FQDN: {CHAIN_HEAD}.{ZONE}")


if __name__ == "__main__":
    main()
