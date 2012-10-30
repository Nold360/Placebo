#!/usr/bin/env python
'''
This is the Placebo SQL-Query Tool

Author: Gerrit Pannek
Licence: GPLv3
'''
import sys
from placebo_server import *

def help():
	print "Usage: "+sys.argv[0]+" <MySQL-String>"

if len(sys.argv) < 2:
	help()
	sys.exit(0)

try:
	if len(sys.argv) == 2:
		query = sys.argv[1]
	else:
		help()
		sys.exit(1)
except:
	help()
	sys.exit(1)

print send_to_db(query)

	
sys.exit(0)
