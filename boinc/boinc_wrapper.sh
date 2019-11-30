#!/bin/bash

CONF="/etc/boinc-client/global_prefs_override.xml"

if [ $# -lt 1 ]; then
	exit 1
fi

xmlstarlet ed -O -L -u "/global_preferences/max_ncpus_pct" --value 50.0 $CONF
boinccmd --read_global_prefs_override

$@

xmlstarlet ed -O -L -u "/global_preferences/max_ncpus_pct" --value 100.0 $CONF
boinccmd --read_global_prefs_override
