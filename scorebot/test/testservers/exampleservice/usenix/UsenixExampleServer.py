#!/usr/bin/env python
import cgi
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


header = "<html><title>Usenix Example Service</title><body>"
    
footer = "<br><br><form method=\"post\">" \
    "New Flag: <input type=\"text\" name=\"flag\" /> <br>" \
    "<input type=\"submit\" value=\"Submit\" /> </form></body></html>"

form = """<br><br><form method="post">
Username: <input type="text" name="user"/> <br>
Password: <input type="text" name="pass"/> <br>
Data: <input type="text" name="data"/> <br>
<input type="hidden" name="debug" value="false">
<input type="submit" value="Submit"/></form>
"""
 
footer = "</body></html>"

class UsenixHttpHandler(BaseHTTPRequestHandler):

	data = {}
	users = []
 
	def do_GET(self):
		self.send_response(200)
		self.send_header('content-type', 'text/html')
		self.end_headers()
        
		self.wfile.write(header)
		self.wfile.write(form)
		self.wfile.write("<h3>Users:</h3>")
		for user in UsenixHttpHandler.users:
			self.wfile.write("%s <br>" % user)
		self.wfile.write(footer)
        

	def do_POST(self):
		contentType, ct_dict = cgi.parse_header(
			self.headers.getheader('content-type'))

		length_str,cl_dict = cgi.parse_header(
			self.headers.getheader('content-length'))
        
		length = int(length_str)
		form_data = cgi.parse_qs(self.rfile.read(length))

		new_data = form_data['data'][0]
		user = form_data['user'][0]
		passwd = form_data['pass'][0]

		print form_data
		msg = "Set data: %s" % new_data

		if user in UsenixHttpHandler.data:
			usr_pass,old_data = UsenixHttpHandler.data[user]
			if(usr_pass != passwd):
				msg = "Invalid password!"
			else:
				msg += ", old data was %s" % old_data
				UsenixHttpHandler.data[user] = (usr_pass,new_data)
			if(form_data['debug'][0] != "false"):
				msg = "Debug: %s" % old_data
		else:
			UsenixHttpHandler.users.append(form_data['user'][0])
			UsenixHttpHandler.data[user] = (passwd,new_data)

    
		self.send_response(200)
		self.send_header('content-type', 'text/html')
		self.end_headers()
		self.wfile.write(msg)
		
        
def main(): 
	try:
		server = HTTPServer(('',40404), UsenixHttpHandler)
        
		print "Starting SimpleFlag server..."
		server.serve_forever()
        
	except KeyboardInterrupt:
		print "ctrl-c caught, killing server"
		server.socket.close()
        
if __name__ == '__main__':
    main()
