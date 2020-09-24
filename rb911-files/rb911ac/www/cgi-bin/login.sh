#!/bin/sh
echo "Content-type: text/plain"
echo ""
if [ "x$QUERY_STRING" != "x" ]; then
	PASS=$(/usr/sbin/uhttpd -d $QUERY_STRING)
	#echo $PASS >> /tmp/login.txt
	ORG=$(cat /etc/config/password)
	if [ "$PASS" = "$ORG" ]; then
		echo "OK"
	else
		echo "FAIL"
	fi
fi
