import ConfigParser
import os

from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.config.ConfigHandler import ConfigHandler

def _getServiceBotConfig(conf):

	if(conf.hasSection("SERVICE_BOT") == False):
		servicebot_conf = ServiceBotConfig()
		conf.addSection("SERVICE_BOT",servicebot_conf)

	return conf.getSection("SERVICE_BOT")
		
class ServiceBotConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section == "ServiceBot"

	def parse(self,cip,section,config):
		min_duration = cip.getfloat(section,"min_round_duration_minutes")
		max_duration = cip.getfloat(section,"max_round_duration_minutes")

		servicebot_conf = _getServiceBotConfig(config)
		servicebot_conf.min_duration_seconds = min_duration*60.0
		servicebot_conf.max_duration_seconds = max_duration*60.0

class ServiceConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section.startswith("Service:")

	def parse(self,cip,section,config):
		name = section[8:]
		script = cip.get(section,"script")
		timeout = int(cip.get(section,"timeout"))
		offscore = int(cip.get(section,"offscore"))
		defscore = int(cip.get(section,"defscore"))

		if(cip.debug == False):
			if(os.access(script,os.X_OK) == False):
				raise ConfigParser.ParsingError(
					"Script %s does not appear to be executable!" % (script))

		servicebot_conf = _getServiceBotConfig(config)
		servicebot_conf.addServiceInfo(name,script,timeout,offscore,defscore)

class ServiceBotConfig:

	def __init__(self):
		self.services = []
		self.min_duration_seconds = None
		self.max_duration_seconds = None

	def isValid(self):
		if(self.min_duration_seconds == None):
			return False

		if(self.max_duration_seconds == None):
			return False

		return True

	def numServices(self):
		return len(self.services)

	def getServiceInfoById(self,id):
		return self.services[id]

	def getRoundLengthMin(self):
		return self.min_duration_seconds

	def getRoundLengthMax(self):
		return self.max_duration_seconds

	def addServiceInfo(self,name,script,timeout,offscore,defscore):
		id = len(self.services)
		service_info = ServiceInfo(id,name,script,timeout,offscore,defscore)
		self.services.append(service_info)
