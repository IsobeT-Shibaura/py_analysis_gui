#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Windows host side dialog server.

Run this script on a Windows 11 machine. It exposes a very small HTTP API:
  GET /open  -> JSON {"path": "C:\\..."}  (null if user cancels)

Environment variables:
  WIN_DIALOG_BIND=host:port   (default 0.0.0.0:5005)

Security note: This is a minimal demo and provides no authentication.
Run only in a trusted network or wrap with reverse proxy + auth.
"""
import os
import json
import ctypes
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, HTTPServer

class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPWSTR),
        ("lpstrTitle", wintypes.LPWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID),
        ("lpTemplateName", wintypes.LPWSTR),
        ("pvReserved", wintypes.LPVOID),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]

OFN_FILEMUSTEXIST = 0x00001000
OFN_PATHMUSTEXIST = 0x00000800


def open_file_dialog() -> str | None:
    buffer_size = 65535
    file_buffer = ctypes.create_unicode_buffer(buffer_size)
    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    ofn.hwndOwner = 0
    ofn.hInstance = 0
    ofn.lpstrFilter = "All Files\0*.*\0Log Files (*.log)\0*.log\0\0"
    ofn.nFilterIndex = 1
    ofn.lpstrFile = file_buffer
    ofn.nMaxFile = buffer_size
    ofn.lpstrTitle = "Select log file"
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        value = file_buffer.value.strip()
        return value if value else None
    return None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/open":
            path = None
            try:
                path = open_file_dialog()
            except Exception:
                path = None
            data = json.dumps({"path": path})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):  # Silence default logging
        return


def main():
    bind = os.environ.get("WIN_DIALOG_BIND", "0.0.0.0:5005")
    host, port = bind.split(":", 1)
    httpd = HTTPServer((host, int(port)), Handler)
    print(f"[win_dialog_server] Listening on http://{bind}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
