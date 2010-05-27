import ConfigParser
import os

from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.config.ConfigHandler import ConfigHandler

class SubmitBotConfigHandler(ConfigHandler):

	def canHandle(self,section):
		return section == "SubmitBot"

	def parse(self,cip,section,config):
		assert(config.hasSection("SUBMIT_BOT") == False),"SubmitBot data already defined!"
		submitbot_conf = SubmitBotConfig()
		submitbot_conf.port = cip.getint(section,"port")
		config.addSection("SUBMIT_BOT",submitbot_conf)

class SubmitBotConfig:

	def __init__(self):
		self.port = None

	def port(self):
		return self.port
