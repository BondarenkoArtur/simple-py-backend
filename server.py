#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
import json
import logging
import time
from binascii import unhexlify
from http.server import BaseHTTPRequestHandler, HTTPServer

import os

fmt24 = '%06x'
fmt32 = '%08x'

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
            f = open("data.bin", "rb")
            data = f.read()
            f.close()
            json_string = "["
            for d in range(0, len(data), 11):
                json_string += "["
                json_string += str(1000 * int.from_bytes(data[d + 0:d + 4], byteorder='big'))
                json_string += ","
                json_string += str(int.from_bytes(data[d + 4:d + 8], byteorder='big'))
                json_string += ","
                json_string += str(int.from_bytes(data[d + 8:d + 11], byteorder='big'))
                json_string += "]"
                json_string += ","
            json_string = json_string[:-1] + "]"
            self.wfile.write(json_string.encode("utf-8"))
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
        binary_data = unhexlify(fmt32 % int(time.time()))
        binary_data += unhexlify(fmt32 % int(data.get('balance')))
        binary_data += unhexlify(fmt24 % int(rank))
        if not os.path.exists("data.bin"):
            out_file = open("data.bin", "w+b")
            out_file.write(binary_data)
            out_file.close()
        else:
            if os.path.getsize("data.bin") < 22:
                out_file = open("data.bin", "a+b")
                out_file.write(binary_data)
                out_file.close()
            else:
                out_file = open("data.bin", "r+b")
                out_file.seek(-22, 2)
                file_data = out_file.read()
                if file_data[4:8] == file_data[15:19] and file_data[8:11] == file_data[19:22] and \
                                binary_data[4:8] == file_data[15:19] and binary_data[8:11] == file_data[19:22]:
                    out_file.seek(-11, 2)
                    out_file.write(binary_data)
                    out_file.truncate()
                else:
                    out_file.write(binary_data)
                    out_file.close()
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
