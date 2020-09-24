#!/bin/sh
echo "Content-type: text/plain"
echo ""
GROUPID=$(uci -q get wireless.@wifi-iface[0].ssid)
CHANNEL=$(uci -q get wireless.@wifi-device[0].channel)
TXPOWER=$(uci -q get wireless.@wifi-device[0].txpower)
[ -z $TXPOWER ] && TXPOWER=30
echo $GROUPID";"$CHANNEL";"$TXPOWER
