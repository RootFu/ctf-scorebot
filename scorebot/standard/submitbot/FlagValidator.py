import time
import threading

from scorebot.common.models.Flag import FlagManager, Flag
from scorebot.config.Config import Config

class SubmissionRecord:

	def __init__(self,teamId,duration):
		self.teamId = teamId
		self.flag_records = []
		self.duration = duration
		self.lock = threading.Lock()

	def compareFlags(self,a,b):
		return a.round == b.round and a.teamId == b.teamId and a.serviceId == b.serviceId

	def verifyUnique(self,newflag,now):
		with self.lock:
			new_records = []
			result = True

			for flag in self.flag_records:
				if(self.compareFlags(flag,newflag) == True):
					result = False

				if(now - flag.timestamp <= self.duration):
					new_records.append(flag)

			if(result == True):
				new_records.append(newflag)

			self.flag_records = new_records
			return result

class FlagValidator:

	VALID = 0
	SAME_TEAM = 1
	EXPIRED = 2
	REPEAT = 3

	def __init__(self,num_teams,duration):
		self.records = []
		self.duration = duration
		for i in xrange(num_teams):
			self.records.append(SubmissionRecord(i,self.duration))

	def validate(self,submitterTeamId,flag):
		now = time.time()

		if(submitterTeamId == flag.teamId):
			return self.SAME_TEAM

		if(now - flag.timestamp > self.duration):
			return self.EXPIRED

		if(self.records[submitterTeamId].verifyUnique(flag,now) == False):
			return self.REPEAT

		return self.VALID
