from multiprocessing import Process

import sys
import time
import getopt

#Common Imports
from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser
from scorebot.common.gameserver.GameServerBot import GameServerBot

#Standard Game Imports
from scorebot.standard.StandardConfig import FlagConfigHandler
from scorebot.standard.servicebot2.ServiceBot import ServiceBot
from scorebot.standard.servicebot2.ServiceBotConfig import ServiceBotConfigHandler, ServiceConfigHandler
from scorebot.standard.submitbot.SubmitBot import SubmitBot
from scorebot.standard.submitbot.SubmitBotConfig import SubmitBotConfigHandler
from scorebot.standard.scoreboardbot.ScoreboardBot import ScoreboardBot
from scorebot.standard.scoreboardbot.ScoreboardBotConfig import ScoreboardBotConfigHandler
from scorebot.standard.StandardCTF import StandardCTF

def main(argv):
	#Parse command line
	try:
		opts,args = getopt.gnu_getopt(argv[1:],"ic:")
	except getopt.GetoptError as err:
		print str(err)
		print "Usage..."
		sys.exit(2)

	initialize = False
	default_config_path = "config/config.ini"
	config_path = default_config_path

	for o, a in opts:
		if o == "-i":
			initialize = True
		
		elif o == "-c":
			config_path = a

		else:
			assert False, "unhandled option"

	#Setup config
	cip = ConfigIniParser()
	cip.addHandler(FlagConfigHandler())
	cip.addHandler(ServiceBotConfigHandler())
	cip.addHandler(SubmitBotConfigHandler())
	cip.addHandler(ScoreboardBotConfigHandler())
	cip.addHandler(ServiceConfigHandler())

	#Load conf file
	if(config_path == default_config_path):
		print "Using default config file",config_path

	conf = cip.load(config_path)
	
	#Temporary hack - this should be in config file..
	#conf.setFlagPhrase("flags wave in the wind")
	required_sections = [
		"FLAG",
		"SUBMIT_BOT",
		"SCOREBOARD_BOT",
		"SUBMIT_BOT",
	]
	assert(conf.isValid(required_sections)),"A required section is missing!"


	#Create Game Type
	gamelogic = StandardCTF(conf,initialize)

	try:
		#Create Game Server
		game_server_bot = GameServerBot(conf,gamelogic)
		game_server_bot.start()
		time.sleep(1)

		#Create ServiceBot
		service_bot = ServiceBot(conf,initialize)		
		service_bot.start()

		#Create SubmitBot
		submit_bot = SubmitBot(conf,initialize)
		submit_bot.start()

		#Create ScoreboardBot
		scoreboard_bot = ScoreboardBot(conf,initialize)
		scoreboard_bot.start()

		scoreboard_bot.join()
		submit_bot.join()
		service_bot.join()
		game_server_bot.join()

	except KeyboardInterrupt:
		print "Main caught keyboard interrupt"

	finally:
		print "Finally.."

if __name__ == '__main__':
	main(sys.argv)
