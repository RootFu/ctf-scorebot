import threading
import subprocess
import os
import time

from scorebot.common.tasks.TaskRunner import TaskRunner
from scorebot.common.models.TeamInfo import TeamInfo

"""
Service Task is responsible for executing and collecting
output of the service scripts. Timeouts are to be handled
by the TaskSchedular. No disk persistance at this level,
but this will hold the last cookie in memory.

Service Task simply collects data, and should be called
in a loop like:
init()
loop:
  launch(NewFlag)
  finish()
  processOutput()
quit()

launch will reset prevFlag() and error() to return None
until processOutput is called again. Caller is responsible
for turning the combination of flags and error messages into
a status value for scoring.
"""

class ServiceTask():

	def __init__(self,script,team,logger=None):
		self.logger = logger

		if(self.logger != None):
			self.logger.debug("Creating Service Task: %r %r" % (team.host,script))

		thread_size = threading.stack_size(524288)
		self.runner = TaskRunner()
		self.runner.start()

		self.script = script
		self.team = team
		self.cookie_txt = None
		self.error_txt = None

		self.prev_flag = None
		self.current_flag = None
		self.expected_flag = None

		self.line_q = None
		threading.stack_size(thread_size)

	def launch(self,flag):
		cmd = [self.script,self.team.host,flag]

		if(self.cookie_txt != None):
			cmd.append(self.cookie_txt)

		self.expected_flag = self.current_flag
		self.current_flag = flag

		self.prev_flag = None
		self.error_txt = None
		
		if(self.logger != None):
			self.logger.debug("Service Task starting for %r (%r)" % (self.team.host,flag))

		self.line_q = self.runner.taskStart(cmd)

	def isAlive(self):
		return self.runner.taskAlive()

	def finish(self):
		self.runner.taskStop()
		if(self.logger != None):
			self.logger.debug("Service Task finished for %r" % (self.team.host))

	def prevFlag(self):
		return self.prev_flag

	def retcode(self):
		return self.runner.taskRetcode()

	def gotExpectedFlag(self):
		if(self.prev_flag == None or self.expected_flag == None):
			return False
		return self.prev_flag == self.expected_flag

	def cookie(self):
		return self.cookie_txt

	def error(self):
		return self.error_txt

	def quit(self):
		self.runner.quit()

	def processOutput(self):
		assert(self.line_q != None)

		for i in xrange(self.line_q.qsize()):
			line = self.line_q.get(False)

			assert(line != None)

			if(line == ""):
				continue

			if(self.logger != None):
				self.logger.debug("(%s) %r" % (self.team.host,line.strip()))

			if(line.startswith("FLAG:")):
				self.prev_flag = line[5:].strip()

			elif(line.startswith("ERROR:")):
				self.error_txt = line[6:].strip()

			elif(line.startswith("COOKIE:")):
				self.cookie_txt = line[7:].strip()
