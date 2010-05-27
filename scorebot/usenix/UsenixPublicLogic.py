import time
import shelve
import os

from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo
from scorebot.gamestatebot.GameStateLogic import GameStateLogic
from scorebot.gamelogic.usenix.UsenixScoring import UsenixPublicScoring
from scorebot.gamelogic.usenix.usenixreportbot.UsenixReportBot import UsenixReportBot

class UsenixPublicLogic(GameStateLogic):

	def __init__(self,conf,init=False):
		self.game_started = False
		self.conf = conf
		self.usenix_conf = conf.getSection("USENIX_CONFIG")
		self.scoring = UsenixPublicScoring(self.conf)
		self.logger = self.conf.buildLogger("UsenixPublicLogic")

		self.servicebot_dispatcher = None
		self.reportbot_dispatcher = None
		self.current_round = 1

		persistance_path = os.path.join(self.usenix_conf.data_dir,"usenix_pub.dat")
		self.shelf = shelve.open(persistance_path)

		if(init == True):
			self.shelf["ROUND"] = self.current_round
			self.shelf["SLA"] = self.scoring.getSla()
			self.shelf.sync()
		else:
			self.current_round = self.shelf["ROUND"]
			self.scoring.setSla(self.shelf["SLA"])
			self.scoring.setRound(self.current_round)
		
	def setup(self,bot_server):
		self.bot_server = bot_server

	def handleBotMessage(self,msg,dispatcher):

		if(msg.type == "CLIENT_HELLO"):
			self.__handleNewClient(msg.data,dispatcher)
			if(self.__checkStart()):
				self.logger.info("Game Started")
				self.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.current_round))

		elif(msg.type == "SERVICE_RESULTS"):
			self.scoring.updateServiceResults(msg.data)
			if(self.__endOfGame() == False):
				self.current_round += 1
				self.shelf["ROUND"] = self.current_round
				self.shelf["SLA"] = self.scoring.getSla()
				self.shelf.sync()
				self.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.current_round))

		elif(msg.type == "REQUEST_SLA"):
			sla_msg = self.__getCurrentSLA()
			self.reportbot_dispatcher.sendMsg(BotMessage("REQUEST_SLA_RESULT",sla_msg))

		else:
			self.logger.error("Unknown Message! Going to stop game! %s %s" % (msg.type,str(msg.data)))
			self.__stopGame()

	def __stopGame(self):
		if(self.servicebot_dispatcher != None):
			self.servicebot_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		if(self.reportbot_dispatcher != None):
			self.reportbot_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		self.bot_server.close()
		

	def __handleNewClient(self,name,dispatcher):
		self.logger.info("New client: %s",name)

		if name == "SERVICE_BOT":
			self.servicebot_dispatcher = dispatcher

		if name == "USENIX_REPORT_BOT":
			self.reportbot_dispatcher = dispatcher

	def __checkStart(self):
		if(self.servicebot_dispatcher == None):
			return False

		if(self.reportbot_dispatcher == None):
			return False

		return True

	def __getCurrentSLA(self):
		sla = self.scoring.getSla()
		results = {}
		for team in self.conf.teams:
			results[team.name] = (team.id,sla[team.id])
		return results

	def __endOfGame(self):
		if(self.current_round == self.usenix_conf.getTotalGameRounds()):
			self.logger.info("End of game!")
			self.__stopGame()
			return True
		return False
