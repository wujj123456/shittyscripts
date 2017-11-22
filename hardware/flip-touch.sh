#!/bin/bash

touchpad=$(xinput list | grep TouchPad | cut -d'=' -f 2 | cut -d'	' -f 1)

if [ ! -z $1 ] && [ $1 -eq 1 ]; then
	xinput enable $touchpad
else
	xinput disable $touchpad
fi
