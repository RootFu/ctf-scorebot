
import SocketServer
import Queue
import cPickle

REPORT_BOT = None

class UsenixReportHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		global REPORT_BOT
		line = self.__readline()

		if(line == "SLA"):
			thread_q = Queue.Queue()
			REPORT_BOT.cmd("SLA_REQ",thread_q)
			result = thread_q.get()
			result_txt = cPickle.dumps(result,cPickle.HIGHEST_PROTOCOL)
			self.request.send(result_txt)

		if(line == "SRV"):
			thread_q = Queue.Queue()
			REPORT_BOT.cmd("SRV_REQ",thread_q)
			result = thread_q.get()
			result_txt = cPickle.dumps(result,cPickle.HIGHEST_PROTOCOL)
			self.request.send(result_txt)
		

	def __readline(self):
		line = ""

		while(True):
			c = self.request.recv(1)
			if(c == '\n' or c == ''):
				break
			else:
				line += c
		return line

class UsenixReportServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

	def __init__(self,addr,report_bot):
		global REPORT_BOT
		SocketServer.TCPServer.allow_reuse_address = True
		SocketServer.TCPServer.__init__(self,addr,UsenixReportHandler)

		REPORT_BOT = report_bot
