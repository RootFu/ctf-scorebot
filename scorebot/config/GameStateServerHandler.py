import ConfigParser
from scorebot.config.ConfigHandler import ConfigHandler
from scorebot.common.models.GameStateServerInfo import GameStateServerInfo

class GameStateServerHandler(ConfigHandler):

	def canHandle(self,section):
		return section == "GameStateServer"

	def parse(self,cip,section,config):
		host = cip.get(section,"host")
		port = cip.getint(section,"port")
		key = cip.get(section,"key")
		iv = cip.get(section,"iv")

		if(len(key) != 16 or len(iv) != 8):
			raise ConfigParser.ParsingError(
				"Key length must be 16 and iv length must be 8.")

		info = GameStateServerInfo(host,port,key,iv)
		config.setGameStateServerInfo(info)
