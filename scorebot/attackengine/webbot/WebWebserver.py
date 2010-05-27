import socket
import SocketServer
import re
import sys
import os
import cgi
import struct 
from urlparse import urlparse
import urllib
import Queue
import time

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from scorebot.common.communication.BotMessage import BotMessage

VALID_FILE_REGEX = re.compile("^(/)?\w+\.(html|css|jpg)$")
FILE_PATH = "/"
COMM = None
LOG = None
WEB_BOT = None

def buildWebRootPath(path):
	return FILE_PATH + "/WebRoot/" + path	

class WebHttpHandler(SimpleHTTPRequestHandler):
	
	def __init__(self,arg1,arg2,arg3):
		self.sync_q = Queue.Queue()
		SimpleHTTPRequestHandler.__init__(self,arg1,arg2,arg3)

	def do_GET(self):
		o = urlparse(self.path)

		if o.path == "/index":
			self.do_index()
		elif o.path == "/view":
			self.do_view(cgi.parse_qs(o.query))
		elif o.path == "/log":
			self.do_log(cgi.parse_qs(o.query))
		elif o.path == "/download":
			self.do_download(cgi.parse_qs(o.query))
		elif o.path == "/manual_submit":
			self.do_manual_submit(cgi.parse_qs(o.query))
		elif o.path == "/toggle":
			self.do_toggle(cgi.parse_qs(o.query))
		elif o.path.endswith(".gif") or o.path.endswith(".css") or o.path.endswith(".jpg"):
			self.path = FILE_PATH + "/WebRoot" + self.path
			SimpleHTTPRequestHandler.do_GET(self)
		else:
			self.send_response(302)
			self.send_header("Location", "/index")
			self.end_headers()

	def do_POST(self):
		o = urlparse(self.path)

		environ = {}
        	environ['REQUEST_METHOD'] = "POST"
        	fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=environ)

		if o.path == "/upload":
			self.do_upload(fs)
		else:
			self.send_response(302)
			self.send_header("Location", "/index")
			self.end_headers()

	def log_message(self, format, *args):
		pass

	def do_upload(self,fs):
		if len(fs['exploit'].value) > 0:
			filename = fs['exploit'].filename
			exploit = fs['exploit'].value
			exploit_msg = BotMessage("NEW_EXPLOIT",(
				filename,
				exploit))
			COMM.send(exploit_msg)
			LOG.info("New exploit: %s" % filename)

		self.send_response(302)
		self.send_header("Location", "/index")
		self.end_headers()

	def do_index(self):
		index = open(buildWebRootPath("index.html")).read()

		WEB_BOT.cmd("LIST_EXPLOITS",self.sync_q)
		response = self.sync_q.get()
	
		if(response == None):
			response= []

		# Flag Stats
		WEB_BOT.cmd("GET_FLAG_STATS",self.sync_q)
		flagStats = self.sync_q.get()

		table = "<table>"
		table += "<tr><th>Name</th><th>Active</th><th>New</th><th>Error</th><th>Success</th></tr>"

		for exploit,active in response:

			n = 0 
			e = 0
			s = 0

			if(flagStats != None):
				for stats in flagStats:
					if(exploit == stats[0]):
						n += stats[2]
						e += stats[3]
						s += stats[4]

			table += "<tr>"
			table += "<td><a href=\"/view?%s\">%s</a></td>" % (
				urllib.urlencode({"exploit":exploit}),exploit,)

			if(active):
				table += "<td><a href=\"/toggle?%s\">Enabled</a></td>" % (
					urllib.urlencode({"exploit":exploit}))
			else:
				table += "<td><a href=\"/toggle?%s\">Disabled</a></td>" % (
					urllib.urlencode({"exploit":exploit}))
			
			table += "<td align=right>%d</td><td align=right>%d</td><td align=right>%d</td>" % (n,e,s)
			table += "</tr>"

		table += "</table>"
		index  = index%(table,)
		self.wfile.write(self.getPage(index))

	def do_view(self,qs):
		exploit = qs["exploit"][0]
		
		#Calculate Stats
		WEB_BOT.cmd("GET_FLAG_STATS",self.sync_q)
		flagStats = self.sync_q.get()
		totalStats = {'n':0, 'e':0, 's':0}
		teamStats = {}

		if(flagStats != None):
			for r in flagStats:
				if r[0] == exploit:
					totalStats['n'] = totalStats['n'] + r[2]
					totalStats['e'] = totalStats['e'] + r[3]
					totalStats['s'] = totalStats['s'] + r[4]

				teamStats[r[1]] = {'n':r[2], 'e':r[3], 's':r[4]}

		stats = """<table>
<tr><td>Team</td><td>Queued</td><td>Error</td><td>Success</td>"""


		for (team,s) in teamStats.items():
			stats += """<tr>
<td>%s</td><td>%s</td><td>%s</td><td>%s</td>
</tr>"""%(team,s['n'],s['e'],s['s'])	

		stats += """
<tr><td>Total</td><td>%s</td><td>%s</td><td>%s</td>
</table>"""%(totalStats['n'], totalStats['e'], totalStats['s'])


		viewContent = open(buildWebRootPath("view.html")).read()

		viewContent = viewContent%(exploit,
			urllib.urlencode({"exploit":exploit}),
			urllib.urlencode({"exploit":exploit}),
			stats)
	
		self.wfile.write(self.getPage(viewContent))
	
	def do_log(self,qs):
		exploit = qs["exploit"][0]
		
		lines = 200
		WEB_BOT.cmd("GET_LOG:%s|%s"%(exploit,lines),self.sync_q)
		response = self.sync_q.get()
		log = "<br>".join(response)
		
		logContent = open(buildWebRootPath("log.html")).read()
		self.wfile.write(logContent%(log,))

	def do_download(self,qs):
		exploit = qs["exploit"][0]

		WEB_BOT.cmd("GET_EXPLOIT:%s"%(exploit),self.sync_q)
		exploitData = self.sync_q.get()

		if exploitData != None:
			self.send_response(200)
	
			if exploit.endswith("py") or exploit.endswith("pl") or exploit.endswith("sh"):
				self.send_header("Content-Type","text/plain")
			else:
				self.send_header("Content-Type","application/octet-stream")
						
			self.send_header("Content-Disposition", "inline; filename="+exploit)
			self.end_headers()
			self.wfile.write(exploitData)
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write("404 Not Found")

	def do_toggle(self,qs):
		WEB_BOT.cmd("TOGGLE_EXPLOIT:%s"%(qs["exploit"][0]),self.sync_q)
		self.send_response(302)
		self.send_header("Location", "/index")
		self.end_headers()

	def do_manual_submit(self,qs):
		"""
		Manual submission is a feature that was requested at defcon 2009.
		In adding this feature, im testing out a new method in the comm class
		that should replace the whole WEB_BOT.cmd infrastructure.
		"""
		flag = qs['flag']
		results = COMM.request(BotMessage("MANUAL_FLAG",flag),10.0)
		if(results == None):
			self.wfile.write("Flag submission appears to be down...")
		else:
			self.wfile.write("Submitted flag %s, response was: %r" % ((flag,results.data)))

	def getPage(self, content):
		decoratorHTML = open(buildWebRootPath("decorator.html")).read()
		
		return decoratorHTML%(content,)
	
class WebWebserver(SocketServer.ThreadingMixIn,HTTPServer):

	def __init__(self,port,conf,comm,logger,web_bot):
		global FILE_PATH
		global COMM
		global LOG
		global WEB_BOT

		COMM = comm
		LOG = logger
		WEB_BOT = web_bot

		HTTPServer.__init__(self,('',port),WebHttpHandler)
		
		FILE_PATH = os.path.relpath(os.path.dirname(__file__),sys.path[0])

	def serve(self):
		SocketServer.TCPServer.allow_reuse_addr = True
		self.serve_forever()
