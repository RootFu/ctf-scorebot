import unittest
import time
import os

from scorebot.standard.servicebot2.ServiceTaskScheduler import ServiceTaskScheduler
from scorebot.standard.servicebot2.ServiceTask import ServiceTask
from scorebot.standard.servicebot2.ServiceBotConfig import ServiceBotConfig
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo
from scorebot.config.Config import Config

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceTaskScheduler(unittest.TestCase):

	def setUp(self):
		#Building a fake config
		timeout = 1
		self.conf = Config()
		self.conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		self.conf.addTeamInfo("Team2","127.0.1.1","127.0.1.0/24")

		self.servicebot_conf = ServiceBotConfig()
		self.servicebot_conf.min_duration_seconds = 5
		self.servicebot_conf.max_duration_seconds = 5

		self.servicebot_conf.addServiceInfo(
			"Service1",
			modulePath()+"/testservices/ErrorService.py",
			timeout,
			1,1)

		self.servicebot_conf.addServiceInfo(
			"Service2",
			modulePath()+"/testservices/ErrorService.py",
			timeout,
			1,1)
		
		self.servicebot_conf.addServiceInfo(
			"Service3",
			modulePath()+"/testservices/ErrorService.py",
			timeout,
			1,1)

		gamestate = GameStateServerInfo(
			"localhost",
			4242,
			"0123456789012345",
			"ABCDEFGH")

		self.conf.setGameStateServerInfo(gamestate)
		self.conf.addSection("SERVICE_BOT",self.servicebot_conf)

	def testSimpleSchedule(self):
		round = 0
		scheduler = ServiceTaskScheduler(self.conf,True)
		
		start = time.time()
		results = scheduler.execute(round)
		end = time.time()

		run_time = end - start
		self.assert_(4.0 < run_time and run_time < 6.0)

		for team,service,task in results:
			self.assertNotEqual(None,task.error())
			self.assertEquals(None,task.prevFlag())

		scheduler.quit()

	def testCookie(self):
		conf = Config()

		servicebot_conf = ServiceBotConfig()
		servicebot_conf.min_duration_seconds = 2
		servicebot_conf.max_duration_seconds = 2
		servicebot_conf.addServiceInfo(
			"Service",
			modulePath()+"/testservices/StoreService.py",
			1,
			1,1)

		conf.addSection("SERVICE_BOT",servicebot_conf)

		conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		
		gamestate = GameStateServerInfo(
			"localhost",
			4242,
			"0123456789012345",
			"ABCDEFGH")
		conf.setGameStateServerInfo(gamestate)

		scheduler = ServiceTaskScheduler(conf,True)
		scheduler.execute(0)
		results = scheduler.execute(1)

		for team,service,task in results:
			self.assertEquals(task.cookie(),"Worked")

		scheduler.quit()

def suite():
	tests = [
		'testSimpleSchedule',
		'testCookie',
	]
	return unittest.TestSuite(map(TestServiceTaskScheduler,tests))
