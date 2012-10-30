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
	print "Usage: "+sys.argv[0]+" <scan|add|update|get|set|ping> <hostname>"

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

elif "get" == sys.argv[1][:3]:
        command = "CLNT_GET"
        try:
                parameter = str(sys.argv[1]).split(":")[1]
        except:
                print "You must enter enter a parameter name! f.e.: get:adm_server"
		sys.exit(1)

	print "Get Paramter: "+parameter

elif "set" == sys.argv[1][:3]:
        command = "CLNT_SET"
        try:
                parameter = str(sys.argv[1]).split(":")[1].split("=")[0]
                value = str(sys.argv[1]).split(":", 1)[1].split("=",1)[1]
        except:
                print "You must enter enter a parameter name and value! f.e.: set:adm_server=127.0.0.1"
		sys.exit(1)
	
	print "Set Parameter "+parameter+" to "+value

elif "ping" == sys.argv[1][:4]:
	print "Trying to connect to host..."
	command = "CLNT_PIG"

print command

host = sys.argv[2]
if len(sys.argv) > 3:
	port = sys.argv[3]
else:
	port = 41337

print host+":"+str(port)+" "+command

if 1 == 1:
#try:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(10)
		s.connect((str(host), int(port)))
		s.settimeout(0)
		s.setblocking(1)
	except:
		print  "Error: "+str(sys.exc_info()[0]) 
		if command == "CLNT_PIG":
			add_status_to_db(host, "socket.error")
		sys.exit(1)

	print "Connected..."

	if command == "CLNT_SCN":
		if host_exists(host):
			send_end(s, encrypt("CLNT_SCN"+path, host))
			ret = decrypt(s.recv(1024)) #Normal recv to prevent high-CPU load, while client is scanning...
			if clean_string(ret[:-4]) == "CLNT_DTA":
				ret = decrypt(recv_end(s))
				if ret[:8] == "CLNT_000":
					add_scan_to_db(host, path, ret[8:])
					print "OK"
				else:
					print "ERROR: Client returned: "+ret[:8]
				
	elif command == "CLNT_VSU":
		if host_exists(host):
			send_end(s,encrypt("CLNT_VSU", host))
			ret = decrypt(s.recv(1024)) #Normal recv to prevent high-CPU load, while client is updating...
			if clean_string(ret[:-4]) == "CLNT_DTA":
				ret = decrypt(recv_end(s))
				print ret
				if ret[:8] == "CLNT_000":
					add_signatures_to_db(host, ret[8:])
					print "OK"
				else:
					print "ERROR: Client returned: "+ret[:8]

	elif command == "CLNT_NEW":
		if not host_exists(host):
			send_end(s,"CLNT_NEW"+get_public_key())
			ret = decrypt(recv_end(s))
			if ret[:8] == "CLNT_NEW":
				add_server_to_db(host, s.getpeername()[0])
				add_public_key(ret[8:])
				send_end(s,encrypt("SRV_0000", host))
			else:
				send_end(s,encrypt("SRV_0001", host))
		else:
			print "Abort! Client already exists!"
			s.close()
			sys.exit(2)

	elif command == "CLNT_GET":
		if host_exists(host):
			send_end(s,encrypt("CLNT_GET"+parameter, host))
			ret = decrypt(recv_end(s))
			
			if ret != "CLNT_401":
				print ret[:-4]
			else:
				print "ERROR: CLNT_401: No such Parameter"
				s.close()
				sys.exit(1)

	elif command == "CLNT_SET":
		if host_exists(host):
			send_end(s,encrypt("CLNT_SET"+parameter+"="+str(value), host))
			ret = decrypt(recv_end(s))[:-4]
			
			if ret == "CLNT_000":
				print "Success: Paramter "+parameter+" has been set to "+str(value)+"!"
			else:
				print "ERROR: "+ret+": No such Parameter"
				s.close()
				sys.exit(1)

	elif command == "CLNT_PIG":
		if host_exists(host):
			send_end(s,encrypt("CLNT_PIG", host))
			ret = recv_end(s)
			if ret[:4] == "----":
				ret = decrypt(ret)
			if ret[:-4] == "CLNT_POG":
				print "OK"
				ret="OK"
			else:
				print "ERROR: "+ret
			add_status_to_db(host, ret)	
	else:
		print "Abort!"
		help()
		sys.exit(1)
		
	s.close()
#except:
#	print "ERROR: Can't connect to Host!"
#	sys.exit(1)
	
sys.exit(0)
