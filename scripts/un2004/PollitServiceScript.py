#!/usr/bin/python -u
import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

candidates = ['blitzkrieg', 'stallone', 'schtrappe', 'blix', 'schmidt']

def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			print cookie
			name,id = cookie.split(":")

			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/~pollit/pollit.html", personality)
			mainpg.open()
			mainpg.parse()

			getPollForm = mainpg.forms[1]
			getPollForm.fields['username'] = name
			getPollForm.fields['pollid'] = id
			resultPage = getPollForm.click(None)

			successPtr = resultPage.page.find("-1")
			print resultPage.page
			if successPtr != -1:
				oldFlag = resultPage.page[successPtr+3:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception (%s) getting flag" % (e)

	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/~pollit/pollit.html", personality)
		mainpg.open()
		mainpg.parse()

		name = CtfUtil.getRandomString(random.randint(6,8))
		id = CtfUtil.getRandomAlphaNum(6)

		createPollForm = mainpg.forms[0]

		for candidate in candidates:
			createPollForm.fields[candidate] = str(random.randint(1,100))

		candidate = random.choice(candidates)
		createPollForm.fields[candidate] = "-1 "+flag

		createPollForm.fields['username'] = name
		createPollForm.fields['pollid'] = id

		resultPage = createPollForm.click(None)

		successPtr = resultPage.page.find("saved.")
		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		cookie = name+":"+id
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
