import base64
import http.server
import socketserver
import urllib.request


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("TIME TO GET")
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def do_CONNECT(self):
        self.proxy_request()

    def proxy_request(self):
        print("proxying request")
        # Call the handle method of the parent class to set the path instance variable
        try:
            print(self.raw_requestline)
            parsed = http.server.BaseHTTPRequestHandler.parse_request(self)
            # http.server.BaseHTTPRequestHandler.handle_one_request(self)

            if parsed:
                print(self.path)
                print(self.request_version)
                print(self.command)

            # Edit the response headers here if desired
            # Example: response.headers['Content-Type'] = 'text/plain'

            # Write the response headers to the client
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

    def make_request(self, req):
        # Make the proxy request
        print("Making request to", req.path)
        with urllib.request.urlopen(req) as response:
            content = response.read()
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
