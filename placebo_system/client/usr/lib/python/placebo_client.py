#!/usr/bin/env python

import string, sys, subprocess

def clean_string(oldString):
        newString = []
        for char in oldString:
                if char not in string.whitespace: newString.append(char)
        return ''.join(newString)

#####################################################################################
# Reads Config and returns a fitting parameter or -1
#####################################################################################
def get_config_parameter(parameter):
        conf_file = open("/etc/placebo/client.conf", "r")
        for line in conf_file:
                if line[0] != "#":
                        if line.find(parameter) != -1:
                                conf_file.close()
                                return str(str(line.split("=")).split("\"")[1])
        conf_file.close()
        return -1


#####################################################################################
# Decrypts a message using the Private Keypair
#####################################################################################
def decrypt(enc_msg):
        command = "gpg --batch --quiet --decrypt << EOF\n"+enc_msg+"EOF"
        proc =  subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Encrypts a message using the "Placebo Server"'s PublicKey
#####################################################################################
def encrypt(msg):
        command = "gpg --batch --quiet --encrypt -a -r \"Placebo Server\"<< EOF\n"+str(msg)+"EOF"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Executes a clamscan on <path>
#####################################################################################
def scan_file(path):
        command = "clamscan -i -r "+path
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


def update_virus_signatures():
        command = "/usr/local/bin/update_clam_signatures.sh"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]

def new_host_request():
        command = "gpg --batch --quiet --export -a $(hostname)"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        key = proc.communicate()[0]
        return encrypt("CLNT_NEW"+key)

def add_public_key(key):
	command = "gpg  --no-verbose --quiet --batch -a --import << EOF\n"+str(key)+"EOF"
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]	

def process_exists(string):
	command = "ps -ef | grep '"+string+"' | grep -v grep"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]

