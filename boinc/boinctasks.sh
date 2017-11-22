#!/bin/bash

# script that controls scheduling between two BOINC projects

SETI='http://setiathome.berkeley.edu/'
WCG='http://www.worldcommunitygrid.org/'
PROJECT_URL=$SETI

num_active_tasks=$(boinccmd --get_tasks | grep "  state:" | grep downloaded | wc -l)
num_fetching_projects=$(boinccmd --get_simple_gui_info | grep "don't request more work: no" | wc -l)
num_projects=$(boinccmd --get_simple_gui_info | grep "don't request more work:" | wc -l)

echo "[$(date --rfc-3339=seconds)] Tasks: $num_active_tasks Fetching projects: $num_fetching_projects/$num_projects"

#day=$(date +%u)
#hour=$(date +%H)
#if [ $day -ge 1 ] && [ $day -lt 6 ] && [ $hour -ge 7 ] && [ $hour -lt 21 ]; then
#	if [ $num_fetching_projects -gt 0 ]; then
#		echo "Disable fetching for all projects"
#		boinccmd --project $WCG nomorework
#		boinccmd --project $SETI nomorework
#	fi
if [ $num_fetching_projects -eq 0 ]; then
	echo "Enable fetching for $WCG"
	boinccmd --project $WCG allowmorework
else
	if [ $num_active_tasks -ge 32 ]; then
		if [ $num_projects -eq $num_fetching_projects ]; then
			echo "Disable fetching for $PROJECT_URL"
			boinccmd --project $PROJECT_URL nomorework
		fi
	elif [ $num_active_tasks -le 30 ]; then
		if [ $num_projects -gt $num_fetching_projects ]; then
			echo "Enable fetching for $PROJECT_URL"
			boinccmd --project $PROJECT_URL allowmorework
		fi
	fi
fi
