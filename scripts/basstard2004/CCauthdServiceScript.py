#!/usr/bin/python -u

import os, random, time, sys, string, re, socket
from utility import pybrowse, browserpersonality, CtfUtil
port = 12345

def getResponse(sock,msg): 
	sock.send(msg+"\n")
	response = sock.recv(1024)
	while(response.find("\r") == -1 and response.find("\n") == -1):
		response += sock.recv(1024)
 	return response.strip()
    
def initConnection(ip):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((ip, port))
	response = sock.recv(1024)
            
	while(response.find("\n") == -1):
		response += sock.recv(1024)
            
	if(response.find("+READY") == -1):
		raise Exception("Failed to receive READY message")

	return sock
        
def score(ip,flag,cookie):
	#Creating connection
	sock = None
	try:
		sock = initConnection(ip)
	except:
		print "ERROR: Could not connect"
		return
        
	#get old flag  
	if cookie != None:
		try:
 			token = cookie
			authText = getResponse(sock,"AUTH "+token)
			authPtr = authText.find("+AUTH")
                
			if(authPtr != -1):
				oldFlag = authText[authPtr+6:][:len(flag)]
				print "FLAG:",oldFlag
                
			getResponse(sock,"REVOKE " + token)              
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:       
		regText = getResponse(sock,"REG "+flag)
		tokenPtr = regText.find("+REG")
            
		if(tokenPtr == -1):
			print "ERROR: Could not post new flag"
			return
            
		token = regText[tokenPtr+5:]
            
		cookie = token
		print "COOKIE:",cookie
 
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)
       
if __name__ == '__main__':
	CtfUtil.main(score) 
