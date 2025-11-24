import os
import json
import urllib.request
import urllib.error
import socket
from typing import Optional

"""Remote Windows dialog client.

Expected environment variables:
  REMOTE_WIN_DIALOG = host:port  (e.g. 192.168.1.20:5005)
  REMOTE_WIN_TIMEOUT = seconds (optional, default 30)
  REMOTE_WIN_MOUNT_PREFIX = Linux mount root for Windows drive mapping
      Example: /mnt/win  (C:\\path\\to\\file.txt -> /mnt/win/C/path/to/file.txt)

Server endpoint:
  GET http://host:port/open  -> {"path": "C:\\..."} or {"path": null}
"""


def request_windows_file() -> Optional[str]:
    target = os.environ.get("REMOTE_WIN_DIALOG")
    if not target:
        return None
    timeout = float(os.environ.get("REMOTE_WIN_TIMEOUT", "30"))
    url = f"http://{target}/open"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            path = data.get("path")
            if not path:
                return None
            return _map_path(path)
    except (urllib.error.URLError, socket.timeout, json.JSONDecodeError):
        return None


def _map_path(win_path: str) -> str:
    """Map a Windows path to a Linux mount if REMOTE_WIN_MOUNT_PREFIX set.

    Example: C:\\Users\\User\\file.txt -> /mnt/win/C/Users/User/file.txt
    """
    prefix = os.environ.get("REMOTE_WIN_MOUNT_PREFIX")
    if not prefix:
        return win_path
    if len(win_path) >= 2 and win_path[1] == ":":  # Drive letter pattern
        drive = win_path[0].upper()
        rest = win_path[2:].lstrip("\\/")
        # Normalize backslashes
        rest = rest.replace("\\", "/")
        return f"{prefix}/{drive}/{rest}"
    return win_path

__all__ = ["request_windows_file"]
