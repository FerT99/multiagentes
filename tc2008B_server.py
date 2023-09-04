# TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
# Python server to interact with Unity via POST
# Sergio Ruiz-Loza, Ph.D. March 2021

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
from gridmodel import ROW_COUNT, COL_COUNT, NUM_ROBOTS, GridModel
import requests

class Server(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        #Enviar en formato JSON
        if self.path == '/unity_url':
            content_length = int(self.headers['Content-length'])
            post_data = int(self.rfile.read(content_length).decode('utf-8'))
            GRID = GridModel(GRID)

        data_to_send = {
            "matrix": GRID 
            }
        
        #Solicitud HTTP POST a Unity para enviar datos
        unity_url = "http://localhost:8585" 
        response = requests.post(unity_url, json=data_to_send)  #Enviar los datos JSON


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n") # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:   # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()