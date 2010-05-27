import ConfigParser

from scorebot.config.ConfigHandler import ConfigHandler

class AttackConfigHandler(ConfigHandler):

	def __init__(self,auto_logic = True):
		self.auto_logic = auto_logic

	def canHandle(self,section):
		return section.startswith("AttackBot")

	def parse(self,cip,section,config):
		if(self.auto_logic == True):
			exploit_dir  = cip.get(section,"exploit_dir")
			exploit_timeout = cip.getint(section,"exploit_timeout_seconds")
			round_interval = cip.getint(section,"round_interval_seconds")
			gather_interval = cip.getint(section,"gather_interval_seconds")

			atkcfg = AttackConfig(self.auto_logic)
			atkcfg.exploit_dir = exploit_dir
			atkcfg.exploit_timeout = exploit_timeout
			atkcfg.round_interval = round_interval
			atkcfg.gather_interval = gather_interval
	
			config.addSection("ATTACK_BOT",atkcfg)

		else:
			exploit_dir  = cip.get(section,"exploit_dir")
			exploit_timeout = cip.getint(section,"exploit_timeout_seconds")
			atkcfg = AttackConfig(self.auto_logic)
			atkcfg.exploit_dir = exploit_dir
			atkcfg.exploit_timeout = exploit_timeout
			config.addSection("ATTACK_BOT",atkcfg)

class AttackConfig:

	def __init__(self,auto_logic=True):
		self.auto_logic = auto_logic
		self.exploit_dir = None
		self.exploit_timeout = None
		self.round_interval = None
		self.gather_interval = None

	def __str__(self):
		return "Dir: %s Timeout: %s Round: %s Gather: %s Auto: %s" % (
			str(self.exploit_dir),
			str(self.exploit_timeout),
			str(self.round_interval),
			str(self.gather_interval),
			str(self.auto_logic))

	def isValid(self):
		if(self.exploit_dir == None):
			return False
	
		if(self.auto_logic == True):	
			if(self.exploit_timeout == None):
				return False

			if(self.round_interval == None):
				return False

			if(self.gather_interval == None):
				return False

		return True
	
	def exploitDir(self):
		return self.exploit_dir

	def exploitTimeout(self):
		return self.exploit_timeout

	def roundInterval(self):
		return self.round_interval

	def gatherInterval(self):
		return self.gather_interval
