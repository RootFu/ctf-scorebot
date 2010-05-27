#!/usr/bin/python -u

import os, random, time, sys, string, socket
from utility import CtfUtil

good_password = ['bbbccc','aaabbb','cccddd']
bad_password  = ['table','desktop','message','password','robot']

rbuffer = ''

def readline(s):
	global rbuffer

	if '\n' in rbuffer:
		pos = rbuffer.find('\n')
		result = rbuffer[:pos]
		rbuffer = rbuffer[pos+1:]
		return result
        
	data = rbuffer+s.recv(100)
	while ('\n' in data) == False:
		data += s.recv(100)

	pos = data.find('\n');
	rbuffer = data[pos+1:]
	return data[:pos]
            
    
def read_flag(s, username, password):
	s.send('login %s %s\n'%(username,password))
	res = readline(s)
    
	if res[:3] != "200":
		return ""
    
	s.send('stat\n')
	res = readline(s)

	if res[:5] == "There":
		return ""
        
	res = readline(s)
	flag = res[4:]
        
	while res[:3] != "200":
		res = readline(s)
        
	return flag
        
        
def create_flag(s, flag):
	username = CtfUtil.getRandomString(6)
	password = random.choice(good_password)
	s.send('new %s %s\n'%(username,password))
        
	res = readline(s)

	if res[:3] != "200":
		return ""
        
	s.send("to: xxxx\n")
	res = readline(s)
        
	s.send("spam\n")
	res = readline(s)
	res = readline(s)
	res = readline(s)
        
	s.send("%s\n"%flag)
	s.send(".\n")
	res = readline(s)
        
	return username+":"+password
    
def score(ip,flag,cookie):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, 4570))
            
		res = readline(s)
		res = readline(s)
		res = readline(s)
            
            
		if cookie != None:
			username, password = cookie.split(":")
			oldFlag = read_flag(s,username,password)
			print "FLAG:",oldFlag
 
		cookie = create_flag(s,flag)
		print "COOKIE:",cookie
 
		s.send("exit\n")
		s.close()

	except Exception, e:
		print "ERROR: %s" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
