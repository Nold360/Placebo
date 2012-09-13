#!/bin/bash

if [ $UID != 0 ] ; then
	echo "You must be root!"
	exit 1
fi

	if [ "$1" == "" ] ; then
	vsig_server=$(grep vsig_server /etc/placebo/client.conf | cut -f2 -d"\"")

	rm  -f /var/lib/clamav/files.list 2> /dev/null
	wget -N -nv $vsig_server/files.list -O /var/lib/clamav/files.list 2> /dev/null

	IFS=$'\n'
	for file in $(cat /var/lib/clamav/files.list); do
		rm "/var/lib/clamav/$(echo $file | awk '{print $2}')"
		wget  "$vsig_server/$(echo $file | awk '{print $2}')" -O "/var/lib/clamav/$(echo $file | awk '{print $2}')"  2> /dev/null
	done

	cd=$(pwd)
	cd /var/lib/clamav/
	md5sum --quiet -c "/var/lib/clamav/files.list"
	cd $cd

	for file in $(ls -1 /var/lib/clamav/*.cvd); do 
		echo -n "$(basename $file);" 
		stat -c "%x" $file | cut -f1 -d. 
	done
	
elif [ "$1" == "INTERNET" ] ; then
	wget http://db.local.clamav.net/main.cvd -O /var/lib/clamav/main.cvd &> /dev/null
	wget http://db.local.clamav.net/daily.cvd -O /var/lib/clamav/daily.cvd &> /dev/null
	wget http://db.local.clamav.net/bytecode.cvd -O /var/lib/clamav/bytecode.cvd &> /dev/null
	wget http://db.local.clamav.net/safebrowsing.cvd -O /var/lib/clamav/safebrowsing.cvd &> /dev/null

	for file in $(ls -1 /var/lib/clamav/*.cvd); do 
		echo -n "$(basename $file);" 
		stat -c "%x" $file | cut -f1 -d. 
	done
fi
exit 0
