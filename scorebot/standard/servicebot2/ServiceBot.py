import logging

from multiprocessing import Process

from scorebot.standard.servicebot2.ServiceTaskScheduler import ServiceTaskScheduler
from scorebot.standard.servicebot2.ServiceTask import ServiceTask
from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

class ServiceBot(Process):

	def __init__(self,conf,init=False):
		Process.__init__(self)
		self.conf = conf
		self.servicebot_conf = conf.getSection("SERVICE_BOT")

		self.comm = None
		self.init = init
		self.logger = conf.buildLogger("ServiceBot")

		self.scheduler = None

	def run(self):
		self.scheduler = ServiceTaskScheduler(self.conf,self.init)
		try:
			self.logger.info("=== Starting ===")
			server_info = self.conf.getGameStateServerInfo()
			self.comm = BotCommClient(
				server_info.host,
				server_info.port,
				server_info.key,
				server_info.iv,
				"SERVICE_BOT")
		

			self.comm.start()
			running = True

			while(running):
				msg = self.comm.receive()
				self.logger.debug("recvd msg: %s (%r)" % (msg.type,str(msg.data)))

				if(msg.type == "EXECUTE_ROUND"):
					round = msg.data
					self.logger.info("=== Service Round(%d) Starting ===" % round)
					results = self.scheduler.execute(round)
					result_msg = self.__parseResults(round,results)
					self.comm.send(result_msg)
					self.logger.debug("Results: %r" % str(result_msg.data))
					self.logger.info("=== Service Round(%d) Ending ===" % round)

				elif(msg.type == "TERMINATE"):
					self.logger.info("Received TERM message from gameserver")
					running = False

				else:
					self.logger.error("Unknown message: %s %s" % (msg.type,str(msg.data)))
					assert(False)

		except KeyboardInterrupt:
			self.logger.warn("Servicebot caught Keyboard Interrupt!")

		finally:
			#cleanup
			self.logger.info("Terminating...")
			print "WTF",self.scheduler
			self.scheduler.quit()
			self.comm.kill()
			self.logger.info("Terminated...")
	
	
	def __parseResults(self,round,task_results):
		results = []

		for teamId in xrange(self.conf.numTeams()):
			results.append([])
			for serviceId in xrange(self.servicebot_conf.numServices()):
				results[teamId].append(None)

		for team,service,task in task_results:
			if(task.gotExpectedFlag()):
				results[team.id][service.id] = 'g'
		
			elif(task.error() == None and task.retcode() == 0):
				results[team.id][service.id] = 'b'
					
			else:
				results[team.id][service.id] = 'e'

		for teamId in xrange(self.conf.numTeams()):
			for serviceId in xrange(self.servicebot_conf.numServices()):
				assert(results[teamId][serviceId] != None)

		return BotMessage("SERVICE_RESULTS",(round,results))
