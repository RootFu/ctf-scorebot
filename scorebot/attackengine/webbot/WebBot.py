import logging
import threading
import Queue
import time
from multiprocessing import Process

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

from scorebot.attackengine.webbot.WebWebserver import WebWebserver

class WebserverThread(threading.Thread):

	def __init__(self,webbot):
		threading.Thread.__init__(self)
		self.webserver = WebWebserver(
			8080,
			webbot.conf,
			webbot.comm,
			webbot.logger,
			webbot)

	def run(self):
		self.webserver.serve()

class WebBot(Process):

	def __init__(self,conf,init=False):
		Process.__init__(self)
		self.conf = conf
		self.comm = None
		self.init = init
		self.webserver = None
		self.logger = conf.buildLogger("WebBot")
		self.cmd_q = Queue.Queue()
		self.buffered_msgs = []
	
	def cmd(self,cmd,q):
		self.cmd_q.put((cmd,q))

	"""
	#Only have to worry about handeling outside events
	#Buffered messages will all be handled after WebBot comms	
	def __getResponse(self, msg_type):
		result = None
	
		while(result == None):
			msg = self.comm.receive()
			if(msg.type == msg_type):
				result = msg
			else:
				self.buffered_msgs.append(msg)

		return result
	"""
		
	def run(self):
		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"ATTACK_WEB_BOT")
	
		self.comm.start()	
		self.webserver = WebserverThread(self)

		self.webserver.start()

		while(True):
			cmd,thread_q = self.cmd_q.get()
			if(cmd == "LIST_EXPLOITS"):
				msg = self.comm.request(BotMessage("LIST_EXPLOITS",None),5)
				assert(msg.type == "LIST_EXPLOITS_RESULT")
				thread_q.put(msg.data)

			elif(cmd == "GET_FLAG_STATS"):
				msg = self.comm.request(BotMessage("GET_FLAG_STATS",None),5)
	
				if(msg != None):
					assert(msg.type == "GET_FLAG_STATS_RESULT")
					thread_q.put(msg.data)
				thread_q.put(None)
				
			elif(cmd.startswith("GET_LOG:")):
				(exploit,lines) = cmd[8:].split("|")
				msg = self.comm.request(BotMessage(cmd,(exploit,lines)),5)
				thread_q.put(msg.data)
			
			elif(cmd.startswith("GET_EXPLOIT:")):
				exploit = cmd[12:]
				msg = self.comm.request(BotMessage(cmd,(exploit,)),5)
				thread_q.put(msg.data)

			elif(cmd.startswith("TOGGLE_EXPLOIT:")):
				self.comm.send(BotMessage(cmd,None))

			msg = self.comm.getPendingMessages()
			if(msg != None):
				self.logger.error("Unexpected message: %r %r" % (msg.type,msg.data))

		self.webserver.join()
