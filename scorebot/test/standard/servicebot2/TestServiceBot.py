import unittest
import time

from scorebot.standard.servicebot.ServiceBot import ServiceBot
from scorebot.config import Config

class TestServiceRunner(unittest.TestCase):

	def testOneScript(self):
		bot = ServiceBot()
	
def suite():
	tests = [
		'testOneScript',
	]
	return unittest.TestSuite(map(TestServiceRunner,tests))
