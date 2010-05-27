class UsenixPrivateScoring:

	def __init__(self,conf):
		self.conf = conf
		self.servicebot_conf = self.conf.getSection("SERVICE_BOT")		
		self.logger = self.conf.buildLogger("UsenixPrivateScoring")

		self.sla = []
		for i in xrange(self.conf.numTeams()):
			self.sla.append([0.0]*self.servicebot_conf.numServices())

	def updateRoundResults(self,service_results):
		round,service_stats = service_results
		assert(len(service_stats) == self.conf.numTeams())
		
		for teamId in xrange(self.conf.numTeams()):
			team_stats = service_stats[teamId]
			team = self.conf.getTeamInfoById(teamId)
			for serviceId in xrange(self.servicebot_conf.numServices()):
				service = self.servicebot_conf.getServiceInfoById(serviceId)
				if(team_stats[serviceId] == 'g'):
					self.sla[teamId][serviceId] += 1.0
				self.logger.debug("Team=%s Service=%s stat=%s raw_sla=%f" % (
					team.name,service.name,
					team_stats[serviceId],self.sla[teamId][serviceId]))
	
	def getServiceSLA(self,num_rounds):
		num_rounds = float(num_rounds)
		
		results = []
		for i in xrange(self.conf.numTeams()):
			results.append([0.0]*self.servicebot_conf.numServices())

		for teamId in xrange(self.conf.numTeams()):
			for serviceId in xrange(self.servicebot_conf.numServices()):
				results[teamId][serviceId] = self.sla[teamId][serviceId]/num_rounds
				self.sla[teamId][serviceId] = 0.0
	
		return results
			
class UsenixPublicScoring:

	def __init__(self,conf):
		self.conf = conf
		self.servicebot_conf = self.conf.getSection("SERVICE_BOT")
		self.scores = [0]*self.conf.numTeams()
		self.sla = [1.0]*self.conf.numTeams()
		self.round = 1

	def updateServiceResults(self,service_results):
		num_services = self.servicebot_conf.numServices()
		round,service_stats = service_results

		assert(len(service_stats) == self.conf.numTeams())
		assert(round == self.round)

		for id in xrange(self.conf.numTeams()):
			team_stats = service_stats[id]
			count = 0
			assert(len(team_stats) == self.servicebot_conf.numServices())
			for serviceId in xrange(num_services):
				if(team_stats[serviceId] == 'g'):
					count += 1.0
			round_value = count/float(num_services)
			self.sla[id] = self.sla[id] + (round_value - self.sla[id])/(float(self.round)+1.0)

		self.round += 1

	def setRound(self,round):
		self.round = round

	def setSla(self,sla):
		self.sla = sla

	def getSla(self):
		return self.sla
