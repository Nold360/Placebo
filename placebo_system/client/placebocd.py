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

import sys, uuid, socket, time, os, subprocess
import pyclamd
from placebolib import *
from threading import Thread
from re import escape

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
	
	def run(self):
		request = recv_end(self.connection)
		dec_request = ""
		#If request is encrypted
		if "-----BEGIN PGP MESSAGE-----" in request.split("\n")[0]:
			try:
				dec_request = self.gpg.decrypt(request)
			except:
				try: send_end(self.connection, self.gpg.encrypt("CLNT_999"))
				except: send_end(self.connection, "CLNT_999")
				self.connection.close()
		#Else it can only be a CLNT_NEW request
		elif "CLNT_NEW" in request[:8]:
			import_result = self.gpg.import_key(request[8:])
			if import_result == 0:
				send_end(self.connection, self.gpg.encrypt("CLNT_NEW"+self.gpg.get_key()))
				request = recv_end(self.connection)
				if self.gpg.decrypt(request)[:-4] == "SRV_0000":
					if DEBUG: print "SUCCESSFULLY IMPORTED SERVER KEY!"	
			else:
				if DEBUG: print "BAD SERVER REQUEST FOR GPG KEY!"	

		#Handle Encrypted Requests		
		#FIXME: Neet to check if GPG has a key for the Server!
		if dec_request or dec_request != "":
			if "CLNT_SCN" in dec_request:
				if DEBUG: print "Got SCAN command for "+clean_string(dec_request[8:-4])
				new_ticket = Ticket(Ticket.TYPE_SCAN, clean_string(dec_request[8:-4]))
				send_end(self.connection, self.gpg.encrypt("CLNT_SCN"+new_ticket.get_ticket_id()))
				self.placebo.new_ticket_arrived(new_ticket)
			elif "CLNT_VSU" in dec_request:	
				if DEBUG: print "Got UPDATE command"
				new_ticket = Ticket(Ticket.TYPE_UPDATE)
				send_end(self.connection, self.gpg.encrypt("CLNT_VSU"+new_ticket.get_ticket_id()))
				self.placebo.new_ticket_arrived(new_ticket)
			elif "CLNT_PIG" in dec_request:
				if DEBUG: print "Got PING/PONG command"
				send_end(self.connection, self.gpg.encrypt("CLNT_POG"))
			elif "CLNT_GET" in dec_request:
				param = dec_request[8:-4]
				if DEBUG: print "Got GET command for "+param
				try:
					val = CONFIG[param]
					if val:
						send_end(self.connection, self.gpg.encrypt("CLNT_GET"+val))
					else:
						send_end(self.connection, self.gpg.encrypt("CLNT_401"))
				except:
					send_end(self.connection, self.gpg.encrypt("CLNT_999"))
			elif "CLNT_SET" in dec_request:
				if DEBUG: print "Got SET command"
				param=dec_request[8:].split("=")[0]
				val=dec_request[8:-4].split("=",1)[1]
				#try:
				if 1:
					if CONFIG[param]:
						CONFIG[param] = val
						self.placebo.write_config()
						send_end(self.connection, self.gpg.encrypt("CLNT_000"))
					else:
						send_end(self.connection, self.gpg.encrypt("CLNT_401"))
				#except:
				#	send_end(self.connection, self.gpg.encrypt("CLNT_999"))
					
		self.connection.close()
	

class Listend(Thread):
	def __init__(self, placebo):
		super(Listend, self).__init__()
		self.placebo = placebo
		addr = (CONFIG["LISTEN_ADDR"],int(CONFIG["LISTEN_PORT"]))
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serversocket.bind(addr)
		self.serversocket.listen(1)
		if DEBUG: print "Listend init done!"

	def run(self):
		while 1:
			try:
				connection,address = self.serversocket.accept()
				if DEBUG: print "Got connection from: "+address[0]
				if address[0] == CONFIG["SERVER_ADDR"] or socket.gethostbyaddr(address[0])[0].split(".")[0] == CONFIG["SERVER_ADDR"]:
					new_thread = Listend_Thread(connection, placebo)
					new_thread.start()
				else:
					send_end(connection,"CLNT_999")
					connection.close()
			except:
				self.serversocket.close()
		serversocket.close()
		sys.exit(0)

class Placebo_Server():
	def __init__(self):	
		#try:
		if 1:
			self.gpg = GPG(CONFIG["GPG_HOME_PATH"])
			self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connection.connect((str(CONFIG["SERVER_ADDR"]), int(CONFIG["SERVER_PORT"])))
		#except:
		#	print "ERROR opening connection to server"
		if DEBUG: print "init socket to placebo server"	

	def send_ticket(self, ticket):
		print "sending..."+str(ticket.get_type()) 
		send_end(self.connection, self.gpg.encrypt(str(ticket.get_ticket_id())+str(ticket.get_content())))
		ret = self.gpg.decrypt(recv_end(self.connection))
		if not "SRV_0000" in ret:
			if DEBUG: print "ERROR: Server didn't accept Ticket! Code: "+ret[:8]	
			return False
		return True	

	def close(self):
		#self.connection.close()
		del self

