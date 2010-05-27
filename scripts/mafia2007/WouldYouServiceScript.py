#!/usr/bin/python -u

"""
http://<server>/~wouldyou/cgi-bin/wouldyou.py
(POST)
name=<id>&steal=<flag>

This stores a new flag under ID <id>

http://<server>/~wouldyou/cgi-bin/wouldyou.py
(POST)
name=<id>&steal=<flag>

This stores a new flag under ID <id>
and returns the value of the previous flag.

"""


import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie):
	# get old flag
	if cookie != None:
		try:
			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/Site/Would_you.html")
			mainpg.open()
			mainpg = pybrowse.Browser("http://" + ip + "/Site//Would_you_files/widget1_markup.html")
			mainpg.open()
			mainpg.parse()
    
			qForm = mainpg.forms[0]
			qForm.fields["q1"] = random.choice(("yes", "no")) 
			qForm.fields["q2"] = random.choice(("yes", "no")) 
			qForm.fields["q3"] = random.choice(("yes", "no")) 
			qForm.fields["q5"] = random.choice(("yes", "no")) 
			qForm.fields["q6"] = random.choice(("yes", "no")) 
			qForm.fields["q7"] = random.choice(("yes", "no")) 
			qForm.fields["steal"] =  flag
			qForm.fields["signature"] = cookie 
			resultingPage = qForm.click(None)
			resultingPage = resultingPage.doRedirects( )
			successPtr = resultingPage.page.find("choice was:")

			if successPtr != -1:
				print "FLAG:",resultingPage.page[successPtr+12:][:len(flag)]

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
                
	# set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/Site/Would_you.html")
		mainpg.open()
		mainpg = pybrowse.Browser("http://" + ip + "/Site//Would_you_files/widget1_markup.html")
		mainpg.open()
		mainpg.parse()
            
		qForm = mainpg.forms[0]
		qForm.fields["q1"] = random.choice(("yes", "no")) 
		qForm.fields["q2"] = random.choice(("yes", "no")) 
		qForm.fields["q3"] = random.choice(("yes", "no")) 
		qForm.fields["q5"] = random.choice(("yes", "no")) 
		qForm.fields["q6"] = random.choice(("yes", "no")) 
		qForm.fields["q7"] = random.choice(("yes", "no")) 

		cookie = CtfUtil.getRandomString(random.randint(3,10))

		qForm.fields["steal"] =  flag
		qForm.fields["signature"] = cookie
		resultingPage = qForm.click(None)
		resultingPage = resultingPage.doRedirects()
   
		successPtr = resultingPage.page.find("was successfully saved.")
		if successPtr == -1:
			print "ERROR: cannot set flag"
    
		print "COOKIE:",cookie
        
	except Exception, e:
		print "ERROR: got exception %s getting flag" % (e)
        

if __name__ == "__main__":
	CtfUtil.main(score)
