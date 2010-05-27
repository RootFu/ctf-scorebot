import logging
import threading
from multiprocessing import Process

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

from scorebot.standard.submitbot.SharedObjects import *
from scorebot.standard.submitbot.SubmitWebserver import SubmitWebserver

class WebserverThread(threading.Thread):

	def __init__(self,conf):
		threading.Thread.__init__(self)
		self.conf = conf
		submit_conf = self.conf.getSection("SUBMIT_BOT")
		self.webserver = SubmitWebserver(submit_conf.port,self.conf)

	def run(self):
		self.webserver.serve()

class SubmitBot(Process):

	def __init__(self,conf,init=False):
		Process.__init__(self)
		self.conf = conf
		self.comm = None
		self.init = init
		self.webserver = WebserverThread(self.conf)
		
	def run(self):
		self.webserver.start()

		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"SUBMIT_BOT")

		self.running = True

		collector = getSharedCollector()

		try:
			self.comm.start()
			while(self.running):
				msg = self.comm.receive()
				assert(msg.type == "COLLECT_FLAGS")
				flags = collector.collect()
				self.comm.send(BotMessage("COLLECT_FLAGS_RESULT",flags))
				
			self.comm.kill()
		except Exception as e:
			print "An exception occured in submitbot"
	
