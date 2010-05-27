import unittest
import os
import subprocess
import time
import threading 
import asyncore

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotCommServer import BotCommServer
from scorebot.common.communication.BotMessage import BotMessage

#Useful function for using relative paths
def modulePath():
	return os.path.dirname(os.path.realpath( __file__ ))

class TestBotCommClient(unittest.TestCase):

	key = "0123456789012345"
	iv = "ABCDEFGH"

	def testEcho(self):
		msg = BotMessage("norm",["Foo","Bar"])
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()
		comm.send(msg)
		rcv = comm.receive(True,5)
		comm.kill()
		
		self.assert_(rcv.type == "norm")
		self.assert_(rcv.data == ["Foo","Bar"])
		
	def testTypes(self):
		msg = BotMessage("rev",["Foo","Bar"])
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()
		comm.send(msg)
		rcv = comm.receive(True,5)
		comm.kill()
		self.assert_(rcv.type == "rev")
		self.assert_(rcv.data == ["Bar","Foo"])

	def testMultiMessage(self):
		m1 = BotMessage("norm",["Foo","Bar"])
		m2 = BotMessage("rev",["Foo","Foo"])
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()
		comm.send(m1)
		comm.send(m2)
		r1 = comm.receive(True,1)
		r2 = comm.receive(True,1)
		comm.kill()

		self.assert_(r1.data == ["Foo","Bar"])
		self.assert_(r2.data == ["Foo","Foo"])

	def testManyMessage(self):
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()
		for i in range(0,100):
			msg = BotMessage("norm",["Test_%d" % i])
			comm.send(msg)
		for i in range(0,100):
			rcv = comm.receive(True,1)
			self.assert_(rcv.data == ["Test_%d" % i])
		comm.kill()
			

	def testMultipleClients(self):
		echo = BotCommClient("",424242,self.key,self.iv,"ECHO")
		foo = BotCommClient("",424242,self.key,self.iv,"FOO")
		echo.start()
		foo.start()

		m1 = BotMessage("norm",["Foo","Bar"])
		m2 = BotMessage("foo","A foo")

		echo.send(m1)
		foo.send(m2)

		r1 = echo.receive(True,1)
		foo.kill()
		echo.kill()

	def testServerStatePassing(self):
		foo = BotCommClient("",424242,self.key,self.iv,"FOO")
		bar = BotCommClient("",424242,self.key,self.iv,"BAR")
		echo = BotCommClient("",424242,self.key,self.iv,"ECHO")

		foo.start()
		bar.start()
		echo.start()

		m1 = BotMessage("foo","A foo message")
		m2 = BotMessage("norm",["Foo","Bar"])

		for i in range(3):
			foo.send(m1)

		echo.send(m2)
		r1 = echo.receive(True,1)
		r2 = bar.receive(True,1)
		self.assert_(r1.data == ["Foo","Bar"])
		self.assert_(r2.data == "Got Foo?")

		foo.kill()
		bar.kill()
		echo.kill()

	def testBasicCommRequest(self):
		req = BotMessage("req1",["Foo","Bar"],True)
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()
		rcv = comm.request(req,"req_result1",1.0)
		comm.kill()
		
		self.assert_(rcv.type == "req_result1")
		self.assert_(rcv.data == ["Foo","Bar"])

	def testCommRequestExtraMessage(self):
		req = BotMessage("req2",["Foo","Bar"],True)
		comm = BotCommClient("",424242,self.key,self.iv,"ECHO")
		comm.start()

		for i in range(0,50):
			msg = BotMessage("norm",["Test_%d" % i])
			comm.send(msg)
		
		for i in xrange(5):
			rcv = comm.request(req,"req_result2",1.0)
			self.assertEquals(rcv.type,"req_result2")
			self.assertEquals(rcv.data,["Foo","Bar"])

		for i in range(0,50):
			rcv = comm.receive(True,1)
			self.assert_(rcv.data == ["Test_%d" % i])

		for i in xrange(5):
			xtra = comm.receive(True,1)
			self.assert_(xtra != None)
			self.assertEquals(xtra.data,i+1)
		
		comm.kill()
		
def suite():
	tests = [
		'testEcho',
		'testTypes',
		'testMultiMessage',
		'testManyMessage',
		'testMultipleClients',
		'testServerStatePassing',
		'testBasicCommRequest',
		'testCommRequestExtraMessage',
	]
	return unittest.TestSuite(map(TestBotCommClient,tests))

if __name__ == '__main__':
	unittest.main()
