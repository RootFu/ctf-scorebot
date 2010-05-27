import unittest
import time
import threading
import random

from scorebot.config.Config import Config
from scorebot.common.models.Flag import FlagManager, Flag
from scorebot.standard.submitbot.FlagCollector import FlagCollector

class FlagCollectorPopulator(threading.Thread):
	def __init__(self,fc,count,N):
		threading.Thread.__init__(self)
		self.fc = fc
		self.count = count
		self.N = N

	def run(self):
		foo = time.time()
		random.jumpahead(self.N)
		time.sleep(random.random())
		
		for i in xrange(self.count):
			flag = Flag(0,i,0,foo)
			self.fc.enque(flag)

class TestFlagCollector(unittest.TestCase):

	def setUp(self):
		self.conf = Config()
		self.conf.setFlagDuration(60)
		self.conf.addTeamInfo("Team1","127.0.0.1","127.0.0.0/24")
		self.conf.addTeamInfo("Team2","127.0.1.1","127.0.1.0/24")

	def testBasicUsage(self):
		fc = FlagCollector()
		f1 = Flag(0,0,0,time.time())
		f2 = Flag(0,1,0,time.time())
		fc.enque(f1)
		fc.enque(f2)

		flags = fc.collect()
		self.assert_(len(flags) == 2)

		flags = fc.collect()
		self.assert_(len(flags) == 0)

	def testThreadSafety(self):
		fc = FlagCollector()
		p1 = FlagCollectorPopulator(fc,10000,10)
		p2 = FlagCollectorPopulator(fc,10000,20)
		p3 = FlagCollectorPopulator(fc,10000,30)
		p4 = FlagCollectorPopulator(fc,10000,30)
		p5 = FlagCollectorPopulator(fc,10000,30)
		
		p1.start()
		p2.start()
		p3.start()
		p4.start()
		p5.start()

		total = 0
		for i in xrange(1000):
			total += len(fc.collect())
			time.sleep(1.0/1000.0)

		p1.join()
		p2.join()
		p3.join()
		p4.join()
		p5.join()

		total += len(fc.collect())		
		self.assertEquals(total,50000)

def suite():
	tests = [
		'testBasicUsage',
		'testThreadSafety',
	]
	return unittest.TestSuite(map(TestFlagCollector,tests))

if __name__ == '__main__':
	unittest.main()
