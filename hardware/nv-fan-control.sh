#!/bin/bash

sleep 10s

nvidia-settings -a [gpu:0]/GPUFanControlState=1 > /dev/null
nvidia-settings -a [fan:0]/GPUCurrentFanSpeed=50 > /dev/null
current=50
next=50
temperature=0

logger "$0: script started"

function changeFanSpeed() {
	if [ "$current" != "$1" ]; then
		logger "$0: Setting fan speed to $1% (T: $temperature)"
		nvidia-settings -a [fan:0]/GPUCurrentFanSpeed=$1 > /dev/null
		current=$1
	fi
}

while [ 1 ]
do
	temperature=`nvidia-settings -q [gpu:0]/GPUCoreTemp | grep GPUCoreTemp | head -n 1 | awk -F": " '{print $2}' | sed 's/\.//'`
	temperature=$(($temperature))
	if [ $temperature -gt 62 ];	then
		changeFanSpeed 100
		sleep 1m
	elif [ $temperature -gt 58 ] && [ $temperature -lt 62 ]; then
		changeFanSpeed 80
	elif [ $temperature -gt 55 ] && [ $temperature -lt 58 ]; then
		changeFanSpeed 60
	elif [ $temperature -lt 54 ] && [ "$current" != "50" ]; then
		changeFanSpeed 50
	fi

	sleep 20s
done
