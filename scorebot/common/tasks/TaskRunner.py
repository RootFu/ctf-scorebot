import threading
import subprocess
import time
import os
import Queue

class LineReader(threading.Thread):
		
	def __init__(self,line_q, pipe):
		threading.Thread.__init__(self)
		self.line_q = line_q
		self.pipe = pipe

	def run(self):
		while(True):
			line = self.pipe.readline()
			self.line_q.put(line.strip())
			if(len(line) == 0): #EOF
				break

class TaskRunner(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.commandline = None
		self.cwd = None
		self.cmd_q = Queue.Queue()
		self.line_q = Queue.Queue()
		self.proc = None
		self.reader = None
		self.task_lock = threading.Lock()
		self.alive_cond = threading.Condition()

	def run(self):
		while(True):
			cmd = self.cmd_q.get()
			self.cmd_q.task_done()
			if(cmd == 'S'):
				with self.task_lock:
					try:
						self.proc = subprocess.Popen(
							self.commandline,
							stdout=subprocess.PIPE,
							stdin=None,
							stderr=subprocess.STDOUT,
							cwd=self.cwd,
							close_fds=True)
					
						self.reader = LineReader(self.line_q, self.proc.stdout)
						self.reader.start()
					except OSError:
						pass
				
				with self.alive_cond:
					self.alive_cond.notifyAll()

			if(cmd == 'H' or cmd == 'Q'):
				with self.task_lock:
					if(self.proc != None):
						if(self.proc.poll() == None):
							self.proc.kill()
						self.proc.wait()
						self.reader.join()

				with self.alive_cond:
					self.alive_cond.notifyAll()

			if(cmd == 'Q'):
				break

	def taskStart(self,commandline):
		assert(self.taskAlive() == False),"Task Already started!"
		with self.task_lock:
			self.commandline = commandline
			self.cwd = os.path.dirname(commandline[0])
			self.cmd_q.put('S')

		with self.alive_cond:
			if(self.taskAlive() == False):
				self.alive_cond.wait()
		
		return self.line_q

	def taskStop(self):
		with self.task_lock:
			self.cmd_q.put('H')

		with self.alive_cond:
			if(self.taskAlive() == True):
				self.alive_cond.wait()

	def taskAlive(self):
		with self.task_lock:
			if(self.proc == None):
				return False
			return self.proc.poll() == None
	
	def taskRetcode(self):
		with self.task_lock:
			if(self.proc == None):
				return None
			return self.proc.returncode
	
	def quit(self):
		with self.task_lock:
			self.cmd_q.put('Q')

		self.cmd_q.join()

		with self.alive_cond:
			if(self.taskAlive() == True):
				self.alive_cond.wait()
