#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def getNotePage(ip,user,email, note):
	personality = browserpersonality.getRandomPersonality()
	mainpg = pybrowse.Browser("http://" + ip + ":10080/", personality)
	mainpg.open()
	mainpg.parse()
        
	noteForm = mainpg.forms[0]
        
	noteForm.fields['user'] = user
	noteForm.fields['email'] = email
	noteForm.fields['note'] = note
        
	return noteForm.click(None)
        
def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			user,email = cookie.split(":")
			resultPage = getNotePage(ip,user,email,CtfUtil.getRandomString(random.randint(5,10)))
                                
			successPtr = resultPage.page.find("NOTE:")

			if successPtr != -1:
				endPointer = resultPage.page[successPtr+6:].find("\n")
				oldFlagText = resultPage.page[successPtr+6:][:endPointer]
				oldFlag = urllib.unquote(oldFlagText)[:len(flag)]
				print "FLAG:",oldFlag
     
		except Exception, e:
			print "ERROR: got exception %s setting new flag" % (e)
			sys.exit(1)
         
	#set the new flag
	try:
		user = CtfUtil.getRandomString(random.randint(6,8))
		email = CtfUtil.getRandomEmail()
		note = flag
            
		resultPage = getNotePage(ip,user,email,note)
            
		successPtr = resultPage.page.find("Annotation saved!")
		if successPtr == -1:
			return
            
		cookie = user+":"+email
		print "COOKIE:",cookie
            
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)
        
if __name__ == "__main__":
	CtfUtil.main(score) 
