#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie):

	#get old flag  
	if cookie != None:
		try:
			name = cookie

			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/~feedback/cgi-bin/candidates.php", personality)
			mainpg.open()
			mainpg.parse()

			candidate = random.randint(0,4)

			feedbackForm = mainpg.forms[candidate]
			feedbackForm.fields['name'] = name
			feedbackForm.fields['comment'] = CtfUtil.getRandomString(5) + " " + CtfUtil.getRandomString(random.randint(4,9)) + random.choice(['?','.','!'])

			resultPage = feedbackForm.click(None)

			successPtr = resultPage.page.find("About")
			if successPtr != -1:
				oldFlag = resultPage.page[successPtr+9:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/~feedback/cgi-bin/candidates.php", personality)
		mainpg.open()
		mainpg.parse()

		candidate = random.randint(0,4)
		feedbackForm = mainpg.forms[candidate]

		name = CtfUtil.getRandomString(random.randint(6,8)) 
		feedbackForm.fields['name'] = name
		feedbackForm.fields['comment'] = flag

		resultPage = feedbackForm.click(None)

		successPtr = resultPage.page.find("feedback so far")
		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		cookie = name
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
