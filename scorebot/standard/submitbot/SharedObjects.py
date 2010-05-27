from scorebot.standard.submitbot.FlagValidator import FlagValidator
from scorebot.standard.submitbot.FlagCollector import FlagCollector

_shared_validator = None
_shared_collector = None

def setSharedValidator(validator):
	global _shared_validator
	_shared_validator = validator

def getSharedValidator():
	global _shared_validator
	return _shared_validator

def setSharedCollector(collector):
	global _shared_collector
	_shared_collector = collector

def getSharedCollector():
	global _shared_collector
	return _shared_collector
