#!/bin/ash

CONFERENCE=$1
shift

#loop through additional filetypes and append
while [ $# -gt 0 ]
do

	echo "Channel: $1" > /tmp/callfile.txt
	echo "CallerID: 110" >> /tmp/callfile.txt
	echo "Context: pots" >> /tmp/callfile.txt
	echo "Application: ConfBridge" >> /tmp/callfile.txt
	echo "Data: $CONFERENCE,silent_bridge,silent_user" >> /tmp/callfile.txt
	/bin/mv /tmp/callfile.txt /tmp/spool/asterisk/outgoing/

	shift

done

