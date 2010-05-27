import socket
import SocketServer
import re
import sys
import os
import cgi
import struct 
from urlparse import urlparse
import urllib
import time

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from scorebot.common.communication.BotMessage import BotMessage

VALID_FILE_REGEX = re.compile("^(/)?\w+\.(html|css|jpg)$")
FILE_PATH = "/"
SCORE_TABLE_TEXT = ""

def buildRootPath(path):
	return FILE_PATH + "/ScoreboardRoot/" + path	

class ScoreboardHttpHandler(SimpleHTTPRequestHandler):
	def do_GET(self):
		global VALID_FILE_REGEX
		global FILE_PATH

		o = urlparse(self.path)

		if(VALID_FILE_REGEX.search(o.path) == None):
			self.send_response(302)
			self.send_header("Location", "/index.html")
			self.end_headers()

		else:
			if o.path == "/index.html":
				self.do_index()
			else:
				self.path = buildRootPath(self.path)
				SimpleHTTPRequestHandler.do_GET(self)

	def do_POST(self):
		pass

	def do_index(self):
		global SCORE_TABLE_TEXT

		index = open(buildRootPath("index.html")).read()
		self.wfile.write(self.getPage(index%SCORE_TABLE_TEXT))

	def log_message(self, format, *args):
		pass

	def getPage(self, content):
		decoratorHTML = open(buildRootPath("decorator.html")).read()
		return decoratorHTML%(content,)
	
class ScoreboardWebserver(SocketServer.ThreadingMixIn,HTTPServer):

	def __init__(self,port):
		global FILE_PATH

		HTTPServer.__init__(self,('',port),ScoreboardHttpHandler)
		FILE_PATH = os.path.relpath(os.path.dirname(__file__),sys.path[0])
		self.running = True

	def serve_forever (self):
		SocketServer.TCPServer.allow_reuse_addr = True
		while self.running:
			self.handle_request()

	def updateScoreText(self,text):
		global SCORE_TABLE_TEXT
		SCORE_TABLE_TEXT = text

	def quit(self):
		self.running = False