class Clamd():
	def __init__(self):
		try:
			self.cd = pyclamd.ClamdUnixSocket()
			self.cd.ping()
		except pyclamd.ConnectionError:
			self.cd = pyclamd.ClamdNetworkSocket()
			try:
				self.cd.ping()
			except pyclamd.ConnectionError:
				if DEBUG: print "ERROR: Couldn't connect to clamd!"
				raise ValueError('could not connect to clamd server either by unix or network socket')
				del self

	def scan_file(self, path):	
		return self.cd.scan_file(path)

	def destroy(self):
		del self

class Ticket_Sender():
	def __init__(self, ticket):
		self.placebo_server = Placebo_Server()
		self.ticket = ticket
		self.tries = 0

	def send(self):
		ret = self.placebo_server.send_ticket(self.ticket)
		if ret:
			if DEBUG: print "Ticket successfully delivered!"
			self.placebo_server.close()
			self.ticket.set_status(Ticket.TICKET_SEND)
		else:
			if DEBUG: print "Ticket couldn't be delivered!"
			self.ticket.set_status(Ticket.TICKET_DENIED)
			self.ticket.RETRIES = self.ticket.RETRIES + 1


class Ticket_Solver_Thread(Thread):
	def __init__(self, ticket, solver):
		super(Ticket_Solver_Thread, self).__init__()
		self.ticket = ticket
		self.solver = solver

	def run(self):
		if DEBUG: print "Working on ticket..."
		self.ticket.RETRIES = self.ticket.RETRIES + 1
		self.ticket.set_status(Ticket.TICKET_INWORK)

		if self.ticket.get_type() == Ticket.TYPE_SCAN:
			ret = self.scan()
			self.ticket.set_status(Ticket.TICKET_DONE)
			return_string = ""
			for filename, value in ret.iteritems(): 
				return_string = return_string+filename+" : "+str(value[1])+"\n"
		elif self.ticket.get_type() == self.ticket.TYPE_UPDATE:
			return_string = self.update()
			self.ticket.set_status(Ticket.TICKET_DONE)

		self.ticket.set_content(return_string)
		self.ticket.write_to_fs()
		
		if self.ticket.get_status() == self.ticket.TICKET_DONE:
			self.solver.del_thread(self)
			del self

	def scan(self):
		if DEBUG: print "Scanning..."
		try: 
			clamav = Clamd()
			return clamav.scan_file(self.ticket.content)
		except:
			if DEBUG: print "Couldn't connect to clamd!"
			ret_error = {"ERROR":"ERROR", "CODE":"CLNT_100"}
			return ret_error
	
	def update(self):
		if DEBUG: print "Updateing..."
		try:
			if "CONFIG" in CONFIG["CLAMD_SOCKET"]:
				f = open(CONFIG["CLAMD_CONFIG"], "r")
				for line in f:
					if line.startswith("LocalSocket"):
						clamd_socket = line.split(" ")[1]
			else:
				clamd_socket = CONFIG["CLAMD_SOCKET"]

			if "SUDO" in CONFIG["UPDATE_MECHANISM"] and CONFIG["SUDO_USER"] != "":
        			command = "sudo -u "+str(CONFIG["SUDO_USER"])+" freshclam --stdout --quiet --daemon-notify="+str(clamd_socket)
			elif "GROUP" in CONFIG["UPDATE_MECHANISM"]:
        			command = "freshclam --stdout --quiet --daemon-notify="+str(clamd_socket)
			else:
				return "ERROR: Configuration failure for freshclam!"
        		proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        		return proc.communicate()[0]
		except:
			if DEBUG: print "ERROR: "+str(sys.exc_info()[0])
			if DEBUG: print "Check client.conf!"
			return str(sys.exc_info()[0]).split("'")[1]


