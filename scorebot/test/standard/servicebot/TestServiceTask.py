import unittest
import time
import os
import pickle

from scorebot.standard.servicebot.ServiceTask import ServiceTask

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceTask(unittest.TestCase):

	def testCorrectScript(self):
		self.__ensureValidGoodService()
		path = os.path.join(modulePath(),'testservices','GoodService.py')
		good = ServiceTask(path,1,"NewFlag","0.0.0.0",None)
		good.start()
		
		self.assert_(good.status() == ServiceTask.OK)
		self.assert_(good.getPrevFlag() == "TestFlag")

	def testBrokenScript(self):
		path = os.path.join(modulePath(),'testservices','BrokenService.py')
		err = ServiceTask(path,2,"NewFlag","0.0.0.0",None)
		err.start()
		self.assert_(err.status() == ServiceTask.INVALID_FLAG)

	def testErrorScript(self):
		path = os.path.join(modulePath(),'testservices','ErrorService.py')
		err = ServiceTask(path,1,"NewFlag","0.0.0.0",None)
		err.start()
		self.assert_(err.status() == ServiceTask.ERROR)
		self.assert_(err.error() == "An Error")

	def testHangScript(self):
		path = os.path.join(modulePath(),'testservices','HangService.py')
		hang = ServiceTask(path,1,"NewFlag","0.0.0.0",None)
		hang.start()
		self.assert_(hang.status() == ServiceTask.KILLED)

	def testStoreScript(self):
		path = os.path.join(modulePath(),'testservices','StoreService.py')
		store = ServiceTask(path,0.5,"NewFlag","0.0.0.0",None)
		store.start()
		self.assert_(store.status() == ServiceTask.INVALID_FLAG)
		self.assert_(store.store() == "Store Text")
		
	def testPastTimeout(self):
		path = os.path.join(modulePath(),'testservices','GoodService.py')
		good = ServiceTask(path,1,"NewFlag","0.0.0.0",None)
		good.start()
		time.sleep(2)
		self.assert_(good.status() == ServiceTask.OK)

	def __ensureValidGoodService(self):
		path = modulePath()+"/testservices/GoodService.flag"
		pickle.dump("TestFlag",open(path,"w"))

def suite():
	tests = [
		'testCorrectScript',
		'testBrokenScript',
		'testErrorScript',
		'testHangScript',
		'testStoreScript',
		'testPastTimeout',
	]
	return unittest.TestSuite(map(TestServiceTask,tests))
