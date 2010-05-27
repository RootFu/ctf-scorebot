#!/usr/bin/env python

import sys
import time

from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser
from scorebot.servicebot.ServiceBot import ServiceBot
from scorebot.attackengine.attackbot.AttackBot import AttackBot
from scorebot.gamestatebot.GameStateBot import GameStateBot

from scorebot.gamelogic.usenix.UsenixLogic import UsenixLogic
from scorebot.gamelogic.usenix.UsenixPublicLogic import UsenixPublicLogic
from scorebot.gamelogic.usenix.UsenixConfig import UsenixExploitConfigHandler
from scorebot.gamelogic.usenix.UsenixConfig import UsenixConfigHandler
from scorebot.gamelogic.usenix.usenixexploitbot.UsenixExploitBot import UsenixExploitBot
from scorebot.gamelogic.usenix.usenixreportbot.UsenixReportBot import UsenixReportBot
from scorebot.servicebot.ServiceBotConfig import ServiceBotConfigHandler, ServiceConfigHandler
#from scorebot.attackengine.attackbot.AttackConfig import AttackConfigHandler

def usage(argv):
	return "Usage: %s [all server service scoreboard public] [init]" % argv[0]
 
def checkInit():
	ans = raw_input("Are you sure you want to reinitialize the game? ")
	if(ans.upper().startswith("Y")):
		return True
	return False

def startBot(bot,init):
	if(bot == "all"):
		startAll(init)

	elif(bot == "public"):
		startPublic(init)

	elif(bot == "server"):
		print "Start Server!",init

	elif(bot == "attack"):
		print "Start Attack!",init

	elif(bot == "scoreboard"):
		print "Start Scoreboard!",init

	else:
		print usage(sys.argv)

def startPublic(init):
	cip = ConfigIniParser()
	cip.addHandler(ServiceBotConfigHandler())
	cip.addHandler(ServiceConfigHandler())
	cip.addHandler(UsenixConfigHandler())

	config_path = "config/usenix_public.ini"
	conf = cip.load(config_path)
	conf.setFlagPhrase("flags wave in the wind")
	
	assert(conf.isValid())

	#Create Game Logic
	usenixlogic = UsenixPublicLogic(conf,init)

	#Create GameStateBot
	game_state_bot = GameStateBot(conf,usenixlogic)
	game_state_bot.start()

	time.sleep(1)
	
	#Create ServiceBot
	servicebot = ServiceBot(conf,init)
	servicebot.start()

	#Create UsenixReportBot
	reportbot = UsenixReportBot(conf,8081)
	reportbot.start()

	servicebot.join()
	reportbot.join()
	game_state_bot.join()

def startAll(init):

	#Setup config
	cip = ConfigIniParser()
	cip.addHandler(ServiceBotConfigHandler())
	cip.addHandler(ServiceConfigHandler())
	cip.addHandler(UsenixConfigHandler())
	cip.addHandler(UsenixExploitConfigHandler())
	#cip.addHandler(AttackConfigHandler(False))
	
	#Load conf file
	config_path = "config/usenix.ini"
	conf = cip.load(config_path)

	#Temporary hack - this should be in config file..
	conf.setFlagPhrase("flags wave in the wind")
	
	assert(conf.isValid())

	#Create Game Logic
	usenixlogic = UsenixLogic(conf,init)

	#Create GameStateBot
	game_state_bot = GameStateBot(conf,usenixlogic)
	game_state_bot.start()

	time.sleep(1)

	#Create ServiceBot
	servicebot = ServiceBot(conf,init)
	servicebot.start()
	
	#Create Scoreboard

	#Create UsenixExploitBot
	usenix_exploit_bot = UsenixExploitBot(conf,init)
	usenix_exploit_bot.start()

	#Create UsenixReportBot
	reportbot = UsenixReportBot(conf,8082)
	reportbot.start()

	reportbot.join()
	usenix_exploit_bot.join()
	servicebot.join()
	game_state_bot.join()

def main(argv):
	if(len(argv) == 2):
		startBot(argv[1],False)

	elif(len(argv) == 3):
		if(argv[2] == "init"):
			if(checkInit()):
				startBot(argv[1],True)
			else:
				print "Not going to do anything..."
				return
		else:
			print usage(argv)

	else:
		print usage(argv)

if __name__ == "__main__":
	main(sys.argv)
