from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo
from scorebot.common.gameserver.GameStateLogic import GameStateLogic

from scorebot.standard.Scoring import BasicScoring

#from scorebot.servicebot.ServiceBotHandler import ServiceBotHandler
#from scorebot.submitbot.SubmitBotHandler import SubmitBotHandler

class StandardCTF(GameStateLogic):

	def __init__(self,conf,init=False):
		self.bot_server = None

		self.servicebot_dispatcher = None
		self.submitbot_dispatcher = None
		self.scoreboardbot_dispatcher = None

		self.conf = conf
		self.servicebot_conf = conf.getSection("SERVICE_BOT")
		self.logger = conf.buildLogger("StandardCTF")

		self.scoring = BasicScoring(conf)
		self.service_status = None

	def setup(self,bot_server):
		self.bot_server = bot_server

	def handleBotMessage(self,msg,dispatcher):

		if(msg.type == "CLIENT_HELLO"):
			self.__handleNewClient(msg.data,dispatcher)

		elif(msg.type == "SERVICE_RESULTS"):
			self.__handleServiceResults(msg.data)

		elif(msg.type == "COLLECT_FLAGS_RESULT"):
			self.__handleSubmitResults(msg.data)

		else:
			self.logger.error("Unknown message: %r %r" % (msg.type,msg.data))

	def __handleNewClient(self, name, dispatcher):
		self.logger.info("New client: %s",name)

		if(name == "SERVICE_BOT"):
			if(self.servicebot_dispatcher == None):
				self.servicebot_dispatcher = dispatcher
			else:
				self.logger.error("Service Bot tried to connect again!")
				return

		if(name == "SUBMIT_BOT"):
			if(self.submitbot_dispatcher == None):
				self.submitbot_dispatcher = dispatcher
			else:
				self.logger.error("Submit Bot tried to connect again!")
				return
		
		if(name == "SCOREBOARD_BOT"):
			if(self.scoreboardbot_dispatcher == None):
				self.scoreboardbot_dispatcher = dispatcher
			else:
				self.logger.error("Scoreboard Bot tried to connect again!")
				return

		if(self.__checkStart() == True):
			self.__startGame()

	def __checkStart(self):

		if(self.servicebot_dispatcher == None):
			return False
		
		if(self.submitbot_dispatcher == None):
			return False

		if(self.scoreboardbot_dispatcher == None):
			return False

		return True

	def __startGame(self):
		init_game = True

		if(init_game):
			self.round = 1

		execute_msg = BotMessage("EXECUTE_ROUND",self.round)
		self.servicebot_dispatcher.sendMsg(execute_msg)

	def __handleServiceResults(self,service_results):
		round, data = service_results
		assert(self.round == round)
		self.service_status = data
		self.scoring.updateDefensiveInfo(data)
		self.submitbot_dispatcher.sendMsg(BotMessage("COLLECT_FLAGS",None))

	def __handleSubmitResults(self,submit_results):
		self.scoring.updateOffensiveInfo(submit_results)
		self.__endRound()

	def __endRound(self):
		self.logger.debug("Ending round %d" % self.round)
		team_off_scores,team_def_scores = self.scoring.updateRoundScores(self.round)
		self.scoreboardbot_dispatcher.sendMsg(BotMessage(
			"UPDATE_SCORES",(team_off_scores,team_def_scores,self.service_status)))

		self.round += 1
		execute_msg = BotMessage("EXECUTE_ROUND",self.round)
		self.servicebot_dispatcher.sendMsg(execute_msg)
