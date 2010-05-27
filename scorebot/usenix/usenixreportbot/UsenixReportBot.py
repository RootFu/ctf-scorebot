import os
import Queue
import threading

from multiprocessing import Process

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage
from scorebot.gamelogic.usenix.usenixreportbot.UsenixReportServer import UsenixReportServer

class UsenixReportServerThread(threading.Thread):

	def __init__(self,usenix_report_bot,port):
		threading.Thread.__init__(self)
		addr = ("",port)
		self.usenix_report_server = UsenixReportServer(addr,usenix_report_bot)

	def run(self):
		self.usenix_report_server.serve_forever()
		
class UsenixReportBot(Process):

	def __init__(self,conf,port):
		Process.__init__(self)
		self.conf = conf
		self.comm = None
		self.cmd_q = None
		self.port = port
		self.logger = conf.buildLogger("UsenixReportBot")
		

	def cmd(self,cmd,q):
		self.cmd_q.put((cmd,q))

	def run(self):

		self.cmd_q = Queue.Queue()

		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"USENIX_REPORT_BOT")

		self.comm.start()

		report_thread = UsenixReportServerThread(self,self.port)
		report_thread.setDaemon(True)
		report_thread.start()

		while(True):
			msg = self.comm.receive(False)
			if(msg != None):
				if(msg.type == "TERMINATE"):
					break
			
			try:
				cmd,q = self.cmd_q.get(True,1)
			except Queue.Empty:
				continue

			if(cmd == "SLA_REQ"):
				self.comm.send(BotMessage("REQUEST_SLA",None))
				msg = self.comm.receive()
				
				if(msg.type == "TERMINATE"):
					break

				elif(msg.type == "REQUEST_SLA_RESULT"):
					q.put(msg.data)

			elif(cmd == "SRV_REQ"):
				self.comm.send(BotMessage("REQUEST_REPORT",None))
				msg = self.comm.receive()
				
				if(msg.type == "TERMINATE"):
					break

				elif(msg.type == "REQUEST_REPORT_RESULT"):
					q.put(msg.data)

		self.comm.kill()
