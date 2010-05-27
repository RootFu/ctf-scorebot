#!/usr/bin/python -u

import socket
import random
import sys

from utility import pybrowse, browserpersonality, CtfUtil

port = 6666

def getData(sock, text):
	try:
		response = ""
		while(True):
			response += sock.recv(1024)
			if(response.find(text) != -1):
				break     
		return response

	except Exception, e:
		print "ERROR: got exception %s reading data from server" % (e)
		sys.exit(1)
    
def parseId(text):
	try:
		ptr = text.find("Bas-ID is:")
		id = text[ptr+11:]
		return id.split("\n")[0]

	except Exception, e:
		print "ERROR: got exception %s parseing id" % (e)
		sys.exit(1)
    
def parseFlag(text,flag):
	try:
		ptr = text.find("Your report:")
		flag = text[ptr+13:][:len(flag)]
		return flag.strip()

	except Exception, e:
		print "ERROR: got exception %s parseing flag" % (e)
		sys.exit(1)
                
    
def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			id = cookie
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((ip, port))

			sock.send("2\n")
			getData(sock,"lookup:")
			sock.send(id+"\n")
			flagText = getData(sock,"continue")
			oldFlag = parseFlag(flagText,flag)
			print "FLAG:",oldFlag     
			sock.send("\n")
			getData(sock,"return:")
            
			#exit
			sock.send("9\n")
			getData(sock,"!")
                
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
        
	#set the new flag
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip, port))
              
		getData(sock,"return:")
		sock.send("1\n")
		getData(sock,"return:")
		sock.send(str(random.randint(1,8))+"\n")
		getData(sock,"alias:")
		sock.send(CtfUtil.getRandomString(random.randint(6,8))+"\n")
            
		#Number of something
		getData(sock,":")
		sock.send(str(random.randint(1,100))+"\n")
            
		#Encrypted report
		getData(sock,":")
		sock.send(flag+"\n")
            
		idText = getData(sock,"continue")
		id = parseId(idText)

		sock.send("\n")
		getData(sock,"return:")
           
		#exit
		sock.send("9\n")
		getData(sock,"!")
            
		cookie = id
		print "COOKIE:",cookie
 
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
