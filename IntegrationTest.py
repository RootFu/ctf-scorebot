from multiprocessing import Process

import sys
import time

#Common Imports
from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser
from scorebot.common.gameserver.GameServerBot import GameServerBot

#Standard Game Imports
from scorebot.standard.servicebot2.ServiceBot import ServiceBot
from scorebot.standard.servicebot2.ServiceBotConfig import ServiceBotConfigHandler, ServiceConfigHandler
from scorebot.standard.submitbot.SubmitBot import SubmitBot
from scorebot.standard.scoreboardbot.ScoreboardBot import ScoreboardBot
from scorebot.standard.StandardCTF import StandardCTF

#Attack Engine Imports
from scorebot.attackengine.attackbot.AttackBot import AttackBot
from scorebot.attackengine.flagsubmissionbot.FlagSubmissionBot import FlagSubmissionBot
#from scorebot.attackengine.collectbot.CollectBot import CollectBot
from scorebot.attackengine.AttackEngineLogic import AttackEngineLogic

def main(argv):

	if(len(argv) != 2):
		print "Usage: %s [standard or attack]" % argv[0]
		return

	if(argv[1] == "standard"):
		mainStandard()
		return

	if(argv[1] == "attack"):
		mainAttack()
		return

def mainAttack():
	#Load conf file
	test_config_path = "config/attack_test.ini"
	conf = ConfigIniParser().load(test_config_path)
	assert(conf.isValid())

	#Create Game Type
	attacklogic = AttackLogic(conf)

	#Create GameStateBot
	game_state_bot = GameStateBot(conf,attacklogic)
	game_state_bot.start()

	time.sleep(1)

	#Create AttackBot
	attack_bot = AttackBot(conf,True)
	attack_bot.start()

	attack_bot.join()
	game_state_bot.join()
	"""
	#Create FlagSubmissionBot
	flag_submission_bot = FlagSubmissionBot(conf,True)
	flag_submission_bot.start()

	#Create CollectBot
	collect_bot = CollectBot(conf,True)
	collect_bot.start()

	collect_bot.join()
	flag_submission_bot.join()
	attack_bot.join()
	game_state_bot.join()
	"""
	
def mainStandard():

	#Setup config
	cip = ConfigIniParser()
	cip.addHandler(ServiceBotConfigHandler())
	cip.addHandler(ServiceConfigHandler())

	#Load conf file
	test_config_path = "config/integration_test.ini"
	conf = cip.load(test_config_path)
	
	#Temporary hack - this should be in config file..
	conf.setFlagPhrase("flags wave in the wind")

	assert(conf.isValid())

	#Create Game Type
	gamelogic = StandardCTF(conf,True)

	try:
		#Create Game Server
		game_server_bot = GameServerBot(conf,gamelogic)
		game_server_bot.start()
		time.sleep(1)

		#Create ServiceBot
		service_bot = ServiceBot(conf,True)		
		service_bot.start()

		#Create SubmitBot
		submit_bot = SubmitBot(conf,True)
		submit_bot.start()

		#Create ScoreboardBot
		scoreboard_bot = ScoreboardBot(conf,True)
		scoreboard_bot.start()

		submit_bot.join()
		service_bot.join()
		game_server_bot.join()

	except KeyboardInterrupt:
		print "Integration test caught keyboard interrupt"

	finally:
		print "Finally.."

if __name__ == '__main__':
	main(sys.argv)
