import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import requests
import gridModel

GRID = []

with open("grid.txt", "r") as my_file:
    for line in my_file:
        data = line.split()
        GRID.append(data)

ROW_COUNT = int(GRID[0][0])
COL_COUNT = int(GRID[0][1])
GRID.pop(0)

# counter = 0
# while model.cleanFlag == False:
#     model.step()
#     counter += 1
# if model.cleanFlag == True:
#   print("step", counter)
#   print("CLEAAAAN")

class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        counter = 0
        list_to_send = []
        while gridModel.model.cleanFlag == False:
            data_to_send = {
            "ROW_COUNT": int(ROW_COUNT),
            "COL_COUNT": int(COL_COUNT),
            "ROBOT_POSX": gridModel.model.robotPosx,
            "ROBOT_POSY": gridModel.model.robotPosy,
            "START_X": gridModel.model.startx,
            "START_Y": gridModel.model.starty,
            "KNOWN_GRID": gridModel.model.intGrid
         }
            
            #json_data = json.dumps(data_to_send)
            #self.wfile.write(json_data.encode('utf-8')) 
            list_to_send.append(data_to_send)
            gridModel.model.step()
            counter += 1 
        data_to_send = {
            "ROW_COUNT": int(ROW_COUNT),
            "COL_COUNT": int(COL_COUNT),
            "ROBOT_POSX": gridModel.model.robotPosx,
            "ROBOT_POSY": gridModel.model.robotPosy,
            "START_X": gridModel.model.startx,
            "START_Y": gridModel.model.starty,
            "KNOWN_GRID": gridModel.model.intGrid
         }
        list_to_send.append(data_to_send)
        SendList = {
            "STEP_LIST": list_to_send,
        }
        jsonlist = json.dumps(SendList)
        #print("data::: ", json_data)
        self._set_response()
        self.wfile.write(jsonlist.encode('utf-8')) 
        print("LIST :): ", jsonlist)
        print("model.knowngrid", gridModel.model.knownGrid)
        
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