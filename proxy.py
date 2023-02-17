import base64
import http.server
import socketserver
import urllib.parse
import urllib.request
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        post_vars = self.parse_POST()
        self.proxy_request(post_vars=post_vars)

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers["content-type"])
        if ctype == "multipart/form-data":
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == "application/x-www-form-urlencoded":
            length = int(self.headers["content-length"])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_CONNECT(self):
        self.proxy_request()

    def proxy_request(self, **kwargs):
        # Call the handle method of the parent class to set the path instance variable
        try:
            print(self.raw_requestline)
            parsed = http.server.BaseHTTPRequestHandler.parse_request(self)

            if parsed:
                print(self.path)
                print(self.request_version)
                print(self.command)

            # create the proxy request
            response = self.make_request(
                self.path, self.command, kwargs.get("post_vars")
            )
            self.send_response(response.status)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()

            # Edit the response content here if desired
            # Example: content = response.content.replace(b'foo', b'bar')

            # Write the response content to the client
            self.wfile.write(response.content)
        except Exception as e:
            self.send_error(400, f"Error parsing request: {e}")
            return

    def authenticate(self, req):
        # Check for required authentication
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            self.send_error(401, "Authentication Required")
            return False

        # Check the username and password
        auth = base64.b64decode(auth_header[6:]).decode("utf-8").split(":")
        if auth[0] != "username" or auth[1] != "password":
            self.send_error(401, "Authentication Failed")
            return False

        return True

    def make_request(self, path, command, body=None):
        # Make the proxy request
        if body is None and command == "GET":
            with urllib.request.urlopen(path) as response:
                content = response.read()
                return ProxyResponse(response.status, response.headers, content)
        elif body is not None and command == "POST":
            # hope it's a post
            data = urllib.parse.urlencode(body).encode()
            with urllib.request.urlopen(path, data=data) as response:
                # TODO: https://docs.python.org/3/library/urllib.request.html do it the right way
                content = response.read()
                print(content)
                return ProxyResponse(response.status, response.headers, content)


class ProxyResponse:
    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self.content = content


if __name__ == "__main__":
    PORT = 8181
    Handler = ProxyHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server...")
            httpd.server_close()
            print("Server shut down.")
