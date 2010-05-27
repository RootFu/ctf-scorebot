#!/usr/bin/python -u
import socket
import random

from utility import pybrowse, browserpersonality, CtfUtil


def sendMessage(ip, message):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, 11111))
	s.send(message)

	response = s.recv(1024)
	s.close()

	return response

def score(ip,flag,cookie):
	#get old flag
	if cookie != None:
		try:
			name = cookie
			msg = "DICT " + name + "\n"
			response = sendMessage(ip,msg)
			print "FLAG:",response
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:  
		name = CtfUtil.getRandomString(random.randint(6,8))
		msg = "STORE "+name+" " + flag + "\n"    
		response = sendMessage(ip,msg)

		successPtr = response.find("included in")
		if successPtr == -1:
			print "Could not set new flag"
			return

		cookie = name
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
