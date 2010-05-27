import sys
import random
import string

"""
This script helps simplify the transition of scorebot4 
scripts to scorebot5 scripts.
"""

def main(scoreFunction):
	ip = sys.argv[1]
	flag = sys.argv[2]
	cookie = None

	if(len(sys.argv) == 4):
		cookie = sys.argv[3]

	scoreFunction(ip,flag,cookie)

def getRandomString(len):
	return "".join(random.choice(string.letters) for i in xrange(len))

def getRandomAlphaNum(len):
	alnum = string.letters + string.digits
	return "".join(random.choice(alnum) for i in xrange(len))

def getRandomEmail():
	domains = ["com","edu","org","biz","net","foo","bar"]
	first = getRandomString(random.randint(5,8))
	second = getRandomString(random.randint(4,8))
	return "%s@%s.%s" % (first,second,random.choice(domains))
