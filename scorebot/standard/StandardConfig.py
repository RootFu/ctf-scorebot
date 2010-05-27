import ConfigParser
from scorebot.config.ConfigHandler import ConfigHandler

class FlagConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section == "Flag"

	def parse(self,cip,section,config):
		assert(config.hasSection("FLAG") == False),"Flag config already defined!"
		phrase = cip.get(section,"passphrase")
		duration = cip.getint(section,"valid_duration_minutes")*60
		flag_conf = FlagConfig(duration,phrase)
		config.addSection("FLAG",flag_conf)

class FlagConfig:

	def __init__(self,duration,passphrase):
		self.duration = duration
		self.passphrase = passphrase

	
