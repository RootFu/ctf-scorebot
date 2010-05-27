#!/usr/bin/python -u

"""
https://<server>:4443/login? user=myname&password=miconsenta&operation=OP-store
this will "touch" the file "myname" and allow for the actual storing  of the flag which is done by
https://<server>:4443/store? filename=flagfile&content=flagcontent&user=myname

(note: the order of the parameters is IMPORTANT!)

To retrieve the file:
echo "flagfile" | nc -u <server> 2345

which will return
https://<server>:4443/flagfile
+flagcontent
"""

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil


#service ports
httpPort = 80
udpPort   = 2345

#constant form values
myPassword  = "miconsenta"
myOperation = "OP-store"
    
#timeout
udpResponseTimeout = 5

def score(ip,flag,cookie):      
	#get old flag
	if cookie != None:
		try:
			(uname, pwd) = cookie.split(':')
			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/~spamgen/cgi-bin/spamgen.py?action=read", personality, debug=0)
			mainpg.open()
			mainpg.parse()
                
			adminForm = mainpg.forms[0]
			adminForm.fields["uname"] = uname 
			adminForm.fields["pwd"]  = pwd
                
			resultingPage = adminForm.click(None)
			resultingPage = resultingPage.doRedirects( )
                
			successPtr = resultingPage.page.find( "</h3>" )
                
			if successPtr != -1:
				oldFlag = resultingPage.page[successPtr+6:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "Error got exception %s getting flag" % (e)
        
	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/~spamgen/cgi-bin/spamgen.py?action=upload", personality, debug=0)
		mainpg.open()
		mainpg.parse()
         
		randomName = CtfUtil.getRandomString(10)

		adminForm = mainpg.forms[0]
		adminForm.fields["uname"] = randomName
		adminForm.fields["pwd"]  = myPassword
		adminForm.fields["thetext"] = flag
        
		resultingPage = adminForm.click(None)
		resultingPage = resultingPage.doRedirects()
        
		failPtr = resultingPage.page.find("uccess")
        
		if failPtr != -1:
			successPtr = resultingPage.page.find( "Your file has been saved" )
        
		cookie = randomName+':'+myPassword
		print "COOKIE:",cookie
    
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
