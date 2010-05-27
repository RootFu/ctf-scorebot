import os
import heapq
import random
import time

from scorebot.config.Config import Config
from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.common.models.TeamInfo import TeamInfo

from scorebot.standard.servicebot.ServiceTask import ServiceTask
from scorebot.standard.servicebot.ServiceTaskFactory import ServiceTaskFactory
from scorebot.standard.servicebot.ServiceTaskRunner import ServiceTaskRunner

class ServiceTaskScheduler:

	def __init__(self,conf,init=False):
		self.conf = conf
		self.servicebot_conf = self.conf.getSection("SERVICE_BOT")
		self.factory = ServiceTaskFactory(conf,init)
		self.runner = ServiceTaskRunner(conf)
		self.runner.start()

	def execute(self,round):
		tasks = []	
		heap = []

		for teamId in range(0,self.conf.numTeams()):
			tasks.append([])
			for serviceId in range(0,self.servicebot_conf.numServices()):
				task = self.factory.build(teamId,serviceId,round)
				tasks[teamId].append(task)

		round_length = random.randint(
			self.servicebot_conf.getRoundLengthMin(),
			self.servicebot_conf.getRoundLengthMax())

		for teamId in range(0,self.conf.numTeams()):
			for serviceId in range(0,self.servicebot_conf.numServices()):
				timeout = self.servicebot_conf.getServiceInfoById(serviceId).timeout
				wait_max = round_length - timeout
				wait = random.randint(0,wait_max)
				heapq.heappush(heap,(wait,tasks[teamId][serviceId],teamId,serviceId))

		total = 0
		while(len(heap) > 0):
			wait,task,teamId,serviceId = heapq.heappop(heap)
			if(total == wait):
				self.runner.insert(task,teamId,serviceId)
			else:
				time.sleep(wait-total)
				total = wait
				self.runner.insert(task,teamId,serviceId)
				
		time.sleep(round_length - (total+1))
		
		for teamId in range(0,self.conf.numTeams()):
			for serviceId in range(0,self.servicebot_conf.numServices()):
				task = tasks[teamId][serviceId]
				self.factory.update(task,teamId,serviceId,round)
	
		return tasks

	def terminateAtRoundEnd(self):
		self.runner.terminateOnEmpty()

	def terminate(self):
		self.runner.terminate()
