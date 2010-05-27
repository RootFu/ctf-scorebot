#!/usr/bin/python -u

import sys
import socket
import string
import random

from utility import CtfUtil

spaminPort = 8008
spamoutPort = 8009

randAlphabet = string.ascii_letters + string.digits

headerString = "SPAM-IN-SPAM-OUT"

def score(ip,flag,cookie):  
	#get flag is spamout
	if cookie != None:
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.connect(( ip, spamoutPort ))
			s.sendall(headerString + "\n" + cookie + "\n")
                
			recvString = ""
			while True:
				data = s.recv(1)
				if not data:
					break
				recvString += data
                    
			oldFlag = recvString
			print "FLAG:",oldFlag 
			s.close()

		except Exception, e:
			print "ERROR: got exception trying to read old flag: %s" % (e)
       
	#set flag is spamin
	try:
		s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s.connect( ( ip, spaminPort ) )
		newName = "".join( [ random.choice( randAlphabet ) for i in range( 0, random.randrange( 6, 24 ) ) ] )
            
		s.sendall( headerString + "\n" + newName + "\n" + flag + "\n" )

		recvString = ""
		while True:
			data = s.recv( 1 )
			if not data:
				break
			recvString += data
    
		cookie = newName
		s.close()
        
		print "COOKIE:",cookie    
        
	except Exception, e:
		print "ERROR: got exception trying to set new flag: %s" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
