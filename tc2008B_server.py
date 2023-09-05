import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
from gridModel import GRID

class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        if self.path == '/unity_url':
            content_length = int(self.headers['Content-length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parsea los datos JSON recibidos
            data = json.loads(post_data)

            # Accede a los datos individualmente
            ROW_COUNT = data["ROW_COUNT"]
            COL_COUNT = data["COL_COUNT"]
            NUM_ROBOTS = data["NUM_ROBOTS"]

            data["GRID"] = GRID
            
            print("Received POST data:")
            print("ROW_COUNTTT:", ROW_COUNT)
            print("COL_COUNTTT:", COL_COUNT)
            print("NUM_ROBOTSSS:", NUM_ROBOTS)
            print("GRID:", GRID)
            
            # Envía los datos JSON a Unity
            unity_url = "http://localhost:8585" 
            response = requests.post(unity_url, json=data)  # Enviar los datos JSON

            self._set_response()
            self.wfile.write("POST request received and processed successfully".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")  # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()