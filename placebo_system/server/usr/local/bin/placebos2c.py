#!/usr/bin/env python
'''
This is the Placebo Server-2-Client Tool
With this tool you are able to scan, update or add a host.

It will write all results to the MySQL Backend using the "placebo_server" Module

Author: Gerrit Pannek
Licence: GPLv3
'''
import string, os, sys, socket, subprocess
from placebo_server import *

def help():
	print "Usage: "+sys.argv[0]+" <scan|add|update> <hostname>"

if len(sys.argv) < 3:
	help()
	sys.exit(0)

if "scan" == sys.argv[1][:4]:
	command = "CLNT_SCN"
	try: 
		path = str(sys.argv[1]).split(":")[1] 
	except:
		path = "/"	

	print "Scanning Client..."
	print "Path: "+path

elif "update" == sys.argv[1]:
	print "Updateing Client..."
	command = "CLNT_VSU"

elif "add" == sys.argv[1]:
	print "Adding Client..."
	command = "CLNT_NEW"

host = sys.argv[2]
if len(sys.argv) > 3:
	port = sys.argv[3]
else:
	port = 41337

print host+":"+str(port)+" "+command

if 1 == 1:
#try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((str(host), int(port)))
	print "Connected..."

	if command == "CLNT_SCN":
		if host_exists(host):
			send_end(s, encrypt("CLNT_SCN"+path, host))
			print "Waiting..."
			ret = decrypt(recv_end(s))
			print "REPLAY: "+ret
			if ret[:8] == "CLNT_000":
				add_scan_to_db(host, path, ret[8:])

	elif command == "CLNT_VSU":
		if host_exists(host):
			send_end(s,encrypt("CLNT_VSU", host))
			ret = decrypt(recv_end(s))
			if ret[:8] == "CLNT_000":
				add_signatures_to_db(host, ret[8:])

	elif command == "CLNT_NEW":
		#if not host_exists(host):
		send_end(s,"CLNT_NEW"+get_public_key())
		ret = decrypt(recv_end(s))
		print ret[:8]
		if ret[:8] == "CLNT_NEW":
			add_server_to_db(host, s.getpeername()[0])
			add_public_key(ret[8:])
			send_end(s,encrypt("SRV_0000", host))
	else:
		print "Abort!"
		sys.exit(1)

	if ret[:8]!= clean_string("CLNT_000") and (command != "CLNT_NEW" and ret[:8] != "CLNT_NEW"):
		print "ERROR_CODE: "+ret[:-4]
	else:
		print "OK"
	s.close()
#except:
#	print "ERROR: Can't connect to Host!"
#	sys.exit(1)
	
sys.exit(0)
