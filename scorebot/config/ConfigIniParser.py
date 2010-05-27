import sys
import os
import ConfigParser
import logging

from scorebot.config.Config import Config
from scorebot.common.models.TeamInfo import TeamInfo
from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.config.TeamConfigHandler import TeamConfigHandler
from scorebot.config.GameStateServerHandler import GameStateServerHandler

class ConfigIniParser(ConfigParser.SafeConfigParser):

	def __init__(self,debug=False):
		ConfigParser.SafeConfigParser.__init__(self)
		self.handlers = [
			TeamConfigHandler(),
			GameStateServerHandler(),
		]

		self.config_path = ""
		self.debug = debug

	def addHandler(self,handler):
		self.handlers.append(handler)

	def load(self,config_path):
		try:
			self.config_path = config_path
			self.read(config_path)

			conf = Config()

			assert(os.path.isfile(config_path)),"%s does not exsist!" % config_path
			assert("base_path" in self.defaults()),"Config file %s has no base_path set!" % config_path
			msg = "No such directory: %s, be sure to edit the base_path in the config file!" % self.defaults()["base_path"]
			assert(os.path.isdir(self.defaults()["base_path"])),msg

			conf.setBasePath(self.defaults()["base_path"])

			#Set up logging first
			self.__parseLogging(conf)
			sections = self.sections()
			sections.remove("Logging")

			for section in sections:
				processed = False
				for handler in self.handlers:
					if(handler.canHandle(section)):
						processed = True
						handler.parse(self,section,conf)
						break

				if(processed == False):
					msg = "Unknown Section: %s" % section
					raise ConfigParser.ParsingError(msg)		
			return conf
		
		except ConfigParser.ParsingError as e:
			err = "Error parsing %s: %s" %(self.config_path,e)
			sys.exit(err)

		except ConfigParser.NoSectionError as e:
			err = "Error parsing %s: A required section is missing: %s" %(self.config_path,e.section)
			sys.exit(err)
	
		except ConfigParser.NoOptionError as e:
			err = "Error parsing %s: A required option in section %s is missing: %s" % (
				self.config_path,e.section,e.option)
			sys.exit(err)

		"""
		except Exception as e:
			print type(e)
			err = "General expception parsing %s: %s" % (self.config_path,e)
			sys.exit(err)
		"""
	def __parseLogging(self,conf):
		log_to_console = self.getboolean("Logging","log_to_console")
		log_to_file = self.getboolean("Logging","log_to_file")
		log_dir = self.get("Logging","log_dir")
		file_log_level = self.get("Logging","file_log_level")
		console_log_level = self.get("Logging","console_log_level")

		conf.use_console_logging = log_to_console
		conf.use_file_logging = log_to_file
		conf.log_dir = log_dir

		if(file_log_level.upper() == "DEBUG"):
			conf.file_log_level = logging.DEBUG
		elif(file_log_level.upper() == "INFO"):
			conf.file_log_level = logging.INFO
		elif(file_log_level.upper() == "WARNING"):
			conf.file_log_level = logging.WARNING
		elif(file_log_level.upper() == "ERROR"):
			conf.file_log_level = logging.ERROR
		elif(file_log_level.upper() == "CRITICAL"):
			conf.file_log_level = logging.CRITICAL
		else:
			msg = "Unknown file log level (%s), should be one of: debug, info, warning, error, critical" % file_log_level
			raise ConfigParser.ParsingError(msg)		
		
		if(console_log_level.upper() == "DEBUG"):
			conf.console_log_level = logging.DEBUG
		elif(console_log_level.upper() == "INFO"):
			conf.console_log_level = logging.INFO
		elif(console_log_level.upper() == "WARNING"):
			conf.console_log_level = logging.WARNING
		elif(console_log_level.upper() == "ERROR"):
			conf.console_log_level = logging.ERROR
		elif(console_log_level.upper() == "CRITICAL"):
			conf.console_log_level = logging.CRITICAL
		else:
			msg = "Unknown console log level (%s), should be one of: debug, info, warning, error, critical" % log_level
			raise ConfigParser.ParsingError(msg)		
		
