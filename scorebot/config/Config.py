import ConfigParser
import logging
import os

from scorebot.common.models.TeamInfo import TeamInfo
#from scorebot.common.models.ServiceInfo import ServiceInfo
from scorebot.common.models.Flag import FlagManager

class NullHandler(logging.Handler):

	def emit(self,record):
		pass

"""
NOTE:

I am in the process of rearchtecting the config class to be more adaptable.
Eventually, I want to make the config object little more then a hash table.
As it is, it is sort of a mesh between the new approach and the old approach.
"""

class Config:

	def __init__(self):
		self.sections = {}

		#Old Approach below - essentially this is "global" data
		#Making changes and appending values is harder then it needs to be
		self.base_path = ""
		self.teams = []

		#Logging
		self.use_console_logging = False
		self.use_file_logging = False
		self.log_dir = "/tmp/"
		self.file_log_level = logging.DEBUG
		self.console_log_level = logging.DEBUG

		#gamestate
		self.gamestate = None

	def isValid(self,section_list):
		if(self.base_path == ""):
			return False

		for section in section_list:
			if(self.hasSection(section) == False):
				return False

		return True

	def addSection(self,section_name,value):
		assert(self.sections.has_key(section_name) == False)
		self.sections[section_name] = value
	
	def getSection(self,section_name):
		assert(self.sections.has_key(section_name) == True)
		return self.sections[section_name]

	def setSection(self,section_name,value):
		assert(self.sections.has_key(section_name) == True)
		self.sections[section_name] = value

	def hasSection(self,section_name):
		return self.sections.has_key(section_name)
		
	def teams():
		return self.teams

	def numTeams(self):
		return len(self.teams)

	def getBasePath(self):
		return self.base_path

	def getTeamInfoById(self,id):
		return self.teams[id]

	def getGameStateServerInfo(self):
		return self.gamestate

	def addTeamInfo(self,name,host,cidr):
		id = len(self.teams)
		team_info = TeamInfo(id,name,host,cidr)
		self.teams.append(team_info)

	#def setRoundLengthMin(self,min):
	#	self.min_round = min
	
	#def setRoundLengthMax(self,max):
	#	self.max_round = max

	def setBasePath(self,path):
		self.base_path = path

	def setGameStateServerInfo(self,info):
		self.gamestate = info

	def buildFlagManager(self):
		assert(self.hasSection("FLAG"))
		flag_conf = self.getSection("FLAG")
		key = self.gamestate.key
		iv = self.gamestate.iv
		phrase = flag_conf.passphrase
		return FlagManager(key,iv,phrase)

	def buildLogger(self,name):
		logger = logging.getLogger(name)
		logger.setLevel(logging.DEBUG)

		formatter = logging.Formatter(
			"%(asctime)s| %(name)s(%(levelname)s): %(message)s",
			"%m/%d/%y %H:%M:%S")

		null_handler = NullHandler()
		null_handler.setLevel(logging.DEBUG)
		logger.addHandler(NullHandler())
		
		if(self.use_console_logging):
			handler = logging.StreamHandler()
			handler.setFormatter(formatter)
			handler.setLevel(self.console_log_level)
			logger.addHandler(handler)
		
		if(self.use_file_logging):
			path = os.path.join(self.log_dir,"%s.log"%name)
			handler = logging.FileHandler(path)
			handler.setFormatter(formatter)
			handler.setLevel(self.file_log_level)
			logger.addHandler(handler)

		return logger
