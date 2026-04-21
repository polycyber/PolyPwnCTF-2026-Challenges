#!/usr/bin/env python3

import sys
import socket
import threading
import os

_print = print
def print(*args, **kwargs):
    kwargs['flush'] = True
    _print(*args, **kwargs)

FLAG = os.environ.get("FLAG", "flag{smuggl3d_p4st_th3_w4st3l4nd_f1r3w4ll}")

INDEX_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>VAULT-13 Research Terminal</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ff41;
            font-family: 'VT323', monospace;
            min-height: 100vh;
            padding: 20px;
            background-image: 
                radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a0a 50%),
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 255, 65, 0.03) 2px, rgba(0, 255, 65, 0.03) 4px);
        }
        .terminal {
            max-width: 900px; margin: 0 auto;
            border: 2px solid #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3), inset 0 0 60px rgba(0, 255, 65, 0.05);
            padding: 30px; position: relative;
        }
        .terminal::before {
            content: "VAULT-13 RESEARCH TERMINAL v2.077";
            position: absolute; top: -12px; left: 20px;
            background: #0a0a0a; padding: 0 10px; font-size: 14px;
        }
        .scanline {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, transparent 50%, rgba(0, 0, 0, 0.1) 51%);
            background-size: 100% 4px; pointer-events: none; z-index: 1000;
        }
        h1 { font-size: 2.5em; text-align: center; margin-bottom: 20px;
             text-shadow: 0 0 10px #00ff41; animation: flicker 3s infinite; }
        @keyframes flicker { 0%, 97%, 100% { opacity: 1; } 98%, 99% { opacity: 0.8; } }
        .warning { background: rgba(255, 0, 0, 0.1); border: 1px solid #ff0000;
                   padding: 15px; margin: 20px 0; color: #ff4444; }
        .warning::before { content: "⚠ WARNING: "; font-weight: bold; }
        .info { background: rgba(0, 255, 65, 0.05); border-left: 3px solid #00ff41;
                padding: 15px; margin: 15px 0; font-size: 1.2em; line-height: 1.6; }
        .endpoint { background: #111; padding: 10px 15px; margin: 10px 0;
                    border-left: 3px solid #ff9900; font-size: 1.3em; }
        .blocked { color: #ff4444; }
        .radiation-symbol { font-size: 3em; text-align: center; margin: 20px 0;
                           animation: pulse 2s ease-in-out infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.5; transform: scale(1); }
                          50% { opacity: 1; transform: scale(1.05); } }
        footer { text-align: center; margin-top: 30px; font-size: 0.9em; opacity: 0.6; }
        code { background: #1a1a1a; padding: 2px 8px; border: 1px solid #333; }
    </style>
</head>
<body>
    <div class="scanline"></div>
    <div class="terminal">
        <h1>☢ VAULT-13 RESEARCH LAB ☢</h1>
        <div class="radiation-symbol">☢</div>
        <div class="warning">
            SECURITY PROTOCOL ACTIVE. Our custom firewall blocks the first request to classified endpoints.
        </div>
        <div class="info">
            <strong>SITUATION REPORT:</strong><br><br>
            Year 2287. The wasteland grows more dangerous each day.<br>
            Raiders have been trying to steal our research data.<br><br>
            Classified research location: <code>/classified/research-data</code>
        </div>
        <div class="endpoint">
            <span class="blocked">[PROTECTED]</span> GET /classified/research-data
        </div>
        <footer>
            VAULT-TEC INDUSTRIES © 2077-2287<br>
            "Preparing for the future"
        </footer>
    </div>
</body>
</html>'''

FLAG_HTML = f'''<!DOCTYPE html>
<html>
<head>
    <title>CLASSIFIED RESEARCH DATA</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body {{
            background: #0a0a0a; color: #00ff41; font-family: 'VT323', monospace;
            padding: 40px; display: flex; justify-content: center;
            align-items: center; min-height: 100vh;
        }}
        .container {{
            border: 2px solid #00ff41; padding: 40px; max-width: 700px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.4); text-align: center;
        }}
        h1 {{ color: #ff9900; font-size: 2em; margin-bottom: 20px; }}
        .flag {{
            background: #111; border: 1px dashed #00ff41;
            padding: 20px; margin: 20px 0; font-size: 1.5em;
            word-break: break-all; color: #ffff00;
        }}
        .success {{ color: #00ff41; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>☢ CLASSIFIED RESEARCH DATA ☢</h1>
        <p class="success">ACCESS GRANTED</p>
        <div class="flag">{FLAG}</div>
    </div>
</body>
</html>'''

BLOCKED_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>ACCESS DENIED</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body {
            background: #0a0a0a; color: #ff4444; font-family: 'VT323', monospace;
            padding: 40px; display: flex; justify-content: center;
            align-items: center; min-height: 100vh;
        }
        .container {
            border: 2px solid #ff4444; padding: 40px; max-width: 600px;
            box-shadow: 0 0 30px rgba(255, 68, 68, 0.4); text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⛔ ACCESS DENIED ⛔</h1>
    </div>
</body>
</html>'''


def build_response(status, body):
    response = f'HTTP/1.1 {status}\r\n'
    response += 'Content-Type: text/html; charset=utf-8\r\n'
    response += f'Content-Length: {len(body)}\r\n'
    response += 'Connection: keep-alive\r\n'
    response += '\r\n'
    response += body
    return response.encode()


def parse_one_request(buffer):
    header_end = buffer.find(b'\r\n\r\n')
    if header_end == -1:
        return None, None, {}, 0, 0
    
    header_data = buffer[:header_end].decode('utf-8', errors='replace')
    lines = header_data.split('\r\n')
    
    if not lines:
        return None, None, {}, 0, 0
    
    parts = lines[0].split(' ')
    if len(parts) < 2:
        return None, None, {}, 0, 0
    
    method = parts[0]
    path = parts[1]
    
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    content_length = int(headers.get('content-length', 0))
    total_size = header_end + 4 + content_length
    
    if len(buffer) < total_size:
        return None, None, {}, 0, 0
    
    return method, path, headers, content_length, total_size


def handle_client(client_socket, addr):
    first_request = True
    buffer = b''
    
    try:
        client_socket.settimeout(5)
        
        while True:
            method, path, headers, body_len, consumed = parse_one_request(buffer)
            
            if method is None:
                try:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                    continue
                except socket.timeout:
                    break
            
            buffer = buffer[consumed:]
            
            if first_request and '/classified' in path:
                response = build_response('403 Forbidden', BLOCKED_HTML)
                client_socket.sendall(response)
                first_request = False
                continue
            
            first_request = False
            
            if path == '/' or path == '':
                response = build_response('200 OK', INDEX_HTML)
            elif path == '/classified/research-data':
                response = build_response('200 OK', FLAG_HTML)
            elif path == '/health':
                response = build_response('200 OK', 'OK')
            else:
                response = build_response('404 Not Found', '<h1>404 Not Found</h1>')
            
            client_socket.sendall(response)
            
            if headers.get('connection', '').lower() == 'close':
                break
                
    except Exception:
        pass
    finally:
        client_socket.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5000))
    server.listen(100)
    print("Server running on port 5000")
    
    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    main()
