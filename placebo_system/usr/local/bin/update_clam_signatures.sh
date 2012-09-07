#!/bin/bash

vsig_server="http://uscesx07/clamav/vsig"

rm  /var/lib/clamav/files.list 2> /dev/null
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
exit 0
