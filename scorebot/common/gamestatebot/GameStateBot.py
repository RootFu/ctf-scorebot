import asyncore

from multiprocessing import Process

from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo

class GameStateBot(Process):

	def __init__(self, conf, gamelogic):
		Process.__init__(self)
		self.conf = conf
		self.gamelogic = gamelogic
		self.server = None

	def run(self):
		try:
			info = self.conf.getGameStateServerInfo()
			self.server = BotCommServer(info.port,info.key,info.iv,self.gamelogic)
			asyncore.loop()
		except KeyboardInterrupt:
			print "GameStateBot caught keyboard interrupt.."

	def stop(self):
		self.server.close()
