#!/bin/bash

function remote {
	ip=$1
	port=$2
	commands=$3

	# check online
	nc -z -w 1 $ip $port
	if [ $? -ne 0 ]; then
		echo "==================="
		echo "$ip:$port offline"
		echo "==================="
		echo
		return
	fi

	echo "==================="
	ssh -p $port $ip "hostname"
	echo "==================="
	echo

	if [ -z "$commands" ]; then
		ssh -p $port $ip "/home/wujj/shittyscripts/boinc/boinc_state.py; echo; sensors | egrep 'Core|Tdie'; echo; nvidia-smi dmon -c 1"
	else
		ssh -p $port $ip "$commands"
	fi
	echo
}

echo "==================="
echo $HOSTNAME
echo "==================="
echo

/home/wujj/shittyscripts/boinc/boinc_state.py
echo
ps -eo pid,comm,cputimes | awk '$3 > 43200 {print $1 " " $2 " " $3}'
echo
sensors | egrep 'Core|Tdie'
echo
