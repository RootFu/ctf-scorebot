import os
import time
import threading
import Queue
import os
import socket
import ssl

from scorebot.common.tasks.TaskRunner import TaskRunner
from scorebot.attackengine.attackbot.AttackTask import AttackTask

def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

class AttackManager(threading.Thread):

	LAUNCH_EXPLOIT = 'L'
	LAUNCH_ALL = 'A'
	KILL_EXPLOIT = 'K'
	KILL_ALL = 'KA'
	STOP_ALL = 'SA'
	PROCESS_OUTPUT = 'P'
	GATHER_FLAGS = 'G'
	UPDATE_EXPLOITS = 'U'
	TEST_GET_EXPLOITS = 'TE'

	def __init__(self,conf,logger,init,auto):
		threading.Thread.__init__(self)
		self.daemon = True
		
		self.init = init
		self.conf = conf
		self.auto = auto
		self.logger = logger
		self.overwrite_key = "NotSet"
		if(self.logger != None):
			self.logger.warn("Add generic support for overwrite keys (defcon17)")

		self.attack_conf = conf.getSection("ATTACK_BOT")
		self.exploits = set()
		self.attack_tasks = {}
		self.collected_flags = Queue.Queue()
		self.cmd_q = Queue.Queue()
		self.test_q = Queue.Queue()

		assert(self.attack_conf.isValid())
		self.attack_tasks = {}

	def run(self):

		if(self.auto == True):
			self.__mainLoopAuto()

		else:
			self.__mainLoopWait()

	def cmd(self,cmd,args=None):
		self.cmd_q.put(cmd)
		if(args != None):
			self.cmd_q.put(args)

	def test(self,cmd):
		self.cmd_q.put(cmd)
		return self.test_q.get()

	def __mainLoopWait(self):
		while(True):
			cmd = self.cmd_q.get()

			if(cmd == AttackManager.LAUNCH_EXPLOIT):
				exploit = self.cmd_q.get()
				self.__launchExploit(exploit)

			elif(cmd == AttackManager.KILL_EXPLOIT):
				exploit = self.cmd_q.get()
				self.__killExploit(exploit)

			elif(cmd == AttackManager.LAUNCH_ALL):
				for attack in self.attack_tasks.itervalues():
					if(attack.isAlive() == False):
						attack.launch()
			
			elif(cmd == AttackManager.STOP_ALL):
				for attack in self.attack_tasks.itervalues():
					if(attack.isAlive() == False):
						attack.stop()

			elif(cmd == AttackManager.PROCESS_OUTPUT):
				for attack in self.attack_tasks.itervalues():
					if(attack.line_q != None):
						attack.processOutput()
				
			elif(cmd == AttackManager.GATHER_FLAGS):
				for key,attack in self.attack_tasks.items():
					flags = attack.collectFlags()
					if(len(flags) > 0):
						teamId,exploit = key
						self.collected_flags.put((teamId,exploit,flags))

			elif(cmd == AttackManager.UPDATE_EXPLOITS):
				self.__updateAvailableExploits()

			elif(cmd == AttackManager.TEST_GET_EXPLOITS):
				self.test_q.put(self.exploits)

			else:
				assert(False),"Unkown command: %s" % cmd

	def __mainLoopAuto(self):
		gather_counter = 0
		round_counter = 0

		while(True):
			
			if(gather_counter == self.attack_conf.gatherInterval()):
				gather_counter = 0

				for attack in self.attack_tasks.itervalues():
					attack.processOutput()

				for key,attack in self.attack_tasks.items():
					flags = attack.collectFlags()
					if(len(flags) > 0):
						teamId,exploit = key
						self.collected_flags.put((teamId,exploit,flags))

			if(round_counter == self.attack_conf.roundInterval()):
				round_counter = 0
				#self.__updateOverwriteKey()
				self.__updateAvailableExploits()
				for attack in self.attack_tasks.itervalues():
					if(attack.isAlive() == False):
						attack.launch(self.overwrite_key)

			time.sleep(1)
			gather_counter += 1
			round_counter += 1

	def getFlags(self):
		results = []
		try:
			size = self.collected_flags.qsize()
			for i in xrange(size):
				results.append(self.collected_flags.get(False))

			return results

		except Queue.Empty:
			return results

	def __updateAvailableExploits(self):
		exploit_dir = self.attack_conf.exploitDir()
		exploit_set = set()
		
		for file in os.listdir(exploit_dir):
			path = os.path.join(exploit_dir,file)
			if(	os.path.isdir(path) == False and 
				os.access(path,os.X_OK) and
				not path.endswith(".bin") and
				not path.endswith(".dat")):
				exploit_set.add(file)

		new_exploits = exploit_set - self.exploits
		removed_exploits = self.exploits - exploit_set

		for exploit in new_exploits:
			self.__updateAttacks(exploit)

		for exploit in removed_exploits:
			self.__stopAttacks(exploit)

		self.exploits = exploit_set

	def __launchExploit(self,exploit):
		try:
			for team in self.conf.teams:
				key = (team.id,exploit)
				attack = self.attack_tasks[key]
				if(attack.isAlive() == False):
					attack.launch()

		except KeyError:
			print "LOG THIS - tried to launch unknown exploit",exploit

	def __killExploit(self,exploit):
		try:
			for team in self.conf.teams:
				key = (team.id,exploit)
				attack = self.attack_tasks[key]
				if(attack.isAlive() == False):
					attack.launch()

		except KeyError:
			print "LOG THIS - tried to kill unknown exploit",exploit
		
	def __updateAttacks(self,exploit):
		exploit_dir = self.attack_conf.exploitDir()
		path = os.path.join(exploit_dir,exploit)
		logger = self.conf.buildLogger("Exploit-%s" % exploit)
		for team in self.conf.teams:
			attack = AttackTask(path,team.host,self.attack_conf.exploitTimeout(),logger)
			key = (team.id,exploit)
			self.attack_tasks[key] = attack

	def __stopAttacks(self,exploit):
		pass

	"""
	def __updateOverwriteKey(self):
		self.logger.error("Using Defcon17 specific workaround to update overwrite key...")
		try:
			s = socket.socket()
			s.settimeout(1)
			s.connect(("10.31.100.100",2525))

			mod_path = modulePath()
			keyfile_path = os.path.join(mod_path,"team_5_key")
			certfile_path = os.path.join(mod_path,"team_5_key.cert")

			ssl_sock = ssl.wrap_socket(
				sock=s,
				keyfile=keyfile_path,
				certfile=certfile_path)
			ssl_sock.write("NEWKEY\n")
			line = ssl_sock.read().strip()
			ssl_sock.close()

			self.overwrite_key = line
			self.logger.info("New overwrite key: %s" % line)

		except Exception as e:
			self.logger.error("Failed to update the overwrite key, using old key (%s)" % str(e))
	"""	
