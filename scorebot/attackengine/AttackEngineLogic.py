import time

from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo
from scorebot.common.gameserver.GameStateLogic import GameStateLogic

class AttackEngineLogic(GameStateLogic):

	def __init__(self,conf):
		self.attackbot_dispatcher = None
		self.webbot_dispatcher = None
		self.flagsubmission_dispatcher = None

		self.attack_conf = conf.getSection("ATTACK_BOT")
		self.bot_server = None
		self.logger = conf.buildLogger("AttackLogic")

		self.time_start = 0
		self.time_end = 0

	def setup(self,bot_server):
		self.bot_server = bot_server

	def handleBotMessage(self,msg,dispatcher):

		if(msg.type == "CLIENT_HELLO"):
			self.__handleNewClient(msg.data,dispatcher)

		elif(msg.type == "COLLECTED_FLAGS"):
			if(self.flagsubmission_dispatcher != None):
				self.flagsubmission_dispatcher.sendMsg(msg)
			else:
				self.logger.warn("Flags captured before flag submit bot connected! (%s)" % str(msg.data[0]))
			
		elif(msg.type == "NEW_EXPLOIT"):
			self.logger.info("Want to add new exploit: %s" % msg.data[0])
			if(self.attackbot_dispatcher != None):
				self.attackbot_dispatcher.sendMsg(msg)
			else:
				self.logger.warn("Exploit added before attackbot connected! (%s)" % msg.data[0])

		elif(msg.type == "LIST_EXPLOITS"):
			if(self.attackbot_dispatcher != None):
				self.attackbot_dispatcher.sendMsg(msg)
			else:
				self.logger.warn("LIST_EXPLOITS called before attackbot connected!")

		elif(msg.type == "LIST_EXPLOITS_RESULT"):
			if(self.webbot_dispatcher != None):
				self.webbot_dispatcher.sendMsg(msg)
			else:
				self.logger.warn("LIST_EXPLOITS_RESULTS called before webbot connected! (%s)" % msg.data)

		elif(msg.type == "GET_FLAG_STATS"):
			if(self.flagsubmission_dispatcher != None):
				self.flagsubmission_dispatcher.sendMsg(msg)
			else:
				self.logger.warn("GET_FLAG_STATS called before flagsubmission connected!")

		elif(msg.type == "GET_FLAG_STATS_RESULT"):
			self.webbot_dispatcher.sendMsg(msg)

		elif(msg.type.startswith("GET_LOG:")):
			self.logger.info("GET_LOG requested")
			self.attackbot_dispatcher.sendMsg(msg)
		
		elif(msg.type.startswith("GET_LOG_RESULT:")):
			self.webbot_dispatcher.sendMsg(msg)
			
		elif(msg.type.startswith("GET_EXPLOIT:")):
			self.logger.info("GET_EXPLOIT requested")
			self.attackbot_dispatcher.sendMsg(msg)
		
		elif(msg.type.startswith("GET_EXPLOIT_RESULT:")):
			self.webbot_dispatcher.sendMsg(msg)
		
		elif(msg.type.startswith("TOGGLE_EXPLOIT:")):
			self.attackbot_dispatcher.sendMsg(msg)

		elif(msg.type == "MANUAL_FLAG"):
			self.flagsubmission_dispatcher.sendMsg(msg)

		elif(msg.type.startswith("MANUAL_FLAG_RESULT")):
			self.webbot_dispatcher.sendMsg(msg)

		else:
			self.logger.warn("Got unknown message %s" % msg.type)
			#dispatcher.sendMsg(BotMessage("TERMINATE",None))
			#self.bot_server.close()

	def __handleNewClient(self,name,dispatcher):
		if name == "ATTACK_BOT":
			self.attackbot_dispatcher = dispatcher
			self.logger.info("New client connected: %s" % name)

		elif name == "ATTACK_WEB_BOT":
			self.webbot_dispatcher = dispatcher
			self.logger.info("New client connected: %s" % name)
		
		elif name == "FLAG_SUBMISSION_BOT": 
			self.flagsubmission_dispatcher = dispatcher
			self.logger.info("New client connected: %s" % name)
		
		elif name == "FLAG_SUBMISSION_BOT_KILL": 
			self.flagsubmission_dispatcher = None
			self.logger.info("Disconnected flag submission bot...")

		else:
			self.logger.error("Unknown client attempted to Connect: %s" % name)
			
	def __checkStart(self):

		if(self.webbot_dispatcher == None):
			return False
		
		if(self.attackbot_dispatcher == None):
			return False

		if(self.flagsubmission_dispatcher == None):
			return False

		return True
