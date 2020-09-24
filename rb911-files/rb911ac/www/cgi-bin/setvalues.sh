#!/bin/sh
echo "Content-type: text/plain"
echo ""
if [ "x$QUERY_STRING" != "x" ]; then
	V=$(/usr/sbin/uhttpd -d $QUERY_STRING)
	#echo "$V" >> /tmp/log.txt
	GROUPID=$(echo $V | awk -F";" '{print $1}')
	CHANNEL=$(echo $V | awk -F";" '{print $2}')
	TXPOWER=$(echo $V | awk -F";" '{print $3}')
	PASSWORD=$(echo $V | awk -F";" '{print $4}')

	uci set wireless.@wifi-iface[0].ssid=$GROUPID
	uci set wireless.@wifi-device[0].channel=$CHANNEL
	uci set wireless.@wifi-device[0].txpower=$TXPOWER
	uci commit wireless
	if [ "$PASSWORD" != "--empty--" ]; then
		echo "$PASSWORD" > /etc/config/password
	fi
	reboot
fi
