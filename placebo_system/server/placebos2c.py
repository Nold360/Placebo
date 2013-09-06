#!/usr/bin/env python
'''
This is the Placebo Server-2-Client Tool
With this tool you are able to scan, update or add a host.

It will write all results to the MySQL Backend using the "placebo_server" Module

Author: Gerrit Pannek
Licence: BSD 2-clause
'''
import string, os, sys, socket, subprocess
from placebo_server_lib import *
from placebolib import *

def help():
	print "Usage: "+sys.argv[0]+" <scan|add|update|get|set|ping>[:parameter[=value]] <hostname>"

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
	port = int(sys.argv[3])
else:
	port = 41337

print host+":"+str(port)+" "+command

gpg = GPG("/home/placebo/.gnupg", client=False, hostname=host)
mysql = Database("localhost", "root", "RootPasswd", "placebo")

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
			mysql.add_status_to_db(host, "socket.error")
		sys.exit(1)

	print "Connected..."

	if command == "CLNT_SCN":
		#if mysql.host_exists(host):
		if 1:
			send_end(s, gpg.encrypt("CLNT_SCN"+path))
			ret = gpg.decrypt(recv_end(s)) 
			if "CLNT_SCN" in ret:
				ticket_id = ret[8:]
				print "Got Ticket: "+ticket_id[:-4]
				mysql.add_ticket_to_db(host, Ticket(Ticket.TYPE_SCAN, content=path, status=Ticket.TICKET_WAITING, id=ticket_id[:-4]))
				s.close()
			else:
				print "ERROR: Client returned: "+ret[:8]
				
	elif command == "CLNT_VSU":
		if mysql.host_exists(host):
			send_end(s,gpg.encrypt("CLNT_VSU"))
			ret = gpg.decrypt(recv_end(s)) 
			if "CLNT_VSU" in ret:
				ticket_id = ret[8:]
				print "Got Ticket: "+ticket_id[:-4]
				mysql.add_ticket_to_db(host, Ticket(Ticket.TYPE_UPDATE, content=None, status=Ticket.TICKET_WAITING, id=ticket_id[:-4]))
				s.close()
			else:
				print "ERROR: Client returned: "+ret[:8]

	elif command == "CLNT_NEW":
		if not mysql.host_exists(host):
			send_end(s,"CLNT_NEW"+gpg.get_key())
			ret = gpg.decrypt(recv_end(s))
			print ret
			if ret[:8] == "CLNT_NEW":
				mysql.add_server_to_db(host, s.getpeername()[0])
				gpg.import_key(ret[8:])
				send_end(s,gpg.encrypt("SRV_0000"))
			else:
				send_end(s,gpg.encrypt("SRV_0001"))
		else:
			print "Abort! Client already exists!"
			send_end(s, gpg.encrypt("SRV_9090"))
			s.close()
			sys.exit(2)

	elif command == "CLNT_GET":
		if mysql.host_exists(host):
			send_end(s,gpg.encrypt("CLNT_GET"+parameter))
			ret = gpg.decrypt(recv_end(s))
			
			if not "CLNT_401" in ret and ret[:-4] != "":
				print "VALUE: "+ret[8:-4]
			elif "CLNT_401" in ret:
				print "ERROR: CLNT_401: No such Parameter"
				s.close()
				sys.exit(1)
			else:
				print "ERROR: Got "+ret[:-4]
				s.close()
				sys.exit(1)

	elif command == "CLNT_SET":
		if mysql.host_exists(host):
			send_end(s,gpg.encrypt("CLNT_SET"+parameter+"="+str(value)))
			ret = gpg.decrypt(recv_end(s))[:-4]
			
			if "CLNT_000" in ret[:-4]:
				print "Success: Paramter "+parameter+" has been set to "+str(value)+"!"
			else:
				print "ERROR: "+ret+": No such Parameter"
				s.close()
				sys.exit(1)

	elif command == "CLNT_PIG":
		if mysql.host_exists(host):
			send_end(s,gpg.encrypt("CLNT_PIG"))
			ret = recv_end(s)
			if ret[:4] == "----":
				ret = gpg.decrypt(ret)
			if ret[:-4] == "CLNT_POG":
				print "OK"
				ret="OK"
			else:
				print "ERROR: "+ret
			mysql.add_status_to_db(host, ret)	
	else:
		print "Abort!"
		help()
		sys.exit(1)
		
	s.close()
#except:
#	print "ERROR: Can't connect to Host!"
#	sys.exit(1)
	
sys.exit(0)

