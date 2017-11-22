#!/bin/sh
#
###
### For assistance, please visit forum.ipinfodb.com
#
# Created by Eric Gamache on 2009-05-26
# Version 1.0 by Eric Gamache -- 2009-06-04
# Version 1.1 updated by Marc-Andre Caron -- 2009-06-08 .. Added timezone
# Version 1.2 updated by Eric Gamache -- 2009-06-08 .. fix minors bugs.
# Version 1.3 updated by Marc-Andre Caron -- 2010-02-11 .. new timezone support, reduced complexity of the script.
# Version 1.4 updated by Junjie Wu -- 2012-06-03 .. added api_key and precision support, removed deprecated timezone support.
#
# This script is provided "as is", with absolutely no warranty expressed or
# implied. Any use is at your own risk. Permission to use or copy this
# script for any purpose is hereby granted without fee. Permission to
# modify the code and to distribute modified code is granted, provided
# the above notices are retained, and a notice that the code was modified
# is included with the above copyright notice.
#
###############################################
# Please supply your own API key
# You can get a free API key by registering on http://ipinfodb.com
YOUR_API_KEY=$(cat .iplocate.key)
###############################################
####
####
####
WGET_OPTION="=-b -q --wait=3 --waitretry=2 --random-wait --limit-rate=9578 "
WGET_AGENT="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"
#
ERROR=0
#
###############################################
if [ "$YOUR_API_KEY" = "" ]; then
  echo "Please edit the script to provide YOUR_API_KEY"
  exit
fi
##############
if [ "$1" = "" ]; then
  ERROR=1
else
  IP=$1
fi
##############
if [ "$2" != "" ]; then
  if [ "$2" != "json" ] && [ "$2" != "xml" ] && [ "$2" != "csv" ]; then
    ERROR=1
  fi
  TYPE="$2"
else
  ERROR=1
fi
##############
if [ "$3" != "" ]; then
  if [ "$3" != "city" ] && [ "$3" != "country" ] ; then
    ERROR=1
  fi
  PREC=$3
else
  ERROR=1
fi
###############################################

###############################################
if [ "$ERROR" != "0" ]; then
  echo " "
  echo " usage : $0 IP TYPE PRECISION"
  echo " Where IP is the IP to check"
  echo " TYPE is the output type (csv|xml|json)"
  echo " PRECISION can only be city or country (city|country)"
  echo " Big thanks to the team of IPInfoDB (http://ipinfodb.com)"
  exit
fi
###############################################
#
TST_wget=`wget > /dev/null 2>&1`
#
ErrorLevel=$?
#
if [ "$ErrorLevel" != 1 ] ; then
  echo " ----"
  echo " wget not found; please install it for proper operation."
  echo " ----"
  exit
fi
###############################################
###############################################
#######
#######
URL="http://api.ipinfodb.com/v3/ip-$PREC/?key=$YOUR_API_KEY&ip=$IP&format=$TYPE"
Info=`wget -qO- --user-agent="$WGET_AGENT" "$URL" 2>&1`
echo "$Info"
