
import os
import time
import cPickle

from scorebot.config.Config import Config
from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.common.models.TeamInfo import TeamInfo
from scorebot.standard.servicebot.ServiceTask import ServiceTask
from scorebot.common.models.Flag import Flag,FlagManager

def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class ServiceTaskFactory:

	def __init__(self,conf,init=False):
		self.conf = conf
		self.servicebot_conf = conf.getSection("SERVICE_BOT")
		self.storage = None
		self.flag_manager = conf.buildFlagManager()
		self.service_loggers = {}

		for service in self.servicebot_conf.services:
			self.service_loggers[service.name] = conf.buildLogger("Service-%s"%service.name)

		if(init):
			self.__createStorage()
		else:
			self.__load()

	def build(self,teamId,serviceId,round):
		team = self.conf.getTeamInfoById(teamId)
		service = self.servicebot_conf.getServiceInfoById(serviceId)
		flag = Flag(teamId,serviceId,round,time.time())

		task = ServiceTask(
				service.script,
				service.timeout,
				self.flag_manager.toTxt(flag),
				team.host,
				self.storage[teamId][serviceId],
				self.service_loggers[service.name])

		return task

	def update(self,task,teamId,serviceId,round):
		self.storage[teamId][serviceId] = task.store()

		if(round == 1 or task.status() != ServiceTask.OK):
			return

		try:
			prev_flag = self.flag_manager.toFlag(task.getPrevFlag())
			if(prev_flag.teamId != teamId or 
			   prev_flag.serviceId != serviceId or
		 	   prev_flag.round+1 != round):
				task.setInvalidFlag()
		except:
				task.setInvalidFlag()

	
	def save(self):	
		file = os.path.join(modulePath(),"ServiceTaskFactory.dat")
		cPickle.dump(self.storage,open(file,'wb'),cPickle.HIGHEST_PROTOCOL)

	def __load(self):
		file = os.path.join(modulePath(),"ServiceTaskFactory.dat")
		self.storage =  cPickle.load(open(file,'rb'))
		
		assert(len(self.storage) == self.conf.numTeams()),"Number of teams did not match"
		assert(len(self.storage[0]) == self.servicebot_conf.numServices()),"Number of services did not match"

	def __createStorage(self):
		assert(False),"The line below is incorrect"
		self.storage = [[None]*self.servicebot_conf.numServices()]*self.conf.numTeams()
		self.save()
