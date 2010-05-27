import unittest
import time

from scorebot.config.Config import Config
from scorebot.common.models.Flag import FlagManager, Flag
from scorebot.standard.submitbot.FlagValidator import FlagValidator

class TestFlagValidator(unittest.TestCase):

	def setUp(self):
		self.conf = Config()
		self.conf.setFlagDuration(60)
		self.conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		self.conf.addTeamInfo("Team2","127.0.1.1","127.0.1.0/24")

	def testEnsureDifferentTeams(self):
		fv = FlagValidator(self.conf.numTeams(),self.conf.getFlagDuration())
		flag = Flag(0,0,0,time.time())
		self.assert_(fv.validate(0,flag) == FlagValidator.SAME_TEAM)
		self.assert_(fv.validate(1,flag) == FlagValidator.VALID)

	def testEnsureDuration(self):
		fv = FlagValidator(self.conf.numTeams(),self.conf.getFlagDuration())
		flagExpired = Flag(0,0,0,time.time()-61)
		flagOk = Flag(0,0,0,time.time()-59)
		self.assert_(fv.validate(1,flagOk) == FlagValidator.VALID)
		self.assert_(fv.validate(1,flagExpired) == FlagValidator.EXPIRED)

	def testEnsureUnique(self):
		fv = FlagValidator(self.conf.numTeams(),self.conf.getFlagDuration())
		flag = Flag(0,0,0,time.time())
		self.assert_(fv.validate(1,flag) == FlagValidator.VALID)
		self.assert_(fv.validate(1,flag) == FlagValidator.REPEAT)

	def testEnsureUniqueBug(self):
		fv = FlagValidator(self.conf.numTeams(),self.conf.getFlagDuration())
		flag = Flag(0,0,0,time.time())
		self.assert_(fv.validate(1,flag) == FlagValidator.VALID)
		for i in xrange(100):
			self.assert_(fv.validate(1,flag) == FlagValidator.REPEAT)

	def testLargeRecord(self):
		fv = FlagValidator(self.conf.numTeams(),self.conf.getFlagDuration())
		
		for i in xrange(1000):
			flag = Flag(0,i,0,time.time())
			self.assert_(fv.validate(1,flag) == FlagValidator.VALID)
		flag = Flag(0,500,0,time.time())
		self.assert_(fv.validate(1,flag) == FlagValidator.REPEAT)

def suite():
	tests = [
		'testEnsureDifferentTeams',
		'testEnsureDuration',
		'testEnsureUnique',
		'testEnsureUniqueBug',
		'testLargeRecord',
	]
	return unittest.TestSuite(map(TestFlagValidator,tests))

if __name__ == '__main__':
	unittest.main()
