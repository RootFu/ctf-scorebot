from multiprocessing import Process
import threading

from scorebot.common.communication.BotCommClient import BotCommClient
from scorebot.common.communication.BotMessage import BotMessage

from scorebot.standard.scoreboardbot.ScoreboardWebserver import ScoreboardWebserver

class ScoreboardServerThread(threading.Thread):

	def __init__(self,port):
		threading.Thread.__init__(self)
		self.scoreboard_server = ScoreboardWebserver(port)
		
	def run(self):
		self.scoreboard_server.serve_forever()

	def quit(self):
		self.scoreboard_server.quit()

	def updateScoreText(self,text):
		self.scoreboard_server.updateScoreText(text)

class ScoreboardBot(Process):

	def __init__(self,conf,init=False):
		Process.__init__(self)
		self.conf = conf
		self.servicebot_conf = self.conf.getSection("SERVICE_BOT")
		self.scoreboard_conf = self.conf.getSection("SCOREBOARD_BOT")

		self.comm = None
		self.init = init
		self.logger = conf.buildLogger("ScoreboardBot")

	def run(self):

		server_info = self.conf.getGameStateServerInfo()
		self.comm = BotCommClient(
			server_info.host,
			server_info.port,
			server_info.key,
			server_info.iv,
			"SCOREBOARD_BOT")

		self.comm.start()

		self.server = ScoreboardServerThread(self.scoreboard_conf.port)

		default_text = self.__genDefaultTable()
		self.server.updateScoreText(default_text)
		self.server.start()

		while(True):
			msg = self.comm.receive()
			assert(msg.type == "UPDATE_SCORES")
			team_off_scores,team_def_scores,service_status = msg.data

			assert(len(team_off_scores) == self.conf.numTeams())
			assert(len(team_def_scores) == self.conf.numTeams())
			assert(len(service_status) == self.conf.numTeams())

			table_text = self.__genScoreTable(team_off_scores,team_def_scores,service_status)
			self.server.updateScoreText(table_text)

	def __genDefaultTable(self):
		team_off_scores = []
		team_def_scores = []
		service_status = []

		for i in xrange(self.conf.numTeams()):
			team_off_scores.append(0)
			team_def_scores.append(0)
			service_status.append([])
			for j in xrange(self.servicebot_conf.numServices()):
				service_status[i].append('g')

		return self.__genScoreTable(team_off_scores,team_def_scores,service_status)

	def __genScoreTable(self,team_off_scores,team_def_scores,service_status):

		table_text = "<table border=1>"

		table_header = "<tr><th>Team</th><th>Offensive</th><th>Defensive</th>"
		for i in xrange(self.servicebot_conf.numServices()):
			service_info = self.servicebot_conf.getServiceInfoById(i)
			table_header += "<th>%s</th>" % service_info.name
		table_header += "</tr>"
		table_text += table_header
	
		for i in xrange(self.conf.numTeams()):
			team_info = self.conf.getTeamInfoById(i)
			table_row = "<tr>"
			table_row += "<td>%s</td>" % team_info.name
			table_row += "<td>%s</td>" % team_off_scores[i]
			table_row += "<td>%s</td>" % team_def_scores[i]
			
			for j in xrange(self.servicebot_conf.numServices()):
				if(service_status[i][j] == 'g'):
					table_row += "<td class='status_good'>Good</td>"

				elif(service_status[i][j] == 'b'):
					table_row += "<td class='status_bad'>Bad Flag</td>"

				else:
					table_row += "<td class='status_error'>Error</td>"

			table_row += "</tr>"
			table_text += table_row

		table_text += "</table>"
		return table_text

