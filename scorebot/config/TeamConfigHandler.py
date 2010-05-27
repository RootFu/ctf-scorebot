import ConfigParser
from scorebot.config.ConfigHandler import ConfigHandler

class TeamConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section.startswith("Team:")

	def parse(self,cip,section,config):
		name = section[5:]
		host = cip.get(section,"host")
		cidr = cip.get(section,"cidr")
		config.addTeamInfo(name,host,cidr)
