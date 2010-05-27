import unittest
import os

from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser

#Useful function for using relative paths
def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class TestConfig(unittest.TestCase):

	def testGetTeams(self):
		test_path = os.path.join(modulePath(),"testini","test_config.ini")
		cip = ConfigIniParser(debug=True)
		conf = cip.load(test_path)
		team1 = conf.getTeamInfoById(0)
		team2 = conf.getTeamInfoById(1)
		
		#Order is not preserved
		self.assert_(team1.name == "Team1" or team1.name == "Team2")
		self.assert_(team2.name == "Team1" or team2.name == "Team2")

	def testValidConfig(self):
		test_path = os.path.join(modulePath(),"testini","test_config.ini")
		conf = ConfigIniParser(debug=True).load(test_path)
		self.assert_(conf.isValid())

	def testMissingSection(self):
		test_path = os.path.join(modulePath(),"testini","no_logging.ini")
		cip = ConfigIniParser(debug=True)
		try:
			cip.load(test_path)
			self.assert_(False,"ConfigParser should have thown exit execption")
		except SystemExit as e:
			self.assertEquals(type(e), type(SystemExit()))

def suite():
	tests = [
		'testGetTeams',
		'testValidConfig',
		'testMissingSection',
	]
	return unittest.TestSuite(map(TestConfig,tests))
