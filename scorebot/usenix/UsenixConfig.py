import ConfigParser

from scorebot.config.ConfigHandler import ConfigHandler

def _getUsenixConfig(config):
	if(config.hasSection("USENIX_CONFIG") == False):
		usenix_config = UsenixConfig()
		config.addSection("USENIX_CONFIG",usenix_config)
	return config.getSection("USENIX_CONFIG")
 
class UsenixExploitConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section.startswith("UsenixExploit")

	def parse(self,cip,section,config):
		name = section.split(":")[1].strip()
		service = cip.get(section,"service")
		value = cip.getint(section,"value")
		captures_flags = cip.getboolean(section,"captures_flags")
		
		usenix_config = _getUsenixConfig(config)
		id = len(usenix_config.exploits)
		exploit = UsenixExploit(id,name,service,value,captures_flags)
		usenix_config.exploits.append(exploit)

class UsenixConfigHandler:

	def canHandle(self,section):
		return section == "Usenix"

	def parse(self,cip,section,config):
		exploit_round_time = cip.getfloat(section,"exploit_round_duration_minutes")
		total_game_rounds = cip.getint(section,"total_game_rounds")
		service_round_count = cip.getint(section,"service_rounds_per_exploit")
		reboot_time = cip.getint(section,"reboot_time_minutes")
		data_dir = cip.get(section,"usenix_data_dir")
		exploit_dir = cip.get(section,"usenix_exploit_dir")

		usenix_config = _getUsenixConfig(config)
		usenix_config.exploit_dir = exploit_dir
		usenix_config.data_dir = data_dir
		usenix_config.exploit_round_time_seconds = exploit_round_time*60.0
		usenix_config.total_game_rounds = total_game_rounds
		usenix_config.service_round_count = service_round_count
		usenix_config.reboot_time = reboot_time * 60.0
		
class UsenixExploit:

	def __init__(self,id,name,service,value,captures_flags):
		self.id = id
		self.name = name
		self.service = service
		self.value = value
		self.captures_flags = captures_flags

class UsenixConfig:

	def __init__(self):
		self.exploit_round_time_seconds = None
		self.total_game_rounds = None
		self.service_round_count = None
		self.exploit_dir = None
		self.data_dir = None
		self.reboot_time = None
		self.exploits = []

	def isValid(self):
		if(self.round_time_seconds == None):
			return False

		if(self.reboot_time == None):
			return False

		return True

	def getExploitById(self,exploitId):
		return self.exploits[exploitId]

	def getExploitRoundTime(self):
		return self.exploit_round_time_seconds

	def getTotalGameRounds(self):
		return self.total_game_rounds

	def getServiceRoundCount(self):
		return self.service_round_count

	def rebootTime(self):
		return self.reboot_time
