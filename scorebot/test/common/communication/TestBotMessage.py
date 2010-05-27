import unittest
import threading
import time

from scorebot.common.communication.BotMessage import toTxt, fromTxt, MsgSequenceError

class TestBotMessage(unittest.TestCase):

	result_txt = "tnwBZldq/SpWsPIcSLUi/LjIQvrCGj+43iJwkhyfUcVh8g=="
	key = "0123456789012345"
	iv = "ABCDEFGH"
	seq = 0

	def testSimpleEncryptMessage(self):
		obj = ["foo","bar"]
		self.assert_(TestBotMessage.result_txt == toTxt(self.key,self.iv,self.seq,obj))	

	def testSimpleDecryptMessage(self):
		obj = fromTxt(self.key,self.iv,self.seq,self.result_txt)
		self.assert_(obj[0] == "foo")
		self.assert_(obj[1] == "bar")
		

	def testLongMessage(self):
		obj = [range(0,1000)]*1000
		txt = toTxt(self.key,self.iv,self.seq,obj)
		test = fromTxt(self.key,self.iv,self.seq,txt)
		map(self.assertEquals,test,[range(1000)]*1000)

	def testInvalidToken(self):
		obj = ["foo","bar"]
		msg = toTxt(self.key,self.iv,self.seq,obj)
		self.assertRaises(MsgSequenceError,fromTxt,self.key,self.iv,1,self.result_txt)

def suite():
	tests = [
		'testSimpleEncryptMessage',
		'testSimpleDecryptMessage',
		'testLongMessage',
		'testInvalidToken',
	]
	return unittest.TestSuite(map(TestBotMessage,tests))

if __name__ == '__main__':
	unittest.main()
