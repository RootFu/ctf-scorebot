
from multiprocessing import Process
import asyncore

from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.gameserver.GameStateLogic import GameStateLogic

key = "0123456789012345"
iv = "ABCDEFGH"
port = 424242

class TestLogic(GameStateLogic):

	def __init__(self):
		self.stored = 0
		self.dispatchers = {}
		self.req2_count = 0

	def handleBotMessage(self,msg,dispatcher):
		if(msg.type == "norm"):
			dispatcher.sendMsg(msg)

		elif(msg.type == "rev"):
			msg.data.reverse()
			dispatcher.sendMsg(msg)
		
		elif(msg.type == "foo"):
			if(self.stored == 2):
				self.dispatchers["BAR"].sendMsg(BotMessage("BAR","Got Foo?"))
			else:
				self.stored += 1

		elif(msg.type == "req1"):
			dispatcher.sendMsg(BotMessage("req_result1",msg.data))

		elif(msg.type == "req2"):
			self.req2_count += 1
			dispatcher.sendMsg(BotMessage("norm",self.req2_count))
			dispatcher.sendMsg(BotMessage("req_result2",msg.data))

		elif(msg.type == "CLIENT_HELLO"):
			self.dispatchers[msg.data] = dispatcher

		else:
			print "WHAT DO I DO WITH THIS MSG???",msg.type,msg.data


	def setup(self,bot_server):
		print "TestServer -- Setup"

class TestServer(Process):

	def run(self):
		logic = TestLogic()
		srv = BotCommServer(port,key,iv,logic)
		asyncore.loop()
