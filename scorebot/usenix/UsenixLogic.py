import time
import os
import shelve
import subprocess
import threading

from scorebot.common.communication.BotMessage import BotMessage
from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo
from scorebot.common.models.Flag import Flag,FlagManager,FlagParseException
from scorebot.gamestatebot.GameStateLogic import GameStateLogic
from scorebot.gamelogic.usenix.UsenixScoring import UsenixPrivateScoring

class RebootThread(threading.Thread):

	def __init__(self,usenix_logic):
		threading.Thread.__init__(self)
		self.usenix_logic = usenix_logic

	def run(self):
		reboot_tasks = []
		for team in self.usenix_logic.conf.teams:
			reboot_tasks.append(subprocess.Popen([
				'/usr/bin/ssh',
				'-i/home/scorebot/.ssh/id_rsa',
				'root@'+team.host,
				'reboot'],close_fds=True))

		self.usenix_logic.logger.warn("(THREAD HACK!)Wating for team systems to restart..")
		time.sleep(self.usenix_logic.usenix_conf.rebootTime())
		for task in reboot_tasks:
			task.kill()

		self.usenix_logic.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.usenix_logic.service_round))
		self.usenix_logic.service_round += 1
		self.usenix_logic.partial_round += 1

class UsenixLogic(GameStateLogic):

	STATE_PRE_GAME_START = 0
	STATE_ROUND_RUNNING = 1
	STATE_EXPLOITS_RUNNING = 2
	STATE_UPDATE_SCOREBOARD = 3

	def __init__(self,conf,init=False):
		self.game_started = False
		self.conf = conf
		self.usenix_conf = conf.getSection("USENIX_CONFIG")
		self.servicebot_conf = conf.getSection("SERVICE_BOT")
		self.scoring = UsenixPrivateScoring(self.conf)

		self.usenix_resetbot_dispatcher = None
		self.exploitbot_dispatcher = None
		self.servicebot_dispatcher = None
		self.usenix_scoreboard_dispatcher = None
		self.usenix_reportbot_dispatcher = None

		self.partial_round = 0
		self.service_round = 0
		self.exploit_round = 0
		self.current_round = 1

		self.logger = self.conf.buildLogger("UsenixLogic")
		self.fm = self.conf.buildFlagManager()

		self.team_scores = [0.0] * self.conf.numTeams()
		self.recent_service_results = None

		self.exploit_to_service_map = [-1]*len(self.usenix_conf.exploits)
		for exploit in self.usenix_conf.exploits:
			for service in self.servicebot_conf.services:
				if(exploit.service == service.name):
					self.exploit_to_service_map[exploit.id] = service.id
					break

			assert(self.exploit_to_service_map[exploit.id] != -1),"Exploit %s - No valid service named %s" % (
				exploit.name,
				exploit.service)

		persistance_path = os.path.join(self.usenix_conf.data_dir,"usenix.dat")
		self.logger.debug("Persistance path: %s",persistance_path)
		self.shelf = shelve.open(persistance_path)

		if(init == True):
			self.shelf["PARTIAL"] = self.partial_round
			self.shelf["ROUND"] = self.current_round
			self.shelf["SCORES"] = self.team_scores
			self.shelf.sync()
		else:
			self.partial_round = self.shelf["PARTIAL"]
			self.current_round = self.shelf["ROUND"]
			self.team_scores = self.shelf["SCORES"]

	def setup(self,bot_server):
		self.bot_server = bot_server

	def handleBotMessage(self,msg,dispatcher):
		if(msg.type == "CLIENT_HELLO"):
			self.__handleNewClient(msg.data,dispatcher)
			if(self.__checkStart()):
				self.logger.info("Game Started")
				self.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.partial_round))
				self.service_round += 1
				self.partial_round += 1

		elif(msg.type == "SERVICE_RESULTS"):
			partial_count = self.usenix_conf.getServiceRoundCount()
			self.recent_service_results = msg.data

			self.scoring.updateRoundResults(msg.data)
			if(self.partial_round % (partial_count+1) != partial_count):
				self.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.service_round))
				self.service_round += 1
			else:
				self.exploitbot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.exploit_round))
				self.exploit_round += 1
			self.partial_round += 1

		elif(msg.type == "USENIX_EXPLOIT_RESULTS"):
			self.logger.debug("Received exploit results!")
			sla_scores = self.scoring.getServiceSLA(self.usenix_conf.getServiceRoundCount())
			self.__updateTeamScores(msg.data,sla_scores)
			
			self.logger.info("=== End of Round %d ===" % self.current_round)
			for team in self.conf.teams:
				self.logger.info("Team %s: %f" % (team.name,self.team_scores[team.id]))

			if(self.__endOfGame() == False):
				self.current_round += 1
				#Store round data..
				self.shelf["PARTIAL"] = self.partial_round
				self.shelf["ROUND"] = self.current_round
				self.shelf["SCORES"] = self.team_scores
				self.shelf.sync()

				self.logger.info("=== Reset Team Systems ===")
				reboot_thread = RebootThread(self)
				reboot_thread.daemon = True
				reboot_thread.start()
				"""
				for team in self.conf.teams:
					subprocess.call([
						'/usr/bin/ssh',
						'-i/home/scorebot/.ssh/id_rsa',
						'root@'+team.host,
						'reboot'
						'&'],close_fds=True, shell=True)

				self.logger.debug("Wating for team systems to restart..")
				time.sleep(self.usenix_conf.rebootTime())

				self.servicebot_dispatcher.sendMsg(BotMessage("EXECUTE_ROUND",self.service_round))
				self.service_round += 1
				self.partial_round += 1
				"""

		elif(msg.type == "REQUEST_REPORT"):
			results = self.__buildReportResult()
			self.usenix_reportbot_dispatcher.sendMsg(BotMessage("REQUEST_REPORT_RESULT",results))

		else:
			self.logger.error("Unknown Message! Going to stop game! %s %s" % (msg.type,str(msg.data)))
			self.__stopGame()

	def __updateTeamScores(self,exploit_results,sla_scores):
		for exploit_result in exploit_results:
			exploitId, exploit_result_list = exploit_result
			serviceId = self.exploit_to_service_map[exploitId]
			service = self.servicebot_conf.getServiceInfoById(serviceId)
			exploit = self.usenix_conf.getExploitById(exploitId)
			for teamId,exploit_success,flags in exploit_result_list:
				team = self.conf.getTeamInfoById(teamId)
				exploit_success = self.__checkExploitSuccess(exploitId,teamId,exploit_success,flags)
				service_sla = 0.0
				if(exploit_success == True):
					service_sla = self.__getSLA(exploitId,teamId,sla_scores)/3.0
				else:
					service_sla += self.__getSLA(exploitId,teamId,sla_scores)

				self.team_scores[teamId] += service_sla
				self.logger.info("Team=%s service=%s (sla=%f) exploit=%s (success=%s)" % (
					team.name,
					service.name,
					service_sla,
					exploit.name,
					str(exploit_success)))

	def __getSLA(self,exploitId,teamId,sla_scores):
		serviceId = self.exploit_to_service_map[exploitId]
		return sla_scores[teamId][serviceId]

	def __checkExploitSuccess(self,exploitId,teamId,exploit_success,flags):
		exploit = self.usenix_conf.exploits[exploitId]

		if(exploit.captures_flags == False and exploit_success == True):
			return True

		if(exploit.captures_flags == True):
			serviceId = self.exploit_to_service_map[exploitId]
			round_count = self.usenix_conf.getServiceRoundCount()
			for flag in flags:
				f = None
				try: 
					f = self.fm.toFlag(flag)
				except Exception:
					self.logger.info("Exploit %s captured INVALID flag! (%r)" % (exploit.name,flag))
					continue

				if(f == None):
					continue

				if(	f.teamId == teamId and 
					f.serviceId == serviceId and
					self.service_round - f.round <= round_count):
					self.logger.info("Exploit %s captured VALID flag!" % (exploit.name))
					return True

				else:
					self.logger.debug("INVALID flag! tid (%d,%d) sid(%d,%d) Current round=%d, flag round=%d total=%d" % (
						f.teamId,teamId,
						f.serviceId,serviceId,
						self.service_round, f.round,round_count))
				
		return False

	def __stopGame(self):
		if(self.exploitbot_dispatcher != None):
			self.exploitbot_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		if(self.servicebot_dispatcher != None):
			self.servicebot_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		if(self.usenix_scoreboard_dispatcher != None):
			self.usenix_scoreboard_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		if(self.usenix_resetbot_dispatcher != None):
			self.usenix_resetbot_dispatcher.sendMsg(BotMessage("TERMINATE",None))

		self.bot_server.close()

	def __handleNewClient(self,name,dispatcher):
		self.logger.info("New client: %s",name)

		if name == "USENIX_EXPLOIT_BOT":
			self.exploitbot_dispatcher = dispatcher

		if name == "SERVICE_BOT":
			self.servicebot_dispatcher = dispatcher

		if name == "USENIX_REPORT_BOT":
			self.usenix_reportbot_dispatcher = dispatcher

	def __checkStart(self):
		if(self.exploitbot_dispatcher == None):
			return False

		if(self.servicebot_dispatcher == None):
			return False

		if(self.usenix_reportbot_dispatcher == None):
			return False

		return True

	def __endOfGame(self):
		if(self.current_round == self.usenix_conf.getTotalGameRounds()):
			self.logger.info("End of game!")
			self.__stopGame()
			return True
		return False

	def __buildReportResult(self):

		# { "team_name" : (team_score, [ (service_name, service status)] ) }

		results = {}
		service_stats = None
		if(self.recent_service_results != None):
			round,service_stats =  self.recent_service_results

		for team in self.conf.teams:
			service_result_list = []
			for service in self.servicebot_conf.services:
				if(service_stats != None):
					service_result_list.append((service.name,service_stats[team.id][service.id]))
				else:
					service_result_list.append((service.name,'e'))

			results[team.name] = (self.team_scores[team.id],service_result_list)

		self.logger.debug("REPORT REQUEST RESULT: %r" % results)
		return results
