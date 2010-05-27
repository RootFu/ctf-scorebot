import socket
import ssl
import os

from scorebot.attackengine.flagsubmissionbot.SubmitClient import SubmitClient
#from SubmitClient import SubmitClient

def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class Defcon17SubmitClient(SubmitClient):

	def __init__(self):
		self.sock = None
		self.path = modulePath()

	def connect(self):
		s = socket.socket()
		s.settimeout(1.0)
		s.connect(("10.31.100.100",2525))
	
		keyfile_path = os.path.join(self.path,"team_5_key")
		certfile_path = os.path.join(self.path,"team_5_key.cert")

		self.sock = ssl.wrap_socket(
			sock=s,
			keyfile=keyfile_path,
			certfile=certfile_path)

		self.sock.write("TOKENS\n")

	def submit(self,flag):
		self.sock.write("%s\n" % flag)
		line = self.__readline()
		if(line == "200 OK"):
			return SubmitClient.VALID

		if(line == "404 Invalid flag"):
			return SubmitClient.INVALID
		else:
			print "Unknown response!",line
			return SubmitClient.INVALID

	def quit(self):
		self.sock.close()
	
	def __readline(self):
		r = self.sock.recv(1)
                line = r

                while r != "\n":
                        r = self.sock.recv(1)
                        line = line + r

                return line.strip()

"""
foo = Defcon17SubmitClient()
foo.connect()
foo.submit("RAWR")
foo.submit("BLAH")
foo.quit()
"""
