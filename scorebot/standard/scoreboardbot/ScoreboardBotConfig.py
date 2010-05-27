import ConfigParser
import os

from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.config.ConfigHandler import ConfigHandler

class ScoreboardBotConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section == "ScoreboardBot"

	def parse(self,cip,section,config):
		assert(config.hasSection("SCOREBOARD_BOT") == False),"ScoreboardBot config already defined!"
		scoreboard_conf = ScoreboardBotConfig()
		scoreboard_conf.port = cip.getint(section,"port")
		config.addSection("SCOREBOARD_BOT",scoreboard_conf)

class ScoreboardBotConfig:

	def __init__(self):
		self.port = None
