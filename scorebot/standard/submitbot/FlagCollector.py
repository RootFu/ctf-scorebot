import threading

class FlagCollector:

	def __init__(self):
		self.recent_flags = []
		self.lock = threading.Lock()

	def enque(self,flag):
		with self.lock:
			self.recent_flags.append(flag)

	def collect(self):
		with self.lock:
			recent = self.recent_flags
			self.recent_flags = []
			return recent
