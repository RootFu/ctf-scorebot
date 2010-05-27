#!/usr/bin/env python
import cgi
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


header = "<html><title>Simple Flag</title><body>"
    
footer = "<br><br><form method=\"post\">" \
    "New Flag: <input type=\"text\" name=\"flag\" /> <br>" \
    "<input type=\"submit\" value=\"Submit\" /> </form></body></html>"
    
class simpleFlagHttpHandler(BaseHTTPRequestHandler):
    current_flag = "No Flag set"
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write(header)
        self.wfile.write(simpleFlagHttpHandler.current_flag)
        self.wfile.write(footer)
        
    def do_POST(self):
        contentType, ct_dict = cgi.parse_header(
			self.headers.getheader('content-type'))

        length_str,cl_dict = cgi.parse_header(
			self.headers.getheader('content-length'))
        
        length = int(length_str)
        data = cgi.parse_qs(self.rfile.read(length))
        
        flag_text = data['flag'][0]
        simpleFlagHttpHandler.current_flag = flag_text
        
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Success: " + simpleFlagHttpHandler.current_flag)
        
def main(): 
    try:
        server = HTTPServer(('',60001), simpleFlagHttpHandler)
        
        print "Starting SimpleFlag server..."
        server.serve_forever()
        
    except KeyboardInterrupt:
        print "ctrl-c caught, killing server"
        server.socket.close()
        
if __name__ == '__main__':
    main()
