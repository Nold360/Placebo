# -*- coding: utf-8 -*-
import string,subprocess,uuid,os,time
import gnupg

#####################################################################################
#
# Placebo Shared Library 
#
#####################################################################################


#####################################################################################
#Thanks to John Nielsen
#http://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
#####################################################################################
End='EndOFTransmission'
def recv_end(the_socket):
	total_data=[];data=''
	while True:
		data=the_socket.recv(8192)
		if End in data:
			total_data.append(data[:data.find(End)])
			break
		if len(data) > 0:
			total_data.append(data)
		if len(total_data)>1:
			#check if end_of_data was split
			last_pair=total_data[-2]+total_data[-1]
			if End in last_pair:
				total_data[-2]=last_pair[:last_pair.find(End)]
				total_data.pop()
				break
	return ''.join(total_data)

#####################################################################################
# Sends data to socket and adds the "End" String for recv_end
#####################################################################################
def send_end(the_socket, data):
	the_socket.send(data+End)
	return 0

	
#####################################################################################
# Cleans a String from whitespaces
#####################################################################################
def clean_string(oldString):
	newString = []
	for char in oldString:
		if char not in string.whitespace: newString.append(char)
	return ''.join(newString)

class GPG():
	def __init__(self, gpg_home_dir,client=True, hostname=None):
		if client:
			self.import_key_string = "Placebo Server"
			self.export_key_string = "Placebo Client"
			self.hostname = "Placebo Server"
		else:
			if not hostname: return None
			self.hostname = hostname
			self.import_key_string = hostname 
			self.export_key_string = "Placebo Server"
                
		if 1:
		#try:
			self.gpg_home_dir = gpg_home_dir
			self.gpg = gnupg.GPG(gnupghome=gpg_home_dir)
			#if not self.hostname: hostname = self.import_key_string
			#else: hostname = self.hostname
			#self.fingerprint = ""
               		#for item in self.gpg.list_keys():
               		#        if hostname in str(item["uids"]):
               		#                self.fingerprint = item["fingerprint"]
               		#if self.fingerprint == "": self.fingerprint = hostname
			#self.gpg.encoding = 'utf-8'
		#except e:
	#		print "ERROR: Couldn't connect to GPG instance!"
	#		del self

	def gen_key(self):
		for key in self.gpg.list_keys(True):
			for content in key:
				if self.export_key_string in content:
					return -1
			
		input = self.gpg.gen_key_input(key_type="DSA", key_length=2048, name_real=socket.gethostname(), name_comment=self.export_key_string)
		self.gpg.gen_key(input)
		return 0

	def import_key(self, key):
		command = "gpg --homedir "+self.gpg_home_dir+" --list-keys 'Placebo Server' &> /dev/null"
		proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

		if proc.communicate()[0] != 0:
			command = "gpg --no-verbose --quiet --batch -a --import << EOF\n"+str(key)+"EOF"
			proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
			
			#FIXME
			#return proc.communicate()[0]	
			return 0
		else:
			return 1

	#FIXME
	def import_key_not_working(self, key):
		for key in self.gpg.list_keys():
			for content in key:
				if self.import_key_string in content:
					return -1

		return self.gpg.import_keys(key)

	def get_key(self):
		return self.gpg.export_keys(self.export_key_string)

	def encrypt(self, msg):
		#FIXME
		#enc_msg = self.gpg.encrypt(msg, fp)
		command = "gpg  --homedir "+self.gpg_home_dir+" --batch --quiet --always-trust --encrypt -a -r \""+str(self.hostname)+"\"<< EOF\n"+str(msg)+"EOF"
        	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        	enc_msg = proc.communicate()[0]
		return enc_msg

	def decrypt(self, enc_msg):
		#FIXME
		command = "gpg  --homedir "+self.gpg_home_dir+" --batch --quiet --decrypt -a -r $(hostname) << EOF\n"+enc_msg+"EOF"
		proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		msg = proc.communicate()[0]
		return msg

	def destroy(self):
		del self

class Ticket():
        TYPE_SCAN = 0
        TYPE_UPDATE = 1

        TICKET_DONE = 0
        TICKET_ERROR = 1
        TICKET_TIMEOUT = 2
        TICKET_WAITING = 3
        TICKET_INWORK = 4
	TICKET_DENIED = 5
        TICKET_SEND=255

        RETRIES = 0
	TIMESTAMP = 0

	TICKET_PATH = "/var/placebo/tickets"

        def __init__(self, type, content=None, status=None, id=None, TICKET_PATH="/var/placebo/tickets"):
                self.type = type
                self.content = content
		self.TICKET_PATH = TICKET_PATH

                if not id: self.id = uuid.uuid4()
                else: self.id = id

                if not status: self.status = self.TICKET_WAITING
                else: self.status = status

                if not id: self.write_to_fs()
		self.set_timestamp()

        def get_status(self):
                return self.status

        def get_ticket_id(self):
                return str(self.id)

        def get_content(self):
                return self.content

        def get_type(self):
                return self.type

	def get_timestamp(self):
		return int(self.TIMESTAMP)

	def set_timestamp(self):
		self.TIMESTAMP = int(time.time())

        def write_to_fs(self):
                ticket_file = open(self.TICKET_PATH+"/"+str(self.type)+"."+str(self.id), "w")
                ticket_file.write(str(self.get_status())+'\n'+str(self.get_content()))
                ticket_file.close()

        def set_content(self, new_content):
                self.content = new_content
		self.set_timestamp()

        def set_status(self, status):
                self.status = status
		self.set_timestamp()

        def destroy(self):
                os.remove(self.TICKET_PATH+"/"+str(self.type)+"."+str(self.id))
                del self
                return 0

