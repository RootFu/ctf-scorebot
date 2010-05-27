import unittest
import multiprocessing
import time
import os

from scorebot.attackengine.attackbot.AttackTask import AttackTask

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class TestAttackTask(unittest.TestCase):

	def testBasicAttack(self):
		path = os.path.join(modulePath(),'testexploits','Succesful.py')
		attack = AttackTask(path,"127.0.0.1",2,None)
		attack.launch()
		time.sleep(0.1)
		attack.processOutput()
		flags = attack.collectFlags()
		self.assertEquals(flags,["foobarbaz"])
		attack.quit()

	def testRestartAttack(self):
		path = os.path.join(modulePath(),'testexploits','Succesful.py')
		attack = AttackTask(path,"127.0.0.1",2,None)
	
		for i in range(5):	
			attack.launch()
			time.sleep(0.1)
			self.assertFalse(attack.isAlive())
		
		attack.processOutput()
		flags = attack.collectFlags()
		self.assertEquals(flags,["foobarbaz"]*5)
		attack.quit()
	
	def testCookieAttack(self):
		path = os.path.join(modulePath(),'testexploits','Cookie.py')
		attack = AttackTask(path,"127.0.0.1",2,None)
	
		for i in range(5):	
			attack.launch()
			time.sleep(0.1)
			self.assertFalse(attack.isAlive())
			attack.processOutput()
		
		flags = attack.collectFlags()
		for i in range(len(flags)):
			self.assertEquals(flags[i],"COOKIEFLAG%d"%i)

		attack.quit()
	
	def testExpireTimeout(self):
		path = os.path.join(modulePath(),'testexploits','Timeout.py')
		attack = AttackTask(path,"127.0.0.1",1,None)
		attack.launch()
		time.sleep(1.5)
		self.assertFalse(attack.isAlive())
		attack.quit()

	def testTimeoutAttack(self):
		path = os.path.join(modulePath(),'testexploits','Timeout.py')
		attack = AttackTask(path,"127.0.0.1",5,None)
		attack.launch()
		time.sleep(0.5)
		attack.processOutput()
		count = 0
		while(attack.isAlive()):
			time.sleep(1)
			count += 1
			self.assertTrue(count < 5)

		attack.quit()

	def testInfiniteAttack(self):
		path = os.path.join(modulePath(),'testexploits','Infinite.py')
		attack = AttackTask(path,"127.0.0.1",1,None)
		attack.launch()
		time.sleep(0.5)
		attack.processOutput()
		time.sleep(2)
		self.assertTrue(attack.isAlive())
		attack.quit()
	
	def testMissingExploit(self):
		self.fail("TODO")

	def testStop(self):
		path = os.path.join(modulePath(),'testexploits','Forever.py')
		attack = AttackTask(path,"127.0.0.1",10,None)
		attack.launch()
		time.sleep(0.3)
		self.assertTrue(attack.isAlive())
		attack.stop()
		time.sleep(0.3)
		self.assertFalse(attack.isAlive())
		attack.quit()

	def testStress(self):
		path = os.path.join(modulePath(),'testexploits','Forever.py')
	
		attacks = []
		for i in xrange(500):
			attacks.append(AttackTask(path,"127.0.0.1",10,None))
			attacks[i].launch()

		for i in xrange(500):
			attacks[i].processOutput()

		for i in xrange(500):
			attacks[i].quit()
			self.assertFalse(attacks[i].isAlive())

def suite():
	tests = [
		'testBasicAttack',
		'testRestartAttack',
		'testCookieAttack',
		'testExpireTimeout',
		'testTimeoutAttack',
		'testMissingExploit',
		'testStop',
		'testInfiniteAttack',
		#'testStress',
	]
	return unittest.TestSuite(map(TestAttackTask,tests))
