class GameStateServerInfo:

	def __init__(self,host,port,key,iv):
		assert(len(key) == 16)
		assert(len(iv) == 8)
		self.host = host
		self.port = port
		self.key = key
		self.iv = iv
