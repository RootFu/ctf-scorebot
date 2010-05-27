#!/usr/bin/python -u

import os, random, time, sys, string

from utility import pybrowse, browserpersonality, CtfUtil

numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
def getRandomDollarAmount(len):
	dollars = ""
	cents = ""
	for i in range(len):
		dollars += random.choice(numbers)
	for i in range(2):
		cents += random.choice(numbers)
    
	return dollars + '.' + cents
    
def getRandomPiratedFiles(num):
	return "Your pirated music here"
    
def createAccount(ip,fname, lname, eaddr, files, price):
	url = "http://" + ip + "/Site/Make_amends_files/widget1_markup.html"
	personality = browserpersonality.getRandomPersonality()
	mainpg = pybrowse.Browser(url, personality)
	mainpg.open()
	mainpg.parse()
    
	userForm = mainpg.forms[0]
	userForm.fields['first'] = fname
	userForm.fields['last'] = lname
	userForm.fields['email'] = eaddr
	userForm.fields['comment'] = files
	userForm.fields['price'] = price
	resultPage = userForm.click(None)
    
	rawPage = resultPage.page
	successPattern = "Thank you for participating"
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error creating account"
		sys.exit(2)
    
	return resultPage
    
def chooseFormatPref(mainpg):
	mainpg.parse()
        
	formatForm = mainpg.forms[0]
	#todo: always prefer txt, just in case the pref cookie is preserved and pdf
	#todo: (as then I wouldn't be able to read it)
	formatForm.fields['ltrfmt'] = "txt"
	#formatForm.fields['ltrfmt'] = random.choice(("pdf","txt"))
        
	resultPage = formatForm.click(None)
    
	rawPage = resultPage.page
	successPattern = "CASE ID #"
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error in chooseFormatPref"
		sys.exit(2)

	caseid = rawPage[successPtr+len(successPattern)+10:][:16]
	return caseid
    
def doNewLogin(ip,eaddr, caseid):
	url = "http://" + ip + "/~amends/cgi-bin/settlement.php"
	personality = browserpersonality.getRandomPersonality()
	mainpg = pybrowse.Browser(url, personality);
	mainpg.open()
	mainpg.parse()
    
	loginForm = mainpg.forms[0]
	loginForm.fields['email'] = eaddr
	loginForm.fields['caseid'] = caseid
	resultPage = loginForm.click(None)
	resultPage = resultPage.doRedirects()
    
	rawPage = resultPage.page
	successPattern = "You haven't yet settled with the MAFIA."
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error in doNewLogin"
		sys.exit(2)
    
	return resultPage
    
def doReturningLogin(ip,eaddr, caseid):
	url = "http://" + ip + "/~amends/cgi-bin/settlement.php"
	personality = browserpersonality.getRandomPersonality()
	mainpg = pybrowse.Browser(url, personality);
	mainpg.open()
	mainpg.parse()
    
	loginForm = mainpg.forms[0]
	loginForm.fields['email'] = eaddr
	loginForm.fields['caseid'] = caseid
	resultPage = loginForm.click(None)
	resultPage = resultPage.doRedirects()
   
	rawPage = resultPage.page
	successPattern = "Settlement Confirmation"
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error in doReturningLogin"
		sys.exit(2)

	return resultPage
    
def viewSettlementLetter(mainpg):
	mainpg.parse()
    
	resultPage = mainpg.click(mainpg.links[0])
    
	rawPage = resultPage.page
	#todo: are we *certain* that we will always be viewing txt?
	#todo: perhaps the bot can always prefer txt output
	successPattern = "Tom Hagen"
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error in viewSettlementLetter"
		sys.exit(2)
        
	return resultPage
    
def paySettlement(mainpg,flag):
	mainpg.parse()
    
	payForm = mainpg.forms[0]
	payForm.fields['ccnum'] = flag
	resultPage = payForm.click(None)
    
	rawPage = resultPage.page

	successPattern = "Thank you for taking the time to pay off the MAFIA!"
	successPtr = rawPage.find(successPattern)

	if successPtr < 0:
		print "ERROR: error in paySettlement"
		sys.exit(2)
    
	return resultPage
    
def viewConfirmation(mainpg):
	mainpg.parse()
    
	resultPage = mainpg.click(mainpg.links[0])
    
	rawPage = resultPage.page
	successPattern = "Settlement Confirmation"
	successPtr = rawPage.find(successPattern)
	if successPtr < 0:
		print "ERROR: error in viewConfirmation"
		sys.exit(2)
    
	return resultPage
        
def score(ip,flag,cookie):
	# get old flag
	oldFlag = ""
	if cookie != None:
		eaddr, caseid = cookie.split(":")
		try:
			# login using the old account
			resultPage = doReturningLogin(ip,eaddr, caseid)
        
			# retrieve flag
			rawPage = resultPage.page
    
			successPattern = "card number:"
			successPtr = rawPage.find(successPattern)
			if successPtr >= 0:
				oldFlag = rawPage[successPtr+21:][:len(flag)] 
				print "FLAG:",oldFlag
                
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
			sys.exit(1)
        
	# set new flag
	try:
		url = "http://" + ip + "/Site/Make_amends.html"
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser(url, personality)
		mainpg.open()
            
		# create a new user acccount
		fname = CtfUtil.getRandomString(random.randint(6,10))
		lname = CtfUtil.getRandomString(random.randint(6,10))
		eaddr = CtfUtil.getRandomEmail()
		files = getRandomPiratedFiles(random.randint(1,5))
		price = getRandomDollarAmount(random.randint(1,5))
		resultPage = createAccount(ip,fname, lname, eaddr, files, price)
        
		# choose settlement letter format preference and get case id
		caseid = chooseFormatPref(resultPage)
        
		# login using the new account
		resultPage = doNewLogin(ip, eaddr, caseid)
        
		# view the settlement letter
		viewSettlementLetter(resultPage)
        
		# settle with the MAFIA
		resultPage = paySettlement(resultPage,flag)
    
		# view the settlement confirmation
		resultPage = viewConfirmation(resultPage)
    
		cookie = eaddr + ":" + caseid

		print "COOKIE:",cookie
    
	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)
		return

if __name__ == "__main__":
	CtfUtil.main(score)
