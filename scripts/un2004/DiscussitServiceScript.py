#!/usr/bin/python -u
import socket
import random

from utility import pybrowse, browserpersonality, CtfUtil
port = 7413

def initConversation(message, sock):
	sock.send(message)
	response = ""
	msg = ""
	while(True):
		response += sock.recv(1024)
		if(response.find("else!") != -1):
			break

	return response

def askRandomQuestion(sock):
	start = ["How ","What ","Why ", "Where " , "When ", "Cows "]
	middle = ["is ", "are ", "were ", "was ", "come ", "over ", "long ", "Cows "]
	end = ["beer", "life", "Cows", "people", "the moon", "the game", "the weather", "binary"]

	filler = ["great ", "good ", "some ", "all ", "bad ", "tall ", "", "", "", ""]
	period = ["?\n","!\n",".\n"]

	msg = random.choice(start) + random.choice(middle) + random.choice(filler) + random.choice(end) + random.choice(period)
	sock.send(msg)
	return sock.recv(1024)

def score(ip,flag,cookie):
	#get old flag
	if cookie != None:
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((ip, port))

			name = cookie
			topic = CtfUtil.getRandomAlphaNum(random.randint(3,8))
			msg = name+" " + topic + "\n" 

			response = initConversation(msg,sock)
			successPtr = response.find("Last time")

			if successPtr != -1:
				oldFlag = response[successPtr+32:][:len(flag)]
				print "FLAG:",oldFlag
			sock.close()

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:  
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip, port))

		name = CtfUtil.getRandomString(random.randint(6,8))
		msg = name+" " + flag + "\n"    
		response = initConversation(msg,sock)

		successPtr = response.find("summoning operator")
		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		for i in range(random.randint(1,3)):
			if len(askRandomQuestion(sock)) < 1:
				print "ERROR: Something doesnt look right"
				return

		sock.close()
		cookie = name
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
