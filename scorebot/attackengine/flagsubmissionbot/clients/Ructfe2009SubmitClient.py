import socket
import ssl
import os

#from scorebot.attackengine.flagsubmissionbot.SubmitClient import SubmitClient
#from SubmitClient import SubmitClient

def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class Ructfe2009SubmitClient():
#class Ructfe2009SubmitClient():

	#VALID=0
	#INVALID=1
	#RETRY=2
	def __init__(self):
		self.sock = None
		self.path = modulePath()

	def connect(self):
		print "+++ CONNECT START +++"
		s = socket.socket()
		s.settimeout(1.0)
		s.connect(("checksystem.e.ructf.org",31337))
	
		self.sock = s
		print "HDR:",self.__readline()
		print "HDR:",self.__readline()
		print "HDR:",self.__readline()
		print "HDR:",self.__readline()
		print "+++ CONNECT END +++"

	def submit(self,flag):
		self.sock.send("%s\n" % flag)
		line = self.__readline()

		line = line[1:].strip()
		print "WOOT",line
		if(line.startswith("Accepted")):
			return 0

		if(line.startswith("Denied: your appropriate")):
			return 2
		else:
			return 1

	def quit(self):
		print "+++ QUIT START +++"
		self.sock.close()
		print "+++ QUIT END +++"
	
	def __readline(self):
		r = self.sock.recv(1)
		line = r
		while r != "\n" and len(r) > 0:
			r = self.sock.recv(1)
			line = line + r

		return line.strip()

"""
foo = Ructfe2009SubmitClient()
foo.connect()
foo.submit("=1234567890123456789012345678901")
foo.quit()
"""
