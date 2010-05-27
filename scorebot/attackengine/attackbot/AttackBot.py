import time
import os
import stat
import Queue

from multiprocessing import Process

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

from scorebot.attackengine.attackbot.AttackManager import AttackManager

class AttackBot(Process):

	def __init__(self,conf,init=False,auto_restart=True):
		Process.__init__(self)
		self.conf = conf
		self.comm = None
		self.init = init
		self.logger = conf.buildLogger("AttackBot")
		self.attack_manager = AttackManager(conf,self.logger,init,auto_restart)
		self.auto_restart = auto_restart

		self.attack_conf = self.conf.getSection("ATTACK_BOT")
		self.round_time = self.attack_conf.roundInterval()
		
	def run(self):
		self.attack_manager.start()		
		
		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"ATTACK_BOT")

		self.comm.start()

		if(self.auto_restart == True):
			self.logger.info("Starting (AUTO Logic)")
			self.__mainLoopAuto()
		else:
			self.logger.info("Starting (WAIT Logic)")
			self.__mainLoopWait()

	def __mainLoopWait(self):
		while(True):
			msg = self.comm.receive()
			self.logger.debug("Wait logic processing msg: %s (%s)" % (msg.type,str(msg.data)))

			if(msg.type == "EXECUTE_EXPLOITS"):
				exploits = msg.data
				for exploit in exploits:
					self.attack_manager.cmd(AttackManager.LAUNCH_EXPLOIT,exploit)

			elif(msg.type == "UPDATE_EXPLOITS"):
				self.attack_manager.cmd(AttackManager.UPDATE_EXPLOITS)
				

			elif(msg.type == "PROCESS_OUTPUT"):
				self.attack_manager.cmd(AttackManager.PROCESS_OUTPUT)

			elif(msg.type == "GATHER_FLAGS"):
				self.attack_manager.cmd(AttackManager.GATHER_FLAGS)
				collected = []
				while(True):
					try:
						collected.append(
							self.attack_manager.collected_flags.get(True,1))
					except Queue.Empty:
						break

				self.comm.send(BotMessage("COLLECTED_FLAGS",collected))

			elif(msg.type == "STOP_EXPLOITS"):
				self.attack_manager.cmd(AttackManager.STOP_ALL)

			elif(msg.type == "TERMINATE"):
				self.comm.kill()
				break

			else:
				assert(False),"Invalid msg type received"

	def __mainLoopAuto(self):
		while(True):
			msg = self.comm.receive(True,1)

			if(msg != None):				
				if(msg.type == "TERMINATE"):
					self.comm.kill()
					break

				elif(msg.type == "NEW_EXPLOIT"):
					self.__newExploit(msg.data[0],msg.data[1])

				elif(msg.type == "LIST_EXPLOITS"):
					exploits = self.__listExploits()
					self.comm.sendResponse(msg,BotMessage("LIST_EXPLOITS_RESULT",exploits))	
	
				elif(msg.type.startswith("GET_LOG:")):
					payload = msg.type[8:]
					(exploit, lines) = payload.split("|")
					lines = int(lines)
					log_data = self.__getLog(exploit,lines)
					self.comm.sendResponse(msg,BotMessage("GET_LOG_RESULT:%s" % exploit, log_data))		
	
				elif(msg.type.startswith("GET_EXPLOIT:")):
					exploit = msg.type[12:]
					data = self.__getExploit(exploit)
					self.comm.sendResponse(msg,BotMessage("GET_EXPLOIT_RESULT:%s" % exploit, data))	

				elif(msg.type.startswith("TOGGLE_EXPLOIT:")):
					exploit = msg.type[15:]
					self.__toggleExploit(exploit)
			else:
				flags = self.attack_manager.getFlags()
				if(len(flags) != 0):
					self.comm.send(BotMessage("COLLECTED_FLAGS",flags))

	def __newExploit(self,filename,filedata):
		self.logger.info("New exploit uploaded: %s" % filename)
		exploit_dir = self.attack_conf.exploitDir()
		path = os.path.join(exploit_dir,filename)
		exploit_file = open(path,"w")
		exploit_file.write(filedata)
		exploit_file.close()
		os.chmod(path,stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)

	def __toggleExploit(self,exploit):
		exploit_dir = self.attack_conf.exploitDir()
		exploit_path = os.path.join(exploit_dir,exploit)

		if(	exploit.endswith(".bin") or
			exploit.endswith(".dat")):
			self.logger.warn("Tried to toggled data file %s" % exploit)

		elif(os.path.exists(exploit_path) and not os.path.isdir(exploit_path)):
			if(os.access(exploit_path,os.X_OK)):
				self.logger.info("Toggled %s off" % exploit)
				os.chmod(exploit_path,
					stat.S_IRUSR | stat.S_IWUSR | 
					stat.S_IRGRP | stat.S_IWGRP |
					stat.S_IROTH | stat.S_IWOTH )
			else:
				self.logger.info("Toggled %s on" % exploit)
				os.chmod(exploit_path,stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
		else:
			self.logger.warn("Tried to toggle unknown exploit: %s" % exploit)

	def __listExploits(self):
		exploit_dir = self.attack_conf.exploitDir()
		exploits = []

		for file in os.listdir(exploit_dir):	
			path = os.path.join(exploit_dir,file)

			if(	os.path.isdir(path) == True or
				path.endswith(".bin") or
				path.endswith(".dat")):
				continue

			if(os.access(path,os.X_OK)):
				exploits.append((file,True))
			else:
				exploits.append((file,False))

		return exploits

	def __getExploit(self, exploit):
		try:
			exploit_dir = self.attack_conf.exploitDir()
			path = os.path.join(exploit_dir,exploit)
			file = open(path,"r")
			data = file.read()

			return data
		except:
			return None


	def __getLog(self, exploit, nLines):
		try:
			log = os.path.join(self.conf.log_dir,"Exploit-%s.log"%exploit)
			file = open(log,"r")
			file.seek(0,os.SEEK_END)
			fsize = file.tell()
			file.seek(max(fsize-65536,0),0)
			lines = file.readlines()
	
			if len(lines) > nLines:
				lines = lines[-nLines:]

			return lines
		except Exception as e:
			self.logger.error("Error getting exploit log: %s" % e)
		return []
		

