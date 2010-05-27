import unittest
import time
import os

from scorebot.config.Config import Config
from scorebot.attackengine.attackbot.AttackManager import AttackManager
from scorebot.attackengine.attackbot.AttackConfig import AttackConfig

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestAttackManager(unittest.TestCase):


	def setUp(self):
		self.conf = Config()
	
		self.conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")	
		self.conf.addTeamInfo("Team2","127.0.1.1","127.0.1.0/24")

		atkcfg = AttackConfig(True)
		atkcfg.exploit_dir = os.path.join(modulePath(),"testexploits")
		atkcfg.exploit_timeout = 5
		atkcfg.round_interval = 5
		atkcfg.gather_interval = 1
		self.conf.addSection("ATTACK_BOT",atkcfg)

	def testUpdateExploits(self):
		manager = AttackManager(self.conf,None,True,False)
		manager.start()
		
		manager.cmd(AttackManager.UPDATE_EXPLOITS)
		exploit_set = manager.test(AttackManager.TEST_GET_EXPLOITS)

		self.assertTrue("Succesful.py" in exploit_set)
		self.assertTrue("Forever.py" in exploit_set)
		self.assertTrue("Timeout.py" in exploit_set)

	def testLaunchExploit(self):
		manager = AttackManager(self.conf,None,True,False)
		manager.start()
		
		manager.cmd(AttackManager.UPDATE_EXPLOITS)
		manager.cmd(AttackManager.LAUNCH_EXPLOIT,"Succesful.py")
		time.sleep(1)

		manager.cmd(AttackManager.PROCESS_OUTPUT)
		time.sleep(1)
		manager.cmd(AttackManager.GATHER_FLAGS)
		time.sleep(1)
		results = manager.getFlags()
		
		self.assertEquals(len(results),2)

		r1 = results[0]
		r2 = results[1]
		
		self.assertEquals(r1[0],0)
		self.assertEquals(r2[0],1)
		self.assertEquals(r1[2],['foobarbaz'])
		self.assertEquals(r2[2],['foobarbaz'])
	
def suite():
	tests = [
		'testUpdateExploits',
		'testLaunchExploit',
	#	'testKillExploit',
	]
	return unittest.TestSuite(map(TestAttackManager,tests))
