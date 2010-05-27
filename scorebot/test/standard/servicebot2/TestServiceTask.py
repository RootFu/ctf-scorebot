import unittest
import time
import os
import pickle

from scorebot.standard.servicebot2.ServiceTask import ServiceTask
from scorebot.common.models.TeamInfo import TeamInfo

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestServiceTask(unittest.TestCase):

	def setUp(self):
		self.team1 = TeamInfo(0,"Test","127.0.0.0","127.0.0.0/24")

	def testCorrectScript(self):
		self.__ensureValidGoodService()
		path = os.path.join(modulePath(),'testservices','GoodService.py')
		good = ServiceTask(path,self.team1)

		good.launch("NewFlag")
		time.sleep(0.1)
		good.finish()
		good.processOutput()
		good.quit()

		self.assertEquals(good.prevFlag(),"TestFlag")

	def testBrokenScript(self):
		path = os.path.join(modulePath(),'testservices','BrokenService.py')
		broken = ServiceTask(path,self.team1)
		broken.launch("NewFlag")
		time.sleep(0.1)
		broken.finish()
		broken.processOutput()
		broken.quit()

		self.assertEquals(broken.prevFlag(),None)

	def testErrorScript(self):
		path = os.path.join(modulePath(),'testservices','ErrorService.py')
		err = ServiceTask(path,self.team1)
		err.launch("NewFlag")
		time.sleep(0.1)
		err.finish()
		err.processOutput()
		err.quit()

		self.assertEquals(err.error(),"An Error")

	def testHangScript(self):
		path = os.path.join(modulePath(),'testservices','HangService.py')
		hang = ServiceTask(path,self.team1)
		hang.launch("NewFlag")
		time.sleep(0.1)

		self.assertEquals(hang.isAlive(),True)
		hang.finish()
		self.assertEquals(hang.isAlive(),False)
		hang.quit()

	def testCookieScript(self):
		path = os.path.join(modulePath(),'testservices','StoreService.py')
		store = ServiceTask(path,self.team1)
		store.launch("NewFlag")
		time.sleep(0.1)
		store.finish()
		store.processOutput()
		store.quit()
		#self.assertEquals(store.status() == ServiceTask.INVALID_FLAG)
		self.assertEquals(store.cookie(),"Store Text")
		
	def __ensureValidGoodService(self):
		path = modulePath()+"/testservices/GoodService.flag"
		pickle.dump("TestFlag",open(path,"w"))

def suite():
	tests = [
		'testCorrectScript',
		'testBrokenScript',
		'testErrorScript',
		'testHangScript',
		'testCookieScript',
	]
	return unittest.TestSuite(map(TestServiceTask,tests))
