#!/bin/bash

CONF="/etc/boinc-client/global_prefs_override.xml"

if [ $# -lt 2 ]; then
	echo "Usage: $0 <ncpus_to_yield> <command ...>"
	exit 1
fi

re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
	echo "$1 is not a positive integer"
	echo "Usage: $0 <ncpus> <command ...>"
	exit 1
fi
YIELD_CPUS=$1
shift

function read_cur_info() {
	CUR_PCT=$(xmlstarlet sel -t -m "/global_preferences/max_ncpus_pct" -v . $CONF)
	CUR_CPUS=$(python3 -c "print(round(($CUR_PCT * $NCPUS)/100))")
}

NCPUS=$(cat /proc/cpuinfo | grep processor | wc -l)
read_cur_info

if [[ $YIELD_CPUS -gt $CUR_CPUS ]]; then
	echo "Can't yield $YIELD_CPUS from $CUR_CPUS CPUs"
	exit 1
fi

TARGET_PCT=$(bc <<< "scale=4; ($CUR_CPUS - $YIELD_CPUS) * 100 / $NCPUS")
echo "Yielding $YIELD_CPUS cores. Setting from $CUR_PCT % to $TARGET_PCT %"

function restore() {
	read_cur_info
	TARGET_PCT=$(bc <<< "scale=4; ($CUR_CPUS + $YIELD_CPUS) * 100 / $NCPUS")
	echo "Restoring fraction from $CUR_PCT % to $TARGET_PCT %"
	xmlstarlet ed -O -L -u "/global_preferences/max_ncpus_pct" --value $TARGET_PCT $CONF && boinccmd --read_global_prefs_override
}

xmlstarlet ed -O -L -u "/global_preferences/max_ncpus_pct" --value $TARGET_PCT $CONF && boinccmd --read_global_prefs_override
trap 'restore' EXIT
$@
