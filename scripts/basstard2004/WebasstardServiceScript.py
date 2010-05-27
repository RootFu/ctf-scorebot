#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib
from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie):
	#get old flag 
	if cookie != None:
		try:
			file = cookie
                
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.connect((ip, 2345))
                
			sock.send(file)
                
			response = ""
			while(True):
				response += sock.recv(1024)
				if(response.find("+") != -1):
					break     
                
			oldFlag = urllib.unquote_plus(response[response.find("+")+1:])
			print "FLAG:",oldFlag
 
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
        
	#set the new flag
	try:
		mainpage = pybrowse.Browser("https://" + ip + ":4443")
		mainpage.open()
		mainpage.parse()
             
		webasstardForm = mainpage.forms[0]
            
		user = CtfUtil.getRandomString(random.randint(6,8))
            
		webasstardForm.fields['user'] = user
		webasstardForm.fields['password'] = "miconsenta"
		webasstardForm.fields['operation'] = "OP-store"

		storeFilePage = webasstardForm.click(None)
            
		successPtr = storeFilePage.page.find("Filename:")
		if(successPtr == -1):
			print "ERROR: could not set new flag"
			return
            
		storeFilePage.parse()
		storeFileForm = storeFilePage.forms[0]
            
		storeFileForm.fields['filename'] = user
		storeFileForm.fields['content'] = flag
            
		resultPage = storeFileForm.click(None)
            
		successPtr = resultPage.page.find("Your file has been saved.")
		if(successPtr == -1):
			print "ERROR: could not set new flag"
			return
            
		cookie = user
		print "COOKIE:",cookie
 
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
