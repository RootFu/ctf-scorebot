import threading
import Queue
import time
import logging

from scorebot.standard.servicebot.ServiceTask import ServiceTask

class ServiceTaskCallback:

	def __init__(self,task_runner,teamId,serviceId):
		self.task_runner = task_runner
		self.teamId = teamId
		self.serviceId = serviceId

	def call(self):
		self.task_runner.onTaskComplete(self.teamId,self.serviceId)

class ServiceTaskRunner(threading.Thread):

	def __init__(self,conf=None):
		threading.Thread.__init__(self)
		self.in_q = Queue.Queue(5000)
		self.fin = False
		self.kill_on_empty = False
		self.task_counter = 0
		self.counter_lock = threading.Lock()

		self.conf = conf
		self.servicebot_conf = None
		self.logger = None

		if(conf != None):
			self.logger = logging.getLogger("ServiceBot")
			self.servicebot_conf = conf.getSection("SERVICE_BOT")

	def insert(self,task,teamId,serviceId):
		callback = ServiceTaskCallback(self,teamId,serviceId)
		task.setCallbackObj(callback)
		self.in_q.put((task,teamId,serviceId))

	def terminateOnEmpty(self):
		self.kill_on_empty = True

	def terminate(self):
		self.fin = True

	def run(self):
		while(True):

			if(self.fin == True):
				return

			if(self.kill_on_empty and self.in_q.empty()):
				return

			count = self.__getTasksCount()
			if(count < 100):
				try:
					task,teamId,serviceId = self.in_q.get(True,2)
					self.__incTasks()
					self.__logNewTask(teamId,serviceId)
					prev = threading.stack_size(262140)
					task.start()
					threading.stack_size(prev)
				except Queue.Empty as e:
					pass
			else:
				if(self.logger != None):
					self.logger.critical("Task runner created too many threads!")
				time.sleep(1)


	def onTaskComplete(self,teamId,serviceId):
		self.__logFinTask(teamId,serviceId)
		self.__decTasks()

	def __logNewTask(self,teamId,serviceId):
		if(self.logger != None and teamId != -1 and serviceId != -1):
			team = self.conf.getTeamInfoById(teamId)
			service = self.servicebot_conf.getServiceInfoById(serviceId)
			if(self.logger != None):
				self.logger.info("Starting task for team %s: %s" % (
					team.name,service.name))

	def __logFinTask(self,teamId,serviceId):
		if(self.logger != None and teamId != -1 and serviceId != -1):
			team = self.conf.getTeamInfoById(teamId)
			service = self.servicebot_conf.getServiceInfoById(serviceId)
			self.logger.info("Finished task for team %s: %s" % (team.name,service.name))
		
	def __getTasksCount(self):
		with self.counter_lock:
			return self.task_counter
		
	def __incTasks(self):
		with self.counter_lock:
			self.task_counter += 1

	def __decTasks(self):
		with self.counter_lock:
			self.task_counter -= 1
