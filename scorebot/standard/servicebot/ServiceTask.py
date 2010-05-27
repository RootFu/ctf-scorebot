import threading
import subprocess
import time
import os

class ServiceTask(threading.Thread):
	OK = 0
	ERROR = 1
	KILLED = 2
	INVALID_FLAG = 3

	def __init__(self, script, timeout, flag, ip, stored,logger=None):
		threading.Thread.__init__(self)
		self.script = script
		self.timeout = timeout
		self.flag = flag
		self.ip = ip
		self.stored = stored
		self.logger =logger
		self.callbackObj = None
		self.retcode = None
		self.result_status = None
		self.proc = None
		self.prevFlag = None
		self.error_txt = "OK"
		self.store_txt = None
		self.fin_cv = threading.Condition()

		if(self.logger != None):
			script_name = os.path.basename(script)
			self.logger.debug("Created service task script=%r ip=%r cookie=%r" % (script_name,self.ip,stored))

	def setCallbackObj(self,callbackObj):
		self.callbackObj = callbackObj

	def run(self):

		self.fin_cv.acquire()

		cmd_list = [self.script,self.ip,self.flag]
		if(self.stored != None):
			cmd_list.append(self.stored)

		self.proc = subprocess.Popen(
				cmd_list, 
				stdout=subprocess.PIPE,
				stdin=None,
				stderr=subprocess.STDOUT,
				cwd=os.path.dirname(self.script),
				close_fds=True)

		slept = 0
	
		self.retcode = self.proc.poll()
		while(self.retcode == None and slept < self.timeout):
			time.sleep(1)
			slept += 1
			self.retcode = self.proc.poll()

		if(self.retcode == None):
			self.proc.kill()
			self.retcode = self.proc.wait()
			self.result_status = ServiceTask.KILLED

		else:
			self.__parseResults()

		self.fin_cv.notifyAll()
		self.fin_cv.release()

		if(self.callbackObj != None):
			self.callbackObj.call()

	def status(self):
		self.fin_cv.acquire()
		while(self.result_status == None):
			self.fin_cv.wait()
		self.fin_cv.release()
		return self.result_status

	def setInvalidFlag(self):
		self.status()
		self.result_status = ServiceTask.INVALID_FLAG

	def getPrevFlag(self):
		self.status()
		return self.prevFlag

	def error(self):
		self.status()
		return self.error_txt

	def store(self):
		self.status()
		return self.store_txt

	def __parseResults(self):
		for line in self.proc.stdout.readlines():

			if(self.logger != None):
				self.logger.debug("(%s) %r" % (self.ip,line.strip()))

			if(line.startswith("FLAG:")):
				self.prevFlag = line[5:].strip()
				self.__setStatus(ServiceTask.OK)

			elif(line.startswith("ERROR:")):
				self.result_status = ServiceTask.ERROR
				self.error_txt = line[6:].strip()

			elif(line.startswith("COOKIE:")):
				self.store_txt = line[7:].strip()

		if(self.prevFlag == None):
			self.prevFlag = "No Flag"
			self.__setStatus(ServiceTask.INVALID_FLAG)


	def __setStatus(self,value):
		if(self.result_status == None):
			self.result_status = value

