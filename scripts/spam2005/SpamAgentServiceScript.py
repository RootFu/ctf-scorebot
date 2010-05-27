#!/usr/bin/python -u
import httplib
import urllib
import random
import re

from utility import pybrowse, browserpersonality, CtfUtil

def postAgentText(ip,agentText):
	url = ip+"/~spamagent/spamagent.html"
        
	mainpg = pybrowse.Browser("http://" + url)
	mainpg.open()
	mainpg = mainpg.doRedirects()
	mainpg.parse()
            
	form = mainpg.forms[0]
           
	form.fields['script'] = agentText
	resultPage = form.click(None).page
        
	return resultPage
    
def score(ip,flag,cookie): 
	personality = browserpersonality.getRandomPersonality()
        
	if cookie != None:
		try:
			name,password = cookie.split(":")
                
			senderText = "<sender><user>"+name+"</user><password>"+password+"</password></sender>"
			codeText = "<code>set flag [store get flag]; results set $flag</code>"
			agentText = "<agent>\n" + senderText +"\n"+codeText+"\n</agent>"
                
			resultPage = postAgentText(ip,agentText)
                
			oldFlag = resultPage[:len(flag)]
			print "FLAG:",oldFlag
 
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
			return
        
	#set new flag
	try:
		name = CtfUtil.getRandomString(random.randint(6,8))
		password = CtfUtil.getRandomAlphaNum(8)
            
		senderText = "<sender><user>"+name+"</user><password>"+password+"</password></sender>"
		codeText = "<code>store set flag \""+flag+"\"; results set \"Flag was set\";</code>"
            
		agentText = "<agent>\n" + senderText +"\n"+codeText+"\n</agent>"
             
		resultPage = postAgentText(ip,agentText)
            
		successPattern = "Flag was set"
		successPtr = resultPage.find(successPattern)

		if successPtr >= 0:
			cookie = name+":"+password
           	print "COOKIE:",cookie 

	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
