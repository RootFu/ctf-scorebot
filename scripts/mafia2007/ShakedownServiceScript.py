#!/usr/bin/python -u

# shakedown scoring script.
# 
# Flags are stored by sending a message from the boss to one of his
# artists.
# Flags are read by logging in as an artist and checking the messages

import os, random, time, sys, string, re

from utility import pybrowse, browserpersonality, CtfUtil

countries = ["US", "Italy", "Germany", "India", "UK", "Austria", "France", "Canada", "test", "blah"]

titles = ["Message", "test", "Test", "Title", "you have mail", "important"]

def getRandomCountry():
	"""get a random country name. 
	   used during the generation of new artist users."""
	return countries[random.randint(0, len(countries) - 1)]
    
def getRandomTitle():
	"""get a random message title.
	   used during the generation of new messages."""
	return titles[random.randint(0, len(titles) - 1)]
   
def checkError(page):
	errorPtr = page.page.find("Traceback")
	if errorPtr != -1:
		print "ERROR: failed checkError"
		sys.exit(-1)
        
	errorPtr = page.page.find("following error")
	if errorPtr != -1:
		print "ERROR: failed checkError"
		sys.exit(-1)
        
    
def score(ip,flag,cookie):
	myPort = "4242"
	oldFlag = None
        
	# get old flag
	if cookie != None:
		artist_name, artist_pwd = cookie.split(":")
        
		try:
			personality = browserpersonality.getRandomPersonality()
                
			# 1. go to the main page
			mainpg = pybrowse.Browser("http://" + ip + "/Site/Bosses_and_artists.html")
			mainpg.open()
        
			# 2. login as an artist
			mainpg = pybrowse.Browser("http://" + ip  + ":" + myPort + "/artists/login/")
			mainpg.open()
			mainpg.parse()

			adminForm = mainpg.forms[0]
			adminForm.fields["username"] = artist_name
			adminForm.fields["password"] = artist_pwd
			resultingPage = adminForm.click( None )
			resultingPage = resultingPage.doRedirects( )
			resultingPage.parse()
			successPtr = resultingPage.page.find("Confirmation number:")
                
			if successPtr != -1:
				oldFlag = resultingPage.page[successPtr + 21:][:len(flag)]
                
			print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
        
	# set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
        
		# 1. go to the shell's page
		mainpg = pybrowse.Browser("http://" + ip + "/Site/Bosses_and_artists.html")
		mainpg.open()
        
		# 2. create a new boss
		mainpg = pybrowse.Browser("http://" + ip + ":" + myPort + "/bosses/new/")
    
		mainpg.open()
		mainpg.parse()
            
		myform = mainpg.forms[0]

		boss_name = CtfUtil.getRandomString(random.randint(6,16))
		boss_pwd = CtfUtil.getRandomString(random.randint(6,8))
            
		myform.fields["name"] = boss_name.capitalize()
		myform.fields["username"] = boss_name
		myform.fields["password"] = boss_pwd
		myform.fields["password_again"] = boss_pwd
            
		resultingPage = myform.click( None )
		resultingPage = resultingPage.doRedirects( )
		resultingPage.parse()
            
		checkError(resultingPage)
        
		# resulting page should be /bosses/view/N/
		boss_id = resultingPage.documentroot.split("/")[3]
            
		# 3. create a new artist and link it to the boss
		mainpg = pybrowse.Browser("http://" + ip + ":" + myPort  + "/artists/new/")
		mainpg.open()

		mainpg.parse()
		successPtr = mainpg.page.find("option value=\"" + boss_id)
		if successPtr == -1:
			print "ERROR: Error creating new artist"
			return
                
		mainpg.forms[0].addField("boss", boss_id)
		myform = mainpg.forms[0]

		artist_name = CtfUtil.getRandomString(random.randint(6,16))
		artist_pwd = CtfUtil.getRandomString(random.randint(6,8))
            
		myform.fields["name"] = artist_name.capitalize()
		myform.fields["username"] = artist_name
		myform.fields["password"] = artist_pwd
		myform.fields["password_again"] = artist_pwd
		myform.fields["country"] = getRandomCountry()

		resultingPage = myform.click( None )
		resultingPage = resultingPage.doRedirects()
		resultingPage.parse()
        
		checkError(resultingPage)
        
		# 4. login as the initial boss
		mainpg = pybrowse.Browser("http://" + ip + ":" + myPort + "/bosses/login/")
		mainpg.open()
		mainpg.parse()
		myform = mainpg.forms[0]
		myform.fields["username"] = boss_name
		myform.fields["password"] = boss_pwd
		resultingPage = myform.click( None )
		resultingPage = resultingPage.doRedirects()
		resultingPage.parse()
        
		# 5. click on the protection link and set flag
		resultingPage = resultingPage.click(resultingPage.links[10])
		resultingPage.doRedirects()
		resultingPage.parse()

		myform = resultingPage.forms[0]
		myform.fields["news-title"] = getRandomTitle()
		myform.fields["news-content"] = "Confirmation number: " + flag
		myform.fields["news-revenue"] = random.randint(0, 1000000)
		resultingPage = myform.click( "news" )
		resultingPage = resultingPage.doRedirects()
		resultingPage.parse()
        
		checkError(resultingPage)
        
		cookie = artist_name + ":" + artist_pwd
		print "COOKIE:",cookie
        
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)
		return

if __name__ == "__main__":
	CtfUtil.main(score)
