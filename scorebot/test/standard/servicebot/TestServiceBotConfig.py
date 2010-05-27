import unittest
import os

from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser
from scorebot.standard.servicebot.ServiceBotConfig import ServiceBotConfigHandler
from scorebot.standard.servicebot.ServiceBotConfig import ServiceConfigHandler
from scorebot.standard.servicebot.ServiceBotConfig import ServiceBotConfig

#Useful function for using relative paths
def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceBotConfig(unittest.TestCase):
	
	def setUp(self):
		self.cip = ConfigIniParser(debug=True)
		self.cip.addHandler(ServiceBotConfigHandler())
		self.cip.addHandler(ServiceConfigHandler())

	def testValid(self):
		test_path = os.path.join(modulePath(),"testini","test_service.ini")
		conf = self.cip.load(test_path)
		servicebot_conf = conf.getSection("SERVICE_BOT")
		self.assert_(servicebot_conf.isValid())
	
	def testGetServices(self):
		test_path = os.path.join(modulePath(),"testini","test_service.ini")
		conf = self.cip.load(test_path)
		servicebot_conf = conf.getSection("SERVICE_BOT")

		service1 = servicebot_conf.getServiceInfoById(0)
		service2 = servicebot_conf.getServiceInfoById(1)
	
		#Order is not preserved
		self.assert_(service1.name == "Service1" or service1.name == "Service2")
		self.assert_(service2.name == "Service1" or service2.name == "Service2")
		self.assert_(service1.timeout == 30)
		self.assert_(service1.defscore == 1)
		self.assert_(service1.offscore == 1)

	def testGetRoundInfo(self):
		test_path = os.path.join(modulePath(),"testini","test_service.ini")
		conf = self.cip.load(test_path)
		servicebot_conf = conf.getSection("SERVICE_BOT")
		
		self.assertEquals(servicebot_conf.getRoundLengthMin(),0.5*60.0)
		self.assertEquals(servicebot_conf.getRoundLengthMax(),2*60.0)

	def testValidServiceScripts(self):
		test_path = os.path.join(modulePath(),"testini","test_service.ini")
		cip = ConfigIniParser()
		cip.addHandler(ServiceBotConfigHandler())
		cip.addHandler(ServiceConfigHandler())
		try:
			conf = cip.load(test_path)
			self.assert_(False,"ConfigParser should have thown exit execption")
		except SystemExit as e:
			self.assertEquals(type(e), type(SystemExit()))

	def testFlagConfig(self):
		self.fail("TODO")
		"""
		test_path = os.path.join(modulePath(),"testini","test_config.ini")
		conf = ConfigIniParser(debug=True).load(test_path)
		self.assert_(conf.getFlagDuration() == 5*60)
		self.assert_(conf.getFlagPhrase() == "SomeWordsHere")
		"""
def suite():
	tests = [
		'testValid',
		'testGetServices',
		'testGetRoundInfo',
		'testValidServiceScripts',
	]
	return unittest.TestSuite(map(TestServiceBotConfig,tests))