class Ticket_Solver(Thread):
	TICKETS_TO_SOLVE = []
	SCAN_THREADS = []

	MAX_SCAN_THREADS = 5
	
	def __init__(self):
		super(Ticket_Solver, self).__init__()

	def run(self):
		while 1:
			if len(self.TICKETS_TO_SOLVE) > 0:
				for ticket in self.TICKETS_TO_SOLVE:
					print str(ticket.get_ticket_id())+" -> "+str(ticket.get_status())
					if ticket.get_status() == Ticket.TICKET_INWORK:
						#Ignore ticketes which are in work
						continue
					elif ticket.get_status() == Ticket.TICKET_SEND:
						#Remove send tickets
						if ticket.destroy() == 0:
							self.TICKETS_TO_SOLVE.remove(ticket)
							continue
					elif ticket.get_status() == Ticket.TICKET_DONE:
						#Don't do anything if ticket is beeing solved
						for running_ticket in self.SCAN_THREADS:
							if running_ticket.get_ticket_id() == ticket.get_ticket_id(): 
								print "Ignore "+ticket.get_ticket_id()
								continue

						sender = Ticket_Sender(ticket)
						sender.send()
					elif ticket.get_status() == Ticket.TICKET_WAITING:
						#Check for duplicate scans/updates
						for item in self.TICKETS_TO_SOLVE:
							if item.get_content() == ticket.get_content() and ticket != item:
								print "Found duplicate..."
								ticket.set_content("CLNT_100")
								ticket.set_status(Ticket.TICKET_DONE)
								ticket.write_to_fs()
								continue
						self.add_thread(ticket)
					elif ticket.get_status() == Ticket.TICKET_ERROR:
						#FIXME: Retry on error
						if ticket.RETRIES <= 3:
							ticket.set_status(Ticket.TICKET_WAITING)
							continue
						else:
							#Ticket couldn't be send to server.. need timeout for that :/
							if (int(time.time()) - ticket.get_timestamp()) > (10 * ticket.RETRIES):
								sender = Ticket_Sender(ticket)
								sender.send()
								ticket.set_timestamp()
					elif ticket.get_status() == Ticket.TICKET_DENIED:
						if ticket.destroy() == 0:
							self.TICKETS_TO_SOLVE.remove(ticket)
							continue
					else:
						continue
					time.sleep(1)
			time.sleep(2)

	def del_thread(self, thread):
		self.SCAN_THREADS.remove(thread)

	def add_thread(self, ticket):	
		if self.MAX_SCAN_THREADS >= len(self.SCAN_THREADS):
			solver_thread = Ticket_Solver_Thread(ticket, self)
			self.SCAN_THREADS.append(solver_thread)
			solver_thread.start()
	
	def add_ticket(self, ticket):
		self.TICKETS_TO_SOLVE.append(ticket)
		return 0

class Placebo(Thread):
	def __init__(self):
		super(Placebo, self).__init__()
		self.parse_config()

		self.ticket_solver = Ticket_Solver()
		self.ticket_solver.start()

		if os.path.exists(CONFIG["TICKET_PATH"]):
			self.parse_ticket_files()
		else:
			print "ERROR: TICKET_PATH '"+CONFIG["TICKET_PATH"]+"'doesn't exist. Check /etc/placebo/client.conf or create dir"
			sys.exit(1)

		listend = Listend(self)
		listend.start()
	
		if DEBUG: print "Init done!"

	def parse_config(self):
		self.config = {}
		try:
			conf_file = open("/etc/placebo/client.conf", "r")
		except:
			print "ERROR: Couldn't open /etc/placebo/client.conf"
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
	
	def parse_ticket_files(self):
		for file in os.listdir(CONFIG["TICKET_PATH"]): 
			print file
			is_status = True
			status = 0
			content = ""
			f = open(CONFIG["TICKET_PATH"]+"/"+file, "r")
			for line in f:
				if line or line != "":
					if is_status: 
						status = int(line.split("\n")[0])
						is_status = False
					else:
						content = content+line
			if status == Ticket.TICKET_INWORK: status = Ticket.TICKET_WAITING
			old_ticket = Ticket(type=int(file.split(".")[0]), content=content, status=status, id=file.split(".")[1])	
			self.new_ticket_arrived(old_ticket)
	
	def write_config(self):
		try:
			conf_file = open("/etc/placebo/client.conf", "wb")
		except:
			if DEBUG: print "Couldn't open config file.."
			return 1
		
		if DEBUG: print "Writing config..."
		for key, val in CONFIG.iteritems():
			conf_file.write(key+' = "'+val+'"\n')
		conf_file.close()
		return 0
		
	
	def run(self):
		while 1:
			time.sleep(1)

	def new_ticket_arrived(self, ticket):
		self.ticket_solver.add_ticket(ticket)
		
if __name__ == "__main__":
	placebo = Placebo()
	placebo.start()
	
	gpg = GPG(CONFIG["GPG_HOME_PATH"])
	if not gpg.get_key() or not gpg: 
		print "ERROR: No GPG-Key found! See /etc/placebo/client.conf or generate key!"
		sys.exit(0)

	#testing code
	#newTicket = Ticket(Ticket.TYPE_SCAN, "/tmp")
	#placebo.new_ticket_arrived(newTicket)

	while 1:
		try:
			time.sleep(1)
		except:
			sys.exit(0)


