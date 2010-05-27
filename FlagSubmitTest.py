from scorebot.attackengine.flagsubmissionbot.FlagSubmitter import FlagSubmitter
from scorebot.attackengine.flagsubmissionbot.Defcon17SubmitClient import Defcon17SubmitClient
import sys
import time
import random
import logging

def buildLogger():
	logger = logging.getLogger("FlagSubmitTest")
	logger.setLevel(logging.DEBUG)

	formatter = logging.Formatter(
		"%(asctime)s| %(name)s(%(levelname)s): %(message)s",
		"%m/%d/%y %H:%M:%S")
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger

def main(args):
	print "main"
	logger = buildLogger()
	client = Defcon17SubmitClient()
	submitter = FlagSubmitter("test_flags.db",logger,client)

	while True:
		for i in range(random.randint(1,5)):
			flag = ''.join([random.choice('0123456789abcdef') for x in xrange(10)])
			submitter.submit(flag,"test.py")			
		time.sleep(5)

if __name__ == "__main__":
	main(sys.argv[1:]);
