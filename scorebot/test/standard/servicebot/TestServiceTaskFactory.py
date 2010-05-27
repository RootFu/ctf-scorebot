import unittest
import time
import os
import pickle

from scorebot.standard.servicebot.ServiceTask import ServiceTask
from scorebot.standard.servicebot.ServiceTaskFactory import ServiceTaskFactory
from scorebot.standard.servicebot.ServiceBotConfig import ServiceBotConfig
from scorebot.config.Config import Config
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceTaskFactory(unittest.TestCase):

	def setUp(self):
		#Building a fake config
		timeout = 1
		self.conf = Config()
		self.conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		self.conf.addTeamInfo("Team2","127.0.1.1","127.0.1.0/24")
	
		self.servicebot_conf = ServiceBotConfig()
	
		self.servicebot_conf.addServiceInfo(
			"Service1",
			modulePath()+"/testservices/GoodService.py",
			timeout,
			1,1)

		self.servicebot_conf.addServiceInfo(
			"Service2",
			modulePath()+"/testservices/StoreService.py",
			timeout,
			1,1)

		gamestate = GameStateServerInfo(
			"localhost",
			4242,
			"0123456789012345",
			"ABCDEFGH")

		self.conf.setGameStateServerInfo(gamestate)
		self.conf.addSection("SERVICE_BOT",self.servicebot_conf)

	def testBuildSimple(self):
		factory = ServiceTaskFactory(self.conf,True)
		task = factory.build(0,0,0)
		task.start()
		self.assert_(task.status() == ServiceTask.OK)

	def testStorePersistance(self):
		factory = ServiceTaskFactory(self.conf,True)
		
		tasks = [
			factory.build(0,1,0),
			factory.build(1,1,0),
		]

		for task in tasks:
			task.start()
		
		factory.update(tasks[0],0,1,1)
		factory.update(tasks[1],1,1,1)

		task = factory.build(1,1,0)
		task.start()
		self.assert_(task.store() == "Worked")

	def testSave(self):
		factory = ServiceTaskFactory(self.conf,True)
		
		tasks = [
			factory.build(0,1,1),
			factory.build(1,1,1),
		]

		for task in tasks:
			task.start()

		factory.update(tasks[0],0,1,0)
		factory.update(tasks[1],1,1,0)

		#Test a "crash recovery" by building a new factory
		factory.save()
		new_factory = ServiceTaskFactory(self.conf,False)
		
		task = new_factory.build(1,1,0)
		task.start()
		self.assert_(task.store() == "Worked")
	
	def testFlagUpdate(self):	
		factory = ServiceTaskFactory(self.conf,True)

		#Simulate the service being down - prev flag should be invalid
		task = factory.build(0,0,6)
		task.start()
		self.assert_(task.status() == ServiceTask.OK)
		factory.update(task,0,0,6)	
		self.assert_(task.status() == ServiceTask.INVALID_FLAG)

		#Simulate a round passing - prev flag should be valid	
		task = factory.build(0,0,7)
		task.start()
		factory.update(task,0,0,7)	
		self.assert_(task.status() == ServiceTask.OK)
	
	def testUpdateRoundOne(self):
		factory = ServiceTaskFactory(self.conf,True)

		#Clear prev flag
		task = factory.build(0,0,42)
		task.start()

		#Round 1 should be ok, even if the prev_flag is invalid		
		task = factory.build(0,0,1)
		task.start()
		self.assertEquals(task.status(),ServiceTask.OK)
		factory.update(task,0,0,1)	
		self.assertEquals(task.status(),ServiceTask.OK)

	def testStress(self):
		self.conf = Config()
		
		for i in range(0,1000):
			self.conf.addTeamInfo("Team","127.0.0.1","127.0.0.0/24")
			self.conf.addServiceInfo(
				"Service",
				modulePath()+"/testservices/GoodService.py",
				1,
				1,1)
		
		factory1 = ServiceTaskFactory(self.conf,True)
		factory2 = ServiceTaskFactory(self.conf,False)

def suite():
	tests = [
		'testBuildSimple',
		'testStorePersistance',
		'testSave',
		'testFlagUpdate',
		'testUpdateRoundOne',
		#'testStress',
	]
	return unittest.TestSuite(map(TestServiceTaskFactory,tests))
