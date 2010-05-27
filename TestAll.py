from scorebot.test.standard.servicebot2 import *
from scorebot.test.standard.submitbot import *
#from scorebot.test.exploitbot import *
from scorebot.test.config import *
#from scorebot.test.gamestatebot import *
#from scorebot.test.gamelogic.usenix import *
from scorebot.test.attackengine.attackbot import *
from scorebot.test.common.communication import *
from scorebot.test.common.models import *
from scorebot.test.common.tasks import *
from scorebot.test.testservers.TestServer import TestServer
import unittest

DO_CONFIG_TESTS = True
DO_COMMS_TESTS = True
DO_SERVICE_BOT_TESTS = True
DO_COMMON_TESTS = True
DO_SUBMIT_TESTS = True
DO_ATTACK_BOT_TESTS = True
#DO_USENIX_TESTS = True
#DO_EXPLOIT_BOT_TESTS = True

alltests = []

if(DO_COMMON_TESTS):
	alltests.append(TestFlag.suite())
	#alltests.append(TestTaskRunner.suite())

if(DO_SERVICE_BOT_TESTS):
	alltests.append(TestServiceTask.suite())
	alltests.append(TestServiceBotConfig.suite())
	alltests.append(TestServiceTaskScheduler.suite())

if(DO_CONFIG_TESTS):
	alltests.append(TestConfig.suite())

if(DO_COMMS_TESTS):
	alltests.append(TestBotMessage.suite())
	alltests.append(TestBotCommClient.suite())
	#alltests.append(TestBotCommController.suite())

if(DO_SUBMIT_TESTS):
	alltests.append(TestSubmitManager.suite())
	alltests.append(TestFlagCollector.suite())

#if(DO_EXPLOIT_BOT_TESTS):
	#alltests.append(TestExploitTask.suite())
	#alltests.append(TestExploitManager.suite())
	#alltests.append(TestExploitConfig.suite())

if(DO_ATTACK_BOT_TESTS):
	alltests.append(TestAttackManager.suite())
	alltests.append(TestAttackTask.suite())

#if(DO_USENIX_TESTS):
#	alltests.append(TestUsenixScoring.suite())

suite = unittest.TestSuite(alltests)
test_server = TestServer()

if __name__ == '__main__':
	test_server.start()
	try:
		unittest.TextTestRunner(verbosity=2).run(suite)
	except:
		print "Exception while testing..."

	finally:
		test_server.terminate()
