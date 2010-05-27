import unittest
import time

from scorebot.common.models.Flag import FlagManager, Flag, FlagParseException

class TestFlag(unittest.TestCase):

	flag_txt = "FLGtnwBZi_2lkrcnZbIQNDsg_eC9LGcLAUdRi6lbn85Js1pD7fe"
	key = "0123456789012345"
	iv = "ABCDEFGH"

	def testFlagToTxt(self):
		fm = FlagManager(self.key,self.iv,"Foo")
		flag = Flag(0,0,0,1234567890.0)
		self.assert_(fm.toTxt(flag) == self.flag_txt)

	def testTxtToFlag(self):
		fm = FlagManager(self.key,self.iv,"Foo")
		flag = fm.toFlag(self.flag_txt)
		self.assert_(flag.teamId == 0)
		self.assert_(flag.serviceId == 0)
		self.assert_(flag.round == 0)
		self.assert_(flag.timestamp == 1234567890.0)

	def testTxtToFlagWS(self):
		fm = FlagManager(self.key,self.iv,"Foo")
		flag = fm.toFlag("  "+self.flag_txt+"  \t\n")
		self.assert_(flag.teamId == 0)
		self.assert_(flag.serviceId == 0)
		self.assert_(flag.round == 0)
		self.assert_(flag.timestamp == 1234567890.0)


	def testIncorrectPadding(self):
		fm = FlagManager(self.key,self.iv,"Foo")
		self.assertRaises(FlagParseException,fm.toFlag,"FLGtnwBZi_2lkrcnZbIQNDsg_eC9_LGcLAUdRi6lbn85Js1pD7fe")

def suite():
	tests = [
		'testFlagToTxt',
		'testTxtToFlag',
		'testTxtToFlagWS',
		'testIncorrectPadding',
	]
	return unittest.TestSuite(map(TestFlag,tests))

if __name__ == '__main__':
	unittest.main()
