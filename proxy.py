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
                url = "http://{}".format(hostname)
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
                print("TRYING TO SEND HEADERS")
                print(self.headers)
                for line in self.headers:
                    key = line
                    value = self.headers.get(key)

                    line_parts = [key, value]
                    print(f"GET REQUEST HEADER: {line}")
                    if len(line_parts) == 2:
                        if line_parts[0].startswith("X-"):
                            pass
                        elif line_parts[0] in ("Connection", "User-Agent"):
                            pass
                        else:
                            sio.write(line)
                            req.add_header(key=key, val=value)
                sio.write("\n")
                sio.write("====END REQUEST=======\n")
                logger.error(sio.getvalue() + "\n")
                try:
                    resp = urllib.request.urlopen(req)
                except urllib.error.HTTPError as e:
                    if e.getcode():
                        resp = e
                    else:
                        self.send_error(599, "error proxying: {}".format(str(e)))
                        sent = True
                        return
                self.send_response(resp.getcode())
                headers = resp.getheaders()
                for header in headers:
                    name, value = header
                    print(f"HEADER BEING WRITTEN TO BE SENT TO CLIENT: {name}: {value}")
                    self.send_header(keyword=name, value=value)
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

    def do_POST(self, body=True):
        sent = False
        try:
            req = None
            resp = None
            sio = io.StringIO()
            try:
                hostname = self.headers.get("Host")
                if not hostname:
                    hostname = "localhost"
                url = "http://{}".format(hostname)
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
                    key = line
                    value = self.headers.get(key)
                    print(f"HEADER BEING WRITTEN TO BE SENT TO TARGET: {key}")
                    line_parts = [key, value]
                    if len(line_parts) == 2:
                        if line_parts[0].startswith("X-"):
                            pass
                        elif line_parts[0] in ("Connection", "User-Agent"):
                            pass
                        else:
                            sio.write(line)
                            req.add_header(key=key, val=value)
                sio.write("\n")
                sio.write("====END REQUEST=======\n")
                logger.error(sio.getvalue() + "\n")
                logger.error("No real error\n")
                try:
                    resp = urllib.request.urlopen(req)
                except urllib.error.HTTPError as e:
                    if e.getcode():
                        resp = e
                    else:
                        self.send_error(599, "error proxying: {}".format(str(e)))
                        sent = True
                        return
                self.send_response(resp.getcode())
                headers = resp.getheaders()
                for header in headers:
                    name, value = header
                    print(f"HEADER BEING WRITTEN TO BE SENT TO CLIENT: {name}: {value}")
                    self.send_header(keyword=name, value=value)
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
        default=8181,
        help="serve HTTP requests on specified port (default: random)",
    )
    args = parser.parse_args(argv)
    return args


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print(("http server is starting on port {}...".format(args.port)))
    server_address = ("127.0.0.1", args.port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print("http server is running as proxy")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
