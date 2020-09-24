#!/bin/sh
echo "Content-type: text/plain"
echo ""
O=$(iwinfo adhoc0 info)
A1=$(echo "$O" | awk '/Signal/ {printf "%d;%d;",-1*$2,-0.85*$5}')
A2=$(echo "$O" | awk '/Link Quality/ {gsub(/\//," "); printf "%d", 100-($6*100/$7)}')
echo $A1$A2