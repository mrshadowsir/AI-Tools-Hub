#!/usr/bin/env python3
"""Tiny dependency-free web server for AI-Tools-Hub."""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import socket

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        print(fmt % args)

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "YOUR-PC-IP"

print("")
print("🆓 Open-Source AI Hub")
print(f"Local: http://127.0.0.1:{PORT}/")
print(f"LAN:   http://{local_ip()}:{PORT}/")
print("Press Ctrl+C to stop.")
print("")
ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
