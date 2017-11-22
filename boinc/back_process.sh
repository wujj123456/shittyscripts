#!/bin/bash

sendmail=1
client=off
owner=root

function ondie() {
	if [ "$client" = "on" ]; then
		cd ~/Private/BOINC
		./boinccmd --quit
		client=off
	fi
	if [ $sendmail -eq 1 ]; then
#		cat client.log | mail -s "Client Shutdown" wujj@umich.edu
		machine=`hostname` && ssh -p 3222 wujj.selfip.com "DISPLAY=:0 notify-send \"$machine rebooted\""
	fi
	exit 0
}

trap 'sendmail=0; ondie' INT
trap 'ondie' TERM EXIT

cd ~/Private/BOINC
pwd

while [ 1 ]
do
	owner=`w -h | grep -v wujj`

	if [ "$owner" = "" ] && [ "$client" = "off" ]; then
		# launch process
		echo "application launching"
		hostname > client.log
		./run_client | tee -a client.log &
		machine=`hostname` && ssh -p 3222 wujj.selfip.com "DISPLAY=:0 notify-send \"Job on $machine started\""
		client=on
	elif [ "$owner" != "" ] && [ "$client" = "on" ]; then
		# shutdown
		echo "application shutdown"
		cd ~/Private/BOINC
		./boinccmd --quit
		machine=`hostname` && ssh -p 3222 wujj.selfip.com "DISPLAY=:0 notify-send \"Job on $machine stopped\""
		client=off
	elif [ "$owner" != "" ] && [ "$client" = "off" ]; then
		# notify again
		machine=`hostname` && ssh -p 3222 wujj.selfip.com "DISPLAY=:0 notify-send \"Job on $machine stopped\""
		sleep 5m
	fi

	sleep 8s

done
