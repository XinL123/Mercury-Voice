#!/usr/bin/env python3
"""Tiny local server for MERCURY·VOICE with HTTP Range support,
so the browser can seek anywhere in a song instantly."""
import os, re, socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 8765

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        fs = os.fstat(f.fileno())
        size = fs.st_size
        start, end = 0, size - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                if m.group(2):
                    end = int(m.group(2))
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end or start >= size:
                self.send_error(416, "Range not satisfiable")
                f.close()
                return None
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        self._range = (start, end)
        return f

    def copyfile(self, source, outputfile):
        start, end = getattr(self, "_range", (0, None))
        source.seek(start)
        remaining = None if end is None else end - start + 1
        while True:
            n = 65536 if remaining is None else min(65536, remaining)
            chunk = source.read(n)
            if not chunk:
                break
            outputfile.write(chunk)
            if remaining is not None:
                remaining -= len(chunk)
                if remaining <= 0:
                    break

    def log_message(self, *args):
        pass

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with Server(("127.0.0.1", PORT), RangeHandler) as httpd:
        httpd.serve_forever()
