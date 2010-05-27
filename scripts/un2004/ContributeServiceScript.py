#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

candidates = ['blitzkrieg', 'stallone', 'schtrappe', 'blix', 'schmidt']

def score(ip,flag,cookie):
	#get old flag
	if cookie != None:
		try:
			cc = cookie

			personality = browserpersonality.getRandomPersonality()
			resultPage = pybrowse.Browser("http://" + ip + "/~support/"+cc+".php", personality)
			resultPage.open()
			resultPage.parse()

			successPtr = resultPage.page.find("(")

			if successPtr != -1:
				oldFlag = resultPage.page[successPtr+1:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		candidate = random.choice(['Blitzkrieg','Stallone','Schtrappe','Schmidt','Blix'])
		cc = str(random.randint(10000000,99999999))
		amount = str(random.randint(1,9999))
		comment = flag 

		setFlagUrl = ip+"/~support/cgi-bin/donate.py?candidate="+candidate+"&cc="+cc+"&amount="+amount+"&comment="+comment
		mainpg = pybrowse.Browser("http://" + setFlagUrl)
		mainpg.open()

		successPtr = mainpg.page.find("Thank you very much")
		if successPtr == -1:
			print "ERROR: could not post new flag"
			return

		cookie = cc
		print "COOKIE:",cookie
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
