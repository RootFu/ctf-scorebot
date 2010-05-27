from multiprocessing import Process

import sys
import time

from scorebot.config.Config import Config
from scorebot.config.ConfigIniParser import ConfigIniParser

from scorebot.attackengine.attackbot.AttackBot import AttackBot
from scorebot.attackengine.webbot.WebBot import WebBot
from scorebot.attackengine.flagsubmissionbot.FlagSubmissionBot import FlagSubmissionBot

from scorebot.attackengine.AttackEngineLogic import AttackEngineLogic
from scorebot.attackengine.attackbot.AttackConfig import AttackConfigHandler

from scorebot.common.gamestatebot.GameStateBot import GameStateBot

flag_submission_bot = None

def main(argv):
	global flag_submission_bot

	if(len(argv) != 2):
		print "Usage: %s [all attack submission]" % argv[0]
		return

	#Load conf file
	config_path = "config/ructfe.ini"
	cip = ConfigIniParser()
	cip.addHandler(AttackConfigHandler(True))
	conf = cip.load(config_path)
	print conf
	assert(conf.isValid())

	#Create Game Type
	if(argv[1] == "all" or argv[1] == "attack"):
		attacklogic = AttackEngineLogic(conf)

		#Create GameStateBot
		game_state_bot = GameStateBot(conf,attacklogic)
		game_state_bot.start()

		time.sleep(1)

		#Create AttackBot
		attack_bot = AttackBot(conf,True)
		attack_bot.start()

		#Create WebBot
		web_bot = WebBot(conf,True)
		web_bot.start()
		print "All Started.."

	if(argv[1] == "all" or argv[1] == "submission"):
		#Create FlagSubmissionBot
		flag_submission_bot = FlagSubmissionBot(conf,True)
		print "Flag started"
		flag_submission_bot.start()
		flag_submission_bot.join()

	game_state_bot.join()
	attack_bot.join()
	web_bot.join()
	
if __name__ == '__main__':
	try:
		main(sys.argv)
	except KeyboardInterrupt:
		if(sys.argv[1] == "submission"):
			flag_submission_bot.terminate()
