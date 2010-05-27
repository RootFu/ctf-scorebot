#!/usr/bin/python -u

import socket
import random
import string
from utility import pybrowse, browserpersonality, CtfUtil
port = 1969


def sendMessage(ip, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	sock.send(message)
	sock.shutdown(1)

	response = ""
	msg = ""
	while(True):
		msg = sock.recv(1024)
		if(not msg):
			break
		response += msg

	sock.close()
	return response


def encrypt(msg):
	key = 'F2654hD4'
	encrypted_message = ""
	for i in range(0,len(msg)):
		encrypted_message += "%02X" % (ord(key[i%len(key)])^ord(msg[i]))
	return encrypted_message

def decrypt(msg):
	key = 'F2654hD4'
	count = 0
	decrypted_message = ""
	for i in range(0,len(msg),2):
		decrypted_message +=  chr(int(msg[i]+msg[i+1],16) ^ ord(key[count%len(key)]))
		count += 1
	return decrypted_message

def score(ip,flag,cookie):
	#get old flag
	if cookie != None:
		try:
			wwid = cookie
			vote = CtfUtil.getRandomString(random.randint(5,10))

			response = sendMessage(ip,encrypt("!"+wwid+" "+vote))
			successPtr = response.find("OK")
			if successPtr != -1:
				oldFlag = decrypt(response[successPtr+3:].strip())
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:  
		wwid = CtfUtil.getRandomString(random.randint(6,8))
		vote = flag

		response = sendMessage(ip,encrypt("!"+wwid+" "+vote))

		successPtr = response.find("OK")
		if successPtr == -1:
			print "ERROR: Could not post new flag"
			return

		cookie = wwid
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
