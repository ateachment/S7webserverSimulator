# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import json
import os

hostName = "localhost"
serverPort = 80
web_dir = os.path.join(os.path.dirname(__file__), 'htdocs')

class HttpRequestHandler(BaseHTTPRequestHandler):
    def __readVariables(self):
        self.__variables = {}              # initialize an empty dictionary for variables
        with open("variables.json", "r", encoding='utf-8') as file:
            self.__variables = json.load(file)
            print(self.__variables)

    def __writeVariables(self):
        # logic of user programm - motor control with self-holding
        if self.__variables["Motorschutzschalter"] == '0':
            self.__variables["Motorschütz"] = '0'
        
        print(self.__variables)
        with open('variables.json','w', encoding='utf8') as file:
            json.dump(self.__variables, file, ensure_ascii=False)

    def _set_headers(self):      
        self.send_response(200)
        #self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

    def __response(self):
        self._set_headers()
        # Open the html file in read mode
        print(self.path)
        try:
            with open(web_dir + self.path, "r", encoding='utf-8') as (file):
                # Read each line in the file
                for line in file:
                    # parse line and find variables
                    matches = re.findall(r':="(.*?)":', line)   # regular expression matches everything between :=" and ":
                    if len(matches) > 0:                        # replace each match: :="variable": by value
                        for match in matches:
                            variable = match
                            value = self.__variables[variable]
                            line = line.replace(':="' + variable + '":', value)
                    # send each line
                    self.wfile.write(bytes(line, "utf-8"))
        except FileNotFoundError:
            self.send_error(404) # file not found
        except Exception:
            self.send_error(500) # internal server error

    def do_GET(self):
        self.__readVariables()
        self.__writeVariables()
        self.__response()
    
    def do_POST(self):       
        self.__readVariables()
        content_length = int(self.headers['Content-Length'])
        webInput = bytes.decode(self.rfile.read(content_length))   # %22Datenbaustein_Motorschaltung%22.WebStart=1 or
                                                                # %22Datenbaustein_Motorschaltung%22.WebStop=0
        print(webInput)
        
        # logic of user programm - motor control with self-holding
        if webInput == "%22Datenbaustein_Motorschaltung%22.WebStart=1":
            self.__variables["Motorschütz"] = '1'
        if webInput == "%22Datenbaustein_Motorschaltung%22.WebStop=0":
            self.__variables["Motorschütz"] = '0'
        
        self.__writeVariables()
        self.__response()


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), HttpRequestHandler, "htdocs")
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")