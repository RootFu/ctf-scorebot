#!/usr/bin/python -u

import re, socket, sys
from utility import CtfUtil

seed = 0
r1 = re.compile("v[0-9]+\\.[0-9]+\\.([0-9]+)")
r2 = re.compile("[0-9a-f]+: ([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])")

"""
Get and set flag for syscalld.
"""

def extractSeed(str):
	seed = 0
	m = r1.search(str)
	if m:
		seed = int(m.group(1))
	return seed
    
def extractFlag(str):
	"""
	Extract flag from "memory dump."
	"""
        
	flag = ""
	lines = str.split("\n")
	for line in lines:
		m = r2.search(line)
		if m:
			#print "DEBUG: matched %s %s %s %s" % \
			#    (m.group(4), m.group(3), m.group(2), m.group(1))
			byte0 = int("0x" + m.group(4), 16)
			byte1 = int("0x" + m.group(3), 16)
			byte2 = int("0x" + m.group(2), 16)
			byte3 = int("0x" + m.group(1), 16)
			flag += chr(byte0) + chr(byte1) + chr(byte2) + chr(byte3)
    
	return flag
    
def randomize(str):
	"""
	Return "randomized" instruction.
	"""
	
	global seed
    
	if seed <= 0:
		return str
    
	ret = ""
	for i in str:
		ret += chr(ord(i) ^ seed)
        
	#print "DEBUG: ret=%s" % (ret)
	return ret
    
def send(fd, str):
	"""
	Send string over socket.
	"""
    
	#print "DEBUG: %s" % (str.strip())
	fd.send(str)
    
	return fd.recv(1024)
    
def score(ip,flag,cookie):
	"""
	Main.
	"""
	global seed
    
	oldFlag = ""
    
	try:
		#Connect
		fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		fd.connect((ip,31337))
    
		#Read banner
		banner = fd.recv(1024)
    
		# XXX: Get seed
		seed = extractSeed(banner)
    
		# Open flag file
		send(fd, "%s %%ecx\n" % (randomize("pushl")))
		send(fd, "%s $0x5,%%eax\n" % (randomize("movl")))
		send(fd, "%s %%ecx,%%ebx\n" % (randomize("movl")))
		send(fd, "%s $0x7273752f,(%%ecx)\n" % (randomize("movl")))    # /usr
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x636f6c2f,(%%ecx)\n" % (randomize("movl")))    # /loc
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x732f6c61,(%%ecx)\n" % (randomize("movl")))    # al/s
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x65726168,(%%ecx)\n" % (randomize("movl")))    # hare
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x7379732f,(%%ecx)\n" % (randomize("movl")))    # /sys
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x6c6c6163,(%%ecx)\n" % (randomize("movl")))    # call
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x6c662f64,(%%ecx)\n" % (randomize("movl")))    # d/fl
		send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		send(fd, "%s $0x00006761,(%%ecx)\n" % (randomize("movl")))    # ag..
		#send(fd, "%s $0x67616c66,(%%ecx)\n" % (randomize("movl")))
		#send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
		#send(fd, "%s $0x0,(%%ecx)\n" % (randomize("movl")))
		send(fd, "%s $0x42,%%ecx\n" % (randomize("movl")))
		send(fd, "%s $0x180,%%edx\n" % (randomize("movl")))
		#print send(fd, "%s\n" % (randomize("dump")))
		send(fd, "%s\n" % (randomize("sysenter")))
    
		#print send(fd, "%s\n" % (randomize("dump")))
    
		# Save fd in ebx, save buffer on stack
		send(fd, "%s %%eax,%%ebx\n" % (randomize("movl")))
		send(fd, "%s %%ecx\n" % (randomize("popl")))
		send(fd, "%s %%ecx\n" % (randomize("pushl")))
    
		#print send(fd, "%s\n" % (randomize("dump")))
    
		# Clear buffer
		#for i in range(8):
			#send(fd, "%s $0x0,(%%ecx)\n" % (randomize("movl")))
			#send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
			#send(fd, "%s %%ecx\n" % (randomize("popl")))
			#send(fd, "%s %%ecx\n" % (randomize("pushl")))
    
		# Get old flag
		send(fd, "%s $0x3,%%eax\n" % (randomize("movl")))
		send(fd, "%s $0x40,%%edx\n" % (randomize("movl")))
    
		#print send(fd, "%s\n" % (randomize("dump")))
    
		send(fd, "%s\n" % (randomize("sysenter")))
    
		#print send(fd, "%s\n" % (randomize("dump")))
		oldFlag = extractFlag(send(fd, "%s %%ecx\n" % (randomize("dump"))))
		print "FLAG:",oldFlag[:len(flag)]
            
		# Rewind file
		send(fd, "%s $0x13,%%eax\n" % (randomize("movl")))
		send(fd, "%s $0x0,%%ecx\n" % (randomize("movl")))
		send(fd, "%s $0x0,%%edx\n" % (randomize("movl")))
    
		send(fd, "%s\n" % (randomize("sysenter")))
    
		send(fd, "%s %%ecx\n" % (randomize("popl")))
		send(fd, "%s %%ecx\n" % (randomize("pushl")))
    
		# Write new flag
		newFlag = flag
		dword = ""
		for i in range(len(newFlag)):
			dword = "%2x%s" % (ord(newFlag[i]), dword)
			if i % 4 == 3:
				send(fd, "%s $0x%s,(%%ecx)\n" % (randomize("movl"), dword))
				send(fd, "%s $0x4,%%ecx\n" % (randomize("addl")))
				dword = ""
    
		if dword:
			while len(dword) < 8:
				dword = "00%s" % (dword)
			send(fd, "%s $0x%s,(%%ecx)\n" % (randomize("movl"), dword))
    
		send(fd, "%s $0x4,%%eax\n" % (randomize("movl")))
		send(fd, "%s %%ecx\n" % (randomize("popl")))
		send(fd, "%s %%ecx\n" % (randomize("pushl")))
		send(fd, "%s $0x%x,%%edx\n" % (randomize("movl"), len(newFlag)))
    
		send(fd, "%s\n" % (randomize("sysenter")))
            
	except Exception, e:
		print "ERROR: %s" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
