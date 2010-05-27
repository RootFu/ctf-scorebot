import SocketServer
import random

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class MyTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		print "received connection"
		self.request.send("Please identify your team with its numerical team-number\n")

		#lin = self.request.recv(1024).strip()
		line = self.readLine()

		self.request.send("Welcome 'team "+line+"'. Enter one flag per line, or QUIT when finished\n")
		while True:
			flag = self.readLine()

			if flag == "quit":
				return
		
			r = random.randint(1,100)

			if r < 50:
				self.request.send("Congratulations, you captured a flag!\n")
			elif r < 60:
				self.request.send("Sorry, flag expired\n")
			elif r < 70:
				self.request.send("Sorry, flag not in database\n")
			elif r < 80:
				self.request.send("Sorry, is this a flag?\n")
			elif r < 95:
				self.request.send("Sorry, your team does not have the corresponding service up\n")
			else:
				self.request.send("Sorry, you already submitted this flag\n")
	

	def readLine(self):
		r = self.request.recv(1)
		line = r
	
		while r != "\n":
			r = self.request.recv(1)
			line = line + r

		return line.strip()


if __name__ == "__main__":
	HOST, PORT = "localhost", 9999
	server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
	server.serve_forever()
