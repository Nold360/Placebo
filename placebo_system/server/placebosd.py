#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
#
# Placebo Client base - This code is in work..
# The rewrite will not be compatible with the "old" Placebo POC code
#
# Dependencies: pyclamd, python-gnupg
#
# Regards Nold
#
############################################################################

import sys, socket, time, os
from placebolib import *
from placebo_server_lib import *
from threading import Thread

DEBUG = True
CONFIG = {}

class Listend_Thread(Thread):
	"""
	This Thread handes the request comming from the Server
	"""
	def __init__(self, connection, placebo):
		super(Listend_Thread, self).__init__()
		self.connection = connection
		self.connection.settimeout(5)
		self.gpg = GPG(CONFIG["GPG_HOME_PATH"])
		self.placebo = placebo
		self.mysql = placebo.mysql
	
	def run(self):
		if DEBUG: print "Got request - need to handle that"
		request = recv_end(self.connection)

		#If request is encrypted
		if "-----BEGIN PGP MESSAGE-----" in request.split("\n")[0]:
			dec_request = gpg.decrypt(request)
		#Else it can only be a CLNT_NEW request
		elif "CLNT_NEW" in enc_msg[:8]:
			if self.gpg.import_key(enc_msg[8:]) != -1:
				send_end(self.connection, gpg.encrypt("CLNT_NEW"+gpg.get_key()))
				request = recv_end(self.connection)
				if "CLNT_000" in self.gpg.decrypt(request):
					if DEBUG: print "SUCCESSFULLY IMPORTED CLIENT KEY!"	
				else:
					if DEBUG: print "BAD CLIENT RESPONSE FOR GPG KEY!"	
		else:
			send_end(self.connection, "SRV_9999")

		#Handle Encrypted Requests		
		#FIXME: Neet to check if GPG has a key for the Server!
		if dec_request or dec_request != "":
			id = dec_request[:36]
			content = dec_request[36:]
			if "EOF" in content:
				content = content[:-4]
			if DEBUG: print "Got Ticket: "+id

			if self.mysql.ticket_exists(id):
				self.mysql.ticket_move(id, content)
				self.mysql.ticket_remove(id)
				send_end(self.connection, self.gpg.encrypt("SRV_0000"))
				print content
				if DEBUG: print "Ticket moved!"
			else:
				send_end(self.connection, self.gpg.encrypt("SRV_7020"))
				if DEBUG: print "Ticket isn't valid!"
						
		self.connection.close()
		del self
	

class Listend(Thread):
	def __init__(self, placebo):
		super(Listend, self).__init__()
		self.placebo = placebo
		self.mysql = placebo.mysql
		addr = (CONFIG["LISTEN_ADDR"],int(CONFIG["LISTEN_PORT"]))
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind(addr)
		self.serversocket.listen(1)
		if DEBUG: print "Listend init done!"

	def run(self):
		while 1:
			if 1:
			#try:
				connection,address = self.serversocket.accept()
				if self.mysql.host_exists(socket.gethostbyaddr(address[0])[0].split(".")[0]):
					new_thread = Listend_Thread(connection, placebo)
					new_thread.start()
				else:
					if DEBUG: print "Bad Client"
					connection.send("SRV_9999")
					connection.close()
			#except:
			#	self.serversocket.close()
		self.serversocket.close()
		sys.exit(0)

class Placebo(Thread):
        def __init__(self):
                super(Placebo, self).__init__()
                self.parse_config()

		self.mysql = Database(CONFIG["MYSQL_HOST"], CONFIG["MYSQL_USER"], 
					CONFIG["MYSQL_PASSWD"], CONFIG["MYSQL_DB"])

                listend = Listend(self)
                listend.start()

                if DEBUG: print "Init done!"

        def parse_config(self):
                self.config = {}
                try:
                        conf_file = open("/etc/placebo/server.conf", "r")
                except:
                        print "ERROR: Couldn't open /etc/placebo/server.conf"
                        sys.exit(1)
                for line in conf_file:
                        if line[0] != "#":
                                try:
                                        parameter = str(line.split("=")).split("\"")
                                        parameter[0] = parameter[0].split("'")[1].strip()
                                        CONFIG[parameter[0]] = parameter[1]
                                except: continue
                conf_file.close()
                return 0

        def run(self):
                while 1:
                        time.sleep(1)

if __name__ == "__main__":
        placebo = Placebo()
        placebo.start()

        gpg = GPG(CONFIG["GPG_HOME_PATH"])
        if not gpg.get_key() or not gpg:
                print "ERROR: No GPG-Key found! See /etc/placebo/client.conf or generate key!"
                sys.exit(1)

        while 1:
                try:
                        time.sleep(1)
                except:
                        sys.exit(1)

