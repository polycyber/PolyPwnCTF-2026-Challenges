#!/usr/bin/env python3
"""
Solve ARC-7 against the live DNS zone (DNS-over-HTTPS).

  python ctf-arc7-lab/tools/solve_live.py

Defaults match the shipped challenge: zone vault.arc7.lemaires.fr, chain head XyQ2wLp9.
For organizers / testing only — do not ship to players.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ZONE = "vault.arc7.lemaires.fr"
DEFAULT_HEAD = "XyQ2wLp9"
DEFAULT_DOH = "https://dns.google/resolve"


def txt_concat_from_doh_payload(payload: dict) -> str:
    """Join TXT RDATA the same way as typical browser loaders (Answer order, type 16)."""
    parts: list[str] = []
    for a in payload.get("Answer", []) or []:
        if a.get("type") != 16:
            continue
        raw = a.get("data")
        if raw is None:
            continue
        if not isinstance(raw, str):
            raw = str(raw)
        # Google often wraps the whole TXT in one pair of quotes
        if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
            raw = raw[1:-1]
        raw = raw.replace('\\"', '"')
        parts.append(raw)
    return "".join(parts)


def fetch_txt(fqdn: str, doh: str, timeout: float) -> str:
    q = urllib.parse.quote(fqdn, safe="")
    url = f"{doh}?name={q}&type=TXT"
    req = urllib.request.Request(url, headers={"Accept": "application/dns-json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode())
    if payload.get("Status") != 0:
        raise RuntimeError(f"DoH status {payload.get('Status')} for {fqdn}")
    s = txt_concat_from_doh_payload(payload)
    if not s:
        raise RuntimeError(f"Empty TXT for {fqdn}")
    return s


def walk_gzip_chain(head: str, zone: str, doh: str, timeout: float) -> str:
    label = head
    b64_parts: list[str] = []
    seen: set[str] = set()
    while True:
        fqdn = f"{label}.{zone}"
        if fqdn in seen:
            raise RuntimeError(f"Loop in chain at {fqdn}")
        seen.add(fqdn)
        raw = fetch_txt(fqdn, doh, timeout)
        if raw.startswith("END"):
            b64_parts.append(raw[3:])
            break
        if len(raw) < 8:
            raise RuntimeError(f"Short TXT at {fqdn}: {raw!r}")
        b64_parts.append(raw[8:])
        label = raw[:8]
    blob = base64.b64decode("".join(b64_parts))
    return gzip.decompress(blob).decode()


def parse_manifest_tokens(manifest: str) -> list[str]:
    rows: list[tuple[int, str]] = []
    for line in manifest.splitlines():
        m = re.match(r"^(\d+)\|([A-Z0-9_]+)\|", line)
        if m:
            rows.append((int(m.group(1)), m.group(2)))
    toks = [
        t
        for _, t in sorted(rows)
        if not t.startswith("JUNK") and not t.startswith("NULL")
    ]
    return toks


def recompose_flag(zone: str, tokens: list[str], doh: str, timeout: float) -> bytes:
    out = b""
    for t in tokens:
        fqdn = f"{t}.{zone}"
        raw = fetch_txt(fqdn, doh, timeout)
        out += base64.b64decode(raw)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zone", default=DEFAULT_ZONE, help="Challenge DNS zone (FQDN)")
    p.add_argument("--head", default=DEFAULT_HEAD, help="First label of gzip+b64 chain")
    p.add_argument("--doh", default=DEFAULT_DOH, help="DNS-over-HTTPS JSON endpoint")
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print manifest and token order",
    )
    args = p.parse_args()

    try:
        manifest = walk_gzip_chain(args.head, args.zone, args.doh, args.timeout)
        if args.verbose:
            print("--- manifest ---")
            print(manifest)
            print("--- end manifest ---")
        tokens = parse_manifest_tokens(manifest)
        if args.verbose:
            print("Fragment order:", tokens)
        flag = recompose_flag(args.zone, tokens, args.doh, args.timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"Network error: {e}", file=sys.stderr)
        return 1
    except (RuntimeError, json.JSONDecodeError, ValueError, gzip.BadGzipFile) as e:
        print(f"Solve error: {e}", file=sys.stderr)
        return 1

    try:
        text = flag.decode()
    except UnicodeDecodeError:
        print(flag)
        return 0

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
