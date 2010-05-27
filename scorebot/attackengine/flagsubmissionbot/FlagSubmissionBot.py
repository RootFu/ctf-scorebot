from multiprocessing import Process
import os
import time
from scorebot.attackengine.flagsubmissionbot.FlagSubmitter import FlagSubmitter
#from scorebot.attackengine.flagsubmissionbot.clients.Defcon17SubmitClient import Defcon17SubmitClient
from scorebot.attackengine.flagsubmissionbot.clients.Ructfe2009SubmitClient import Ructfe2009SubmitClient
from scorebot.attackengine.flagsubmissionbot.SubmitClient import SubmitClient

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

class FlagSubmissionBot(Process):

	def __init__(self,conf,init=False):
		Process.__init__(self)
		self.conf = conf
		self.comm = None
		self.init = init
		self.logger = conf.buildLogger("FlagSubmission")

		db_path = os.path.join(conf.log_dir,"flags.db")
		
		self.logger.error("Remember to change hard coded defcon client")
		self.client = Ructfe2009SubmitClient()
		self.submitter = FlagSubmitter(db_path,self.logger,self.client)

	def run(self):
		
		#Start Attack Manager
		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"FLAG_SUBMISSION_BOT")

		self.running = True

		self.comm.start()
		while(self.running):
			msg = self.comm.receive()
			if(msg.type == "COLLECTED_FLAGS"):
				self.__pwnFlags(msg.data)

			elif(msg.type == "GET_FLAG_STATS"):
				results = self.submitter.getFlagStats()
				self.comm.sendResponse(msg,BotMessage("GET_FLAG_STATS_RESULT",results))

			elif(msg.type == "MANUAL_FLAG"):
				result_msg = self.__pwnSingleFlag(msg.data)
				self.comm.sendResponse(msg,BotMessage("MANUAL_FLAG_RESULT",result_msg))

			else:
				self.logger.warn("Unknown message: %s %r",msg.type,msg.data)

	def terminate(self):
		server_info = self.conf.getGameStateServerInfo()
		comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"FLAG_SUBMISSION_BOT_KILL")

		comm.start()
		time.sleep(2)
		comm.kill()
		comm.join()
		Process.terminate(self)

	def __pwnFlags(self,flag_data):
		for teamId,exploit,flags in flag_data:
			self.logger.info("Received %d flags using %s from team %d" % (len(flags),exploit,teamId))
			for flag in flags:
				self.submitter.submit(flag,exploit,teamId)

	def __pwnSingleFlag(self,flag):
#		try:
			self.logger.debug("Pwn single flag: %s",flag)
			self.client.connect()
			resp = self.client.submit(flag)
			self.client.quit()

			if(resp == SubmitClient.VALID):
				return "Flag submitted and it was valid!."
			elif(resp == SubmitClient.INVALID):
				return "Flag submitted, but it was invalid :("
			else:
				return "It is suggested that this flag is retried (maybe a service is down?)"

#		except Exception as e:
#			self.logger.info("Error submitting single flag: %s" % e)
#			return "Error submitting flag: %s" % e
