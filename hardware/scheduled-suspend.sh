#!/bin/bash -e

if [ $# -ne 1 ]; then
	echo "Usage: $0 <delay before wake up>"
	exit 1
fi

if [ $(whoami) != 'root' ]; then
	echo "Must run with sudo or root"
	exit 1
fi	

delay=$1
wakeup=$(date +%s -d+$delay)

echo $wakeup > /sys/class/rtc/rtc0/wakealarm
systemctl suspend
