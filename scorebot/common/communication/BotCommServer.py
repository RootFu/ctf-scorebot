import asyncore,asynchat
import socket
import random

from scorebot.common.communication import BotMessage
from scorebot.common.gameserver.GameStateLogic  import GameStateLogic 

class SetIVBotMessage(BotMessage.BotMessage):

	def __init__(self):
		new_iv = "".join(map(chr,map(random.randint,[0]*8,[255]*8)))
		BotMessage.BotMessage.__init__(self,"SET_IV",new_iv)

class BotServerDispatcher(asynchat.async_chat):

	def __init__(self, conn, key, iv, gamelogic):
		asynchat.async_chat.__init__(self,conn)
		self.gamelogic = gamelogic
		self.set_terminator("\n\n")
		self.data = ""
		self.key = key
		self.iv = iv
		self.send_seq = 0
		self.recv_seq = 0
		iv_msg = SetIVBotMessage()
		self.sendMsg(iv_msg)
		self.iv = iv_msg.data

	def collect_incoming_data(self,data):
		self.data += data
	
	def found_terminator(self):
		msg = BotMessage.fromTxt(self.key,self.iv,self.recv_seq,self.data)
		self.recv_seq += 1
		self.data = ""
		self.gamelogic.handleBotMessage(msg,self) 

	def sendMsg(self,obj):
		txt = BotMessage.toTxt(self.key,self.iv,self.send_seq,obj)
		self.send_seq += 1
		self.push(txt+self.terminator)

class BotCommServer(asyncore.dispatcher):

	def __init__(self,port,key,iv,gamelogic):
		asyncore.dispatcher.__init__(self)
		self.key = key
		self.iv = iv

		self.gamelogic = gamelogic
		self.gamelogic.setup(self)

		self.shutdown = 0
		self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(("",port))
		self.listen(5)

	def handle_close(self):
		self.close()

	def handle_accept(self):
		conn,addr = self.accept()
		BotServerDispatcher(conn,self.key,self.iv,self.gamelogic)
