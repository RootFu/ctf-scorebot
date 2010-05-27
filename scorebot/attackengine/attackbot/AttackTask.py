import threading
import subprocess
import os
import time

from scorebot.common.tasks.TaskRunner import TaskRunner

class AttackTimer(threading.Thread):

	def __init__(self,runner,timeout):
		threading.Thread.__init__(self)
		self.runner = runner
		self.timeout = timeout
		self.lock = threading.Lock()
		self.running = True	
		self.infinite = False

	def run(self):
		while(self.running):

			with self.lock:
				if(self.runner.taskAlive() and self.timeout == 0 and self.infinite == False):
					self.runner.taskStop()

			time.sleep(1)

			with self.lock:
				if(self.runner.taskAlive() and self.infinite == False):
					self.timeout -= 1

	def setTimeout(self,timeout):
		with self.lock:
			self.timeout = timeout
			self.infinite = False

	def setInfinite(self):
		with self.lock:
			self.infinite = True
	
class AttackTask():
	
	def __init__(self,script,ip,timeout,logger):
		self.logger = logger

		if(self.logger != None):
			self.logger.debug("Creating Attack Task: %r %r %d" % (script,ip,timeout))

		thread_size = threading.stack_size(524288)
		self.runner = TaskRunner()
		self.runner.start()
		
		self.script = script
		self.line_q = None
		self.ip = ip
		self.cookie = None
		self.captured_flags = []

		self.timeout = timeout
		self.timeout_set = False
		self.timer = AttackTimer(self.runner,timeout)
		self.timer.start()
		threading.stack_size(thread_size)

	def launch(self,overwrite_key=None):
		cmd = [self.script,self.ip]

		if(overwrite_key != None):
			cmd.append(overwrite_key)

		if(self.cookie != None):
			cmd.append(self.cookie)

		self.line_q = self.runner.taskStart(cmd)
		self.timeout_set = False
		self.timer.setTimeout(self.timeout)

	def isAlive(self):
		return self.runner.taskAlive()

	def stop(self):
		self.runner.taskStop()

	def quit(self):
		self.timer.running = False
		self.runner.quit()

	def processOutput(self):
		assert(self.line_q != None)
		count = self.line_q.qsize()

		for i in xrange(count):
			line = self.line_q.get(False)
			assert(line != None)

			if(line == ""):
				continue

			if(self.logger != None):
				self.logger.debug("(%s) %r" % (self.ip,line))

			if(line.startswith("FLAG:")):
				self.captured_flags.append(line[5:].strip())
				if(self.timeout_set == False):
					self.timer.setTimeout(self.timeout)

			if(line.startswith("COOKIE:")):
				self.cookie = line[7:].strip()
				if(self.timeout_set == False):
					self.timer.setTimeout(self.timeout)

			if(line.startswith("TIMEOUT:")):
				value = line[8:].strip()
				if(value.upper() == "INFINITE"):
					self.timer.setInfinite()
				else:
					value = int(value)
					if(value == 0):
						self.timeout_set = False
						self.timer.setTimeout(self.timeout)

					else:
						self.timer.setTimeout(value)
						self.timeout_set = True

			line = None 

	def collectFlags(self):
		flags = self.captured_flags
		self.captured_flags = []
		return flags
