import os
import heapq
import random
import time

from scorebot.config.Config import Config
from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.common.models.TeamInfo import TeamInfo
from scorebot.common.models.Flag import Flag,FlagManager

from scorebot.standard.servicebot2.ServiceTask import ServiceTask

class ServiceTaskScheduler:

	def __init__(self,conf,init=False):
		self.conf = conf
		self.servicebot_conf = self.conf.getSection("SERVICE_BOT")
		self.flag_manager = self.conf.buildFlagManager()

		self.tasks = []
	
		for service in self.servicebot_conf.services:
			logger = conf.buildLogger("Service_%s" % service.name)
			for team in self.conf.teams:
				self.tasks.append((team,service,ServiceTask(service.script,team,logger)))

	def quit(self):
		for team,service,task in self.tasks:
			task.quit()

	def execute(self,round):
	
		heap = []
	
		round_length = random.randint(
			self.servicebot_conf.getRoundLengthMin(),
			self.servicebot_conf.getRoundLengthMax())

		for team,service,task in self.tasks:
			wait_max = round_length - service.timeout
			wait = random.randint(0,wait_max)
			flag = Flag(team.id,service.id,round,time.time()+float(wait))
			heapq.heappush(heap,(wait,task,self.flag_manager.toTxt(flag)))
		
		total = 0
		while(len(heap) > 0):
			wait,task,flag = heapq.heappop(heap)
			if(total == wait):
				task.launch(flag)
			else:
				time.sleep(wait-total)
				total = wait
				task.launch(flag)
				
		time.sleep(round_length - total)
		
		for team,service,task in self.tasks:
			task.finish()
			task.processOutput()

		return self.tasks
"""
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
"""
