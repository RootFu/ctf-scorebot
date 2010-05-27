class Scoring():

	def updateOffensiveInfo(self,submit_results):
		assert(False)

	def updateDefensiveInfo(self,round,defensive_data):
		assert(False)

	def updateRoundScores(self):
		assert(False)

"""
1 point for every flag captured
1 point for every service which had no
flags captured this round
"""
class BasicScoring():

	def __init__(self,conf):
		self.round = 1
		self.conf = conf
		self.logger = conf.buildLogger("BasicScoring")
		self.servicebot_conf = conf.getSection("SERVICE_BOT")
		self.round_def_data = None

		self.team_def_scores = []
		self.team_off_scores = []
		self.was_hacked = []

		for teamId in xrange(self.conf.numTeams()):

			self.team_def_scores.append(0)
			self.team_off_scores.append(0)
			self.was_hacked.append([])

			for serviceId in xrange(self.servicebot_conf.numServices()):
				self.was_hacked[teamId].append(False)
			
	def updateOffensiveInfo(self,offensive_data):
		for hackerId,flag in offensive_data:
			self.team_off_scores[hackerId] += 1
			self.was_hacked[flag.teamId][flag.serviceId] = True

	def updateDefensiveInfo(self,defensive_data):
		assert(self.round_def_data == None)
		self.round_def_data = defensive_data

	def updateRoundScores(self,round):
		assert(self.round_def_data != None)
		assert(self.round == round)

		self.logger.info("=== Scores for round %d ===" % self.round)

		for teamId in xrange(self.conf.numTeams()):
			for serviceId in xrange(self.servicebot_conf.numServices()):

				if(self.was_hacked[teamId][serviceId] == True):
					self.was_hacked[teamId][serviceId] = False
					continue

				status = self.round_def_data[teamId][serviceId]
				if(status == 'g' or (status == 'b' and self.round == 1)):
					self.team_def_scores[teamId] += 1
				
			team_name = self.conf.getTeamInfoById(teamId).name
			self.logger.info("%r: off=%d def=%d" % (
				team_name,self.team_off_scores[teamId],self.team_def_scores[teamId]))

		self.round_def_data = None
		self.round += 1

		return self.team_off_scores,self.team_def_scores
