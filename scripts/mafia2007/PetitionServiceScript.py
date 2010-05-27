#!/usr/bin/python -u

"""

http://<server>/~petition/cgi-bin/petition.py?first=john&last=doe&email=john@doe.com&comment=<flag>&id=

This stores a new flag and generate an ID

http://<server>/~petition/cgi-bin/petition.py?first=&last=&email=&comment=&id=<id>

This will print the stored flag, given the ID


"""

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie): 
	# get old flag
	retFlag = None
        
	if cookie != "":
		try:
			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/Site/Petition.html")
			mainpg.open()
			mainpg = pybrowse.Browser("http://" + ip + "/Site//Petition_files/widget1_markup.html")
			mainpg.open()
			mainpg.parse()
 
			adminForm = mainpg.forms[0]
			adminForm.fields["comment"] = "" 
			adminForm.fields["id"]  = cookie
			resultingPage = adminForm.click( None )
			resultingPage = resultingPage.doRedirects()
			successPtr = resultingPage.page.find("Your comment was:")
			if successPtr != -1:
				oldFlag = resultingPage.page[successPtr+18:][:len(flag)]
				print "FLAG:",oldFlag
                
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
        
	# set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/Site/Petition.html")
		mainpg.open()
		mainpg = pybrowse.Browser("http://" + ip + "/Site//Petition_files/widget1_markup.html")
		mainpg.open()
		mainpg.parse()

		myform = mainpg.forms[0]
		myform.fields["first"] = CtfUtil.getRandomString(random.randint(4,10))
		myform.fields["last"] = CtfUtil.getRandomString(random.randint(4,10))
		myform.fields["email"] = CtfUtil.getRandomEmail()
		myform.fields["comment"] = flag

		myform.fields["id"] = ""
		resultingPage = myform.click(None)
		resultingPage = resultingPage.doRedirects()
		successPtr = resultingPage.page.find( "Your ID is " )
        
		if successPtr != -1:
			cookie = resultingPage.page[successPtr+11:][:8]
			print "COOKIE:",cookie
        
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)
       
if __name__ == "__main__":
	CtfUtil.main(score) 
