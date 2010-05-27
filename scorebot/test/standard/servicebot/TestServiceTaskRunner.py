import unittest
import time
import os

from scorebot.standard.servicebot.ServiceTaskRunner import ServiceTaskRunner
from scorebot.standard.servicebot.ServiceTask import ServiceTask

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceTaskRunner(unittest.TestCase):

	def testSimpleInsert(self):
		test = ServiceTaskRunner()
		test.start()

		script = modulePath()+"/testservices/HangService.py"
		task = ServiceTask(script,2,"Flag","10.0.0.1",None)
		test.insert(task,-1,-1)

		test.terminateOnEmpty()
		self.assert_(task.status() == ServiceTask.KILLED)

	def testErrorInsert(self):
		test = ServiceTaskRunner()
		test.start()

		script = modulePath()+"/testservices/ErrorService.py"

		tasks = []
		for i in range(0,10):
			task = ServiceTask(script,1,"Flag","10.0.0.1",None)
			tasks.append(task)
			test.insert(task,-1,-1)
		test.terminateOnEmpty()

		for task in tasks:
			self.assert_(task.status() == ServiceTask.ERROR)

	def testStress(self):
		test = ServiceTaskRunner()
		test.start()
		
		script = modulePath()+"/testservices/HangService.py"
		task = None
		for i in range(0,1000):
			task = ServiceTask(script,2,"Flag","10.0.0.1",None)
			test.insert(task,-1,-1)

		test.terminateOnEmpty()
		self.assert_(task.status() == ServiceTask.KILLED)
		

def suite():
	tests = [
		'testSimpleInsert',
		'testErrorInsert',
	]
	return unittest.TestSuite(map(TestServiceTaskRunner,tests))

def stressSuite():
	tests = [
		'testStress',
	]
	return unittest.TestSuite(map(TestServiceTaskRunner,tests))
