#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
import json
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        # next needed for CORS
        self.send_header('Access-Control-Allow-Origin', '*'),
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type'),
        self.send_header('Access-Control-Allow-Methods', 'POST'),
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        if str(self.path).startswith('/data/'):
            # data = "[[" + str(int(time.time() * 1000)) + "," + str(random.randrange(10)) + "," + str(
                # random.randrange(100)) + "]]"
            self.wfile.write("[".format(self.path).encode('utf-8'))
            f = open("data.txt", "rb")
            self.wfile.write(f.read())
            self.wfile.write("]".format(self.path).encode('utf-8'))
        else:
            f = open("index.html", "rb")
            self.wfile.write(f.read())
            # self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        data = json.loads(post_data.decode('utf-8'))
        rank = data.get('rank')
        if rank == "undefined":
            rank = 0
        # todo fix first value should be without comma
        array = ",[" + str(int(time.time() * 1000)) + "," + data.get('balance') + "," + rank + "]\n"
        f = open("data.txt", "a+")
        f.write(array)
        f.close()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def do_OPTIONS(self):
        self._set_response()
        self.wfile.write("OPTIONS request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
