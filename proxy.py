import argparse
import http.cookiejar
import http.cookies
import io
import logging
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.response
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig()

logger = logging.getLogger(__name__)


class PassThroughRedirectHandler(urllib.request.HTTPRedirectHandler):
    # alternative handler
    def http_error_300(self, req, fp, code, msg, header_list):
        data = urllib.response.addinfourl(fp, header_list, req.get_full_url())
        data.status = code
        data.code = code

        return data

    # setup aliases
    http_error_301 = http_error_300
    http_error_302 = http_error_300
    http_error_303 = http_error_300
    http_error_307 = http_error_300


opener = urllib.request.build_opener(PassThroughRedirectHandler)
urllib.request.install_opener(opener)


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def send_response(self, code, message=None):
        # this is a proxy, so I don't want it to add headers. i want to inherit all of these headers.
        self.log_request(code)
        self.send_response_only(code, message)

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
                url = self.path
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
                try:
                    cookie_jar = http.cookiejar.CookieJar()
                    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
                    opener = urllib.request.build_opener(cookie_processor)
                    resp = opener.open(req)
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
                    self.send_header(keyword=name, value=value)
                # cookie?
                for cookie in cookie_jar:
                    try:
                        c = http.cookies.SimpleCookie()
                        c.load(cookie)
                        header = c.output(header="").lstrip()
                        set_message, val = header.split(":")
                        self.send_header("Set-Cookie", val)
                    except AttributeError as e:
                        pass
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
                url = self.path
                req = urllib.request.Request(url=url, method="POST")
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
                    line_parts = [key, value]
                    if len(line_parts) == 2:
                        if line_parts[0].startswith("X-"):
                            pass
                        elif line_parts[0] in ("Connection", "User-Agent"):
                            pass
                        else:
                            sio.write(f"{key}={value}")
                            sio.write("\n")
                            req.add_header(key=key, val=value)
                content_length = int(self.headers.get("Content-Length", 0))
                # Read the request body from the socket
                request_body = self.rfile.read(content_length)
                sio.write(request_body.decode("utf-8"))
                sio.write("\n")
                sio.write("====END REQUEST=======\n")
                logger.error(sio.getvalue() + "\n")
                logger.error("No real error\n")
                try:
                    cookie_jar = http.cookiejar.CookieJar()
                    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
                    opener = urllib.request.build_opener(cookie_processor)
                    resp = opener.open(req, request_body)
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
                    self.send_header(keyword=name, value=value)
                # cookie?
                for cookie in cookie_jar:
                    try:
                        c = http.cookies.SimpleCookie()
                        c.load(cookie)
                        header = c.output(header="").lstrip()
                        set_message, val = header.split(":")
                        self.send_header("Set-Cookie", val)
                    except AttributeError as e:
                        pass
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
