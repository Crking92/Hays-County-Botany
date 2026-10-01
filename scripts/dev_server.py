#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 8000

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    print(f"Hays Botany learner server: http://localhost:{PORT}")
    print("Browser caching is disabled so interface updates appear immediately.")
    ThreadingHTTPServer(("127.0.0.1", PORT), NoCacheHandler).serve_forever()
