#!/usr/bin/env python

import commands, os, array, string, sys, time
from socket import *
from threading import Thread
import subprocess, MySQLdb
from /usr/local/lib/placebo/server import *


#####################################################################################
# Thread for processing Server requests
#####################################################################################
class proc_server_request(Thread):
	def __init__ (self, connect, address, hostname):
        	Thread.__init__(self)
        	self.connect = connect
		self.address = address
		self.hostname = hostname

	def run(self):
		connect = self.connect
		msg = decrypt(connect.recv(65565))
		if msg != None:
			if clean_string(msg[0:8]) == "CLNT_NEW":
				add_server_to_db(hostname, address[0])
				add_key_to_keyring(str(msg[8:]))
				print msg[9:]
				connect.send(encrypt("SRV_0000",hostname))	
			elif clean_string(msg[0:8]) == "CLNT_SCN":
				add_scan_to_db(hostname, str(msg[8:]))
				connect.send(encrypt("SRV_0000", hostname))	
			elif clean_string(msg[0:8]) == "CLNT_VSU":
				add_signatures_to_db(hostname, str(msg[8:]))
				connect.send(encrypt("SRV_0000", hostname))
			else:
				connect.send(encrypt("SRV_0001", hostname))
		connect.close()

##### MAIN #####
port=int(get_config_parameter("srv_port"))
host=get_config_parameter("srv_addr")
addr=(host,port)

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.bind(addr)
serversocket.listen(5)

while 1: 
    try: 
        connection,address = serversocket.accept()
	hostname = str(get_hostname(address[0]))
	print hostname
      	new_thread = proc_server_request(connection,address[0],hostname)
       	new_thread.start()
		
    except KeyboardInterrupt:
        print "Exit"
	serversocket.close()
	sys.exit(0)
       
serversocket.close()


