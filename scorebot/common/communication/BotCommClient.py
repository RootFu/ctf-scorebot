import asyncore,asynchat
import socket
import threading
import Queue
import time

from scorebot.common.communication import BotMessage

class ClientHello(BotMessage.BotMessage):

	def __init__(self,name):
		BotMessage.BotMessage.__init__(self,"CLIENT_HELLO",name)

class BotClientDispatcher(asynchat.async_chat):

	def __init__(self,comm):
		asynchat.async_chat.__init__(self)
		self.set_terminator("\n\n")
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.comm = comm
		self.data = ""

	def establish(self,server,port):
		self.connect((server,port))

	def handle_connect(self):
		pass

	def collect_incoming_data(self,data):
		self.data += data
		
	def found_terminator(self):
		#self.comm.msg_output_q.put(self.data)
		self.comm.updateOutputQ(self.data)
		self.data = ""

class BotCommClient(threading.Thread):

	def __init__(self,server,port,key,iv,client_type):
		threading.Thread.__init__(self)
		self.msg_input_q = Queue.Queue(100)
		self.msg_output_q = Queue.Queue(100)
		self.request_buffer = Queue.Queue(100)

		self.map = {}
		self.dispatcher = BotClientDispatcher(self)

		self.server = server
		self.port = port
		self.key = key
		self.iv = iv
		self.client_type = client_type

		self.alive = True
		self.alive_lock = threading.Lock()
		self.recv_lock = threading.Lock()
		self.send_lock = threading.Lock()
		self.init_cond = threading.Condition()
		self.msg_arrival_cond = threading.Condition()

		self.initialized = False
		self.send_seq = 0
		self.recv_seq = 0

	def protocolInit(self):
		with self.init_cond:
			asyncore.loop(timeout=1,count=2,map=self.map)
			if(self.msg_output_q.empty() == False):
				msg = self.msg_output_q.get(self)
				obj = BotMessage.fromTxt(self.key,self.iv,self.recv_seq,msg)
				self.recv_seq += 1
				if(obj.type == "SET_IV"):
					self.iv = obj.data
					hello = ClientHello(self.client_type)
					txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,hello)
					self.msg_input_q.put(txt)
					self.send_seq += 1
					self.initialized = True
					self.init_cond.notifyAll()
				else:
					assert("Failed to set IV")
			else:
				assert("Server did not send initial message!")

	def run(self):
		self.dispatcher.establish(self.server,self.port)
		self.dispatcher.add_channel(self.map)

		self.protocolInit()

		while(True):
			with self.alive_lock:
				if(self.alive == False):
					return
			while(not self.msg_input_q.empty()):
				msg = self.msg_input_q.get(False)
				self.dispatcher.push(msg+self.dispatcher.terminator)

			asyncore.loop(timeout=0.05,count=1,map=self.map)

	def send(self,msg):
		with self.init_cond:
			if(self.initialized == False):
				self.init_cond.wait()

		with self.send_lock:
			txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,msg)
			self.send_seq += 1
			self.msg_input_q.put(txt)

	def receive(self,block=True,timeout=None):
		with self.init_cond:
			if(self.initialized == False):
				self.init_cond.wait()

		if(self.request_buffer.empty() == False):
			return self.request_buffer.get(block,timeout)

		try:	
			msg = self.msg_output_q.get(block,timeout)
		except Queue.Empty:
			return None

		with self.recv_lock:
			obj = BotMessage.fromTxt(self.key,self.iv,self.recv_seq,msg)
			self.recv_seq += 1
		
		return obj

	def sendResponse(self,orig_msg,resp_msg):
		with self.init_cond:
			if(self.initialized == False):
				self.init_cond.wait()

		with self.send_lock:
			resp = BotMessage.BotMessage(
				resp_msg.type,resp_msg.data,BotMessage.BotMessage.RESP,orig_msg.req_id)
			txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,resp)
			self.send_seq += 1
			self.msg_input_q.put(txt)

	def request(self,msg,timeout=None):

		start_time = time.time()

		req_id = self.send_seq
		req_msg = BotMessage.BotMessage(msg.type,msg.data,BotMessage.BotMessage.REQ,req_id)

		with self.init_cond:
			if(self.initialized == False):
				self.init_cond.wait()

		with self.send_lock:
			txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,req_msg)
			self.send_seq += 1
			self.msg_input_q.put(txt)

		while(True):
			with self.msg_arrival_cond:
				if(self.msg_output_q.empty()):
					self.msg_arrival_cond.wait(timeout)
				
				with self.recv_lock:
					if(self.msg_output_q.empty() == False):

						msg = self.msg_output_q.get(False)
						obj = BotMessage.fromTxt(self.key,self.iv,self.recv_seq,msg)
						self.recv_seq += 1

						if(obj.req_type == BotMessage.BotMessage.RESP and obj.req_id == req_id):
							return obj
						else:
							self.request_buffer.put(obj,True,timeout)
					
					#Check the buffer for the desired message
					result = None
					tmp = []
					while(self.request_buffer.empty() == False):
						obj = self.request_buffer.get()
						if(obj.req_type == BotMessage.BotMessage.RESP and obj.req_id == req_id):
							result = obj
							break
						else:
							tmp.append(obj)

					for obj in tmp:
						self.request_buffer.put(obj,True)

					if(result == None and (time.time() - start_time) < timeout):
						continue

					return result
						
		"""
		with self.send_lock:
			with self.recv_lock:
				txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,msg)
				self.send_seq += 1
				self.msg_input_q.put(txt)
				
				while(True):
					try:	
						msg = self.msg_output_q.get(True,timeout)
						obj = BotMessage.fromTxt(self.key,self.iv,self.recv_seq,msg)
						self.recv_seq += 1

						if(obj.type == response_type):
							return obj
						else:
							self.request_buffer.put(obj,True,timeout)

					except Queue.Empty:
						return None
		"""

	def getPendingMessages(self,timeout=0.05):
		with self.init_cond:
			if(self.initialized == False):
				self.init_cond.wait()
		
		if(self.request_buffer.empty() == False):
			return self.request_buffer.get(block,timeout)
		else:
			return None

	def updateOutputQ(self,data):
		with self.msg_arrival_cond:
			self.msg_output_q.put(data)
			self.msg_arrival_cond.notifyAll();

	def kill(self):
		with self.alive_lock:
			self.alive = False

