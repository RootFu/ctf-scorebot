import unittest
import multiprocessing
import time
import os

from scorebot.common.tasks.TaskRunner import TaskRunner

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestTaskRunner(unittest.TestCase):

	def testBasic(self):
		path = os.path.join(modulePath(),'testtasks','Succesful.py')
		runner = TaskRunner()
		runner.start()

		out_q = runner.taskStart([path,"Foo"])
		txt = out_q.get(True,1)
		self.assertEquals(txt,"FLAG: foobarbaz")
		self.assertEquals(len(out_q.get(True,1)),0)

		self.assertFalse(runner.taskAlive())
		self.assertEquals(0,runner.taskRetcode())
		runner.quit()

	def testRestart(self):
		path = os.path.join(modulePath(),'testtasks','Succesful.py')
		runner = TaskRunner()
		runner.start()

		out_q = runner.taskStart([path,"Foo"])
		txt = out_q.get(True,1)
		self.assertEquals(txt,"FLAG: foobarbaz")
		self.assertEquals(len(out_q.get(True,1)),0)
		
		out_q = runner.taskStart([path,"Foo"])
		txt = out_q.get(True,1)
		self.assertEquals(txt,"FLAG: foobarbaz")
		self.assertEquals(len(out_q.get(True,1)),0)

		self.assertFalse(runner.taskAlive())
		self.assertEquals(0,runner.taskRetcode())
		runner.quit()

	def testHang(self):
		path = os.path.join(modulePath(),'testtasks','Hang.py')
		runner = TaskRunner()
		runner.start()

		out_q = runner.taskStart([path,"Foo"])
		time.sleep(0.1)
		self.assertTrue(runner.taskAlive())
		runner.taskStop()
		self.assertFalse(runner.taskAlive())
		runner.quit()

	def testOverloadQue(self):
		path = os.path.join(modulePath(),'testtasks','FlagZ.py')
		runner = TaskRunner()
		runner.start()
		out_q = runner.taskStart([path,"Foo"])
		time.sleep(1)
		runner.quit()

		self.assertFalse(runner.taskAlive())
		self.assert_(out_q.qsize() > 1000)

	def testBroken(self):
		path = os.path.join(modulePath(),'testtasks','Broken.py')
		runner = TaskRunner()
		runner.start()
		out_q = runner.taskStart([path,"Foo"])
		time.sleep(0.2)
		self.assertEquals(len(out_q.get()),34)
		self.assertFalse(runner.taskAlive())
		runner.quit()	

	def testLinesThenHang(self):
		path = os.path.join(modulePath(),'testtasks','Hang2.py')
		runner = TaskRunner()
		runner.start()
		out_q = runner.taskStart([path,"Foo"])

		line1 = out_q.get()
		line2 = out_q.get()

		self.assertEquals("A"*1024,line1)
		self.assertEquals("B"*1024,line2)

		self.assertTrue(runner.taskAlive())
		runner.quit()
		self.assertFalse(runner.taskAlive())

	def testNewLineFront(self):
		path = os.path.join(modulePath(),'testtasks','SuccesfulNL.py')
		runner = TaskRunner()
		runner.start()

		out_q = runner.taskStart([path,"Foo"])
		txt = out_q.get(True,1)
		self.assertEquals(txt,"")
		txt = out_q.get(True,1)
		self.assertEquals(txt,"FLAG: foobarbaz")
		self.assertEquals(len(out_q.get(True,1)),0)

		self.assertFalse(runner.taskAlive())
		self.assertEquals(0,runner.taskRetcode())
		runner.quit()

	def testStress(self):
		path = os.path.join(modulePath(),'testtasks','Hang.py')
		runners = []
		for i in range(100):
			runner = TaskRunner()
			runner.start()
			runner.taskStart([path,"Foo"])
			runners.append(runner)

		for i in range(100):
			runners[i].quit()

		for i in range(100):
			self.assertFalse(runners[i].taskAlive())


def suite():
	tests = [
		'testBasic',
		'testRestart',
		'testHang',
		'testOverloadQue',
		'testBroken',
		'testLinesThenHang',
		'testNewLineFront',
		#'testStress',
	]
	return unittest.TestSuite(map(TestTaskRunner,tests))
