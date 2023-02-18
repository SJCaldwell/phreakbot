#!/usr/bin/env python

import argparse
import io
import logging
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig()

logger = logging.getLogger(__name__)


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        sent = False
        try:
            req = None
            resp = None
            sio = io.StringIO()
            try:
                hostname = self.headers.get("Host")
                if not hostname:
                    hostname = "localhost"
                print("The hostname is:")
                print(hostname)
                url = "http://{}".format(hostname)
                print(url)
                req = urllib.request.Request(url=url)
                sio.write("====BEGIN REQUEST=====\n")
                sio.write(url)
                sio.write("\n")
                sio.write(self.command)
                sio.write(" ")
                sio.write(self.path)
                sio.write(" ")
                sio.write(self.request_version)
                sio.write("\n")
                for line in self.headers:
                    line_parts = [o.strip() for o in line.split(":", 1)]
                    print(line_parts)
                    if len(line_parts) == 2:
                        if line_parts[0].startswith("X-"):
                            pass
                        elif line_parts[0] in ("Connection", "User-Agent"):
                            pass
                        else:
                            sio.write(line)
                            req.add_header(*line_parts)
                sio.write("\n")
                sio.write("====END REQUEST=======\n")
                logger.error(sio.getvalue())
                try:
                    print("req is")
                    print(req)
                    print(req.get_full_url())
                    resp = urllib.request.urlopen(req)
                except urllib.error.HTTPError as e:
                    if e.getcode():
                        resp = e
                    else:
                        self.send_error(599, "error proxying: {}".format(str(e)))
                        sent = True
                        return
                self.send_response(resp.getcode())
                respheaders = resp.info()
                for line in resp.headers:
                    line_parts = line.split(":", 1)
                    if len(line_parts) == 2:
                        self.send_header(*line_parts)
                self.end_headers()
                sent = True
                if body:
                    self.wfile.write(resp.read())
                return
            finally:
                if resp:
                    resp.close()
                sio.close()
        except IOError as e:
            if not sent:
                self.send_error(404, "error trying to proxy: {}".format(str(e)))


def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Either Proxy or Echo HTTP requests")
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=random.randint(20000, 60000),
        help="serve HTTP requests on specified port (default: random)",
    )
    parser.add_argument(
        "--type",
        dest="server_type",
        choices=["echo", "proxy"],
        default="echo",
        help="Whether to run as a proxy server or echo server",
    )
    args = parser.parse_args(argv)
    return args


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print(("http server is starting on port {}...".format(args.port)))
    server_address = ("127.0.0.1", args.port)
    if args.server_type == "proxy":
        httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    else:
        httpd = HTTPServer(server_address, EchoHTTPRequestHandler)
    print(("http server is running as {}...".format(args.server_type)))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
