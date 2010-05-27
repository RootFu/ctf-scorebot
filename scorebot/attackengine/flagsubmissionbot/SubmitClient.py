class SubmitClient:

	VALID=0
	INVALID=1
	RETRY=2

	def connect(self):
		assert(False),"Overide in child class"

	def submit(self,flag):
		assert(False),"Overide in child class"

	def quit(self):
		assert(False),"Overide in child class"
