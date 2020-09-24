#!/bin/ash

echo "Channel: SIP/$1" > "/opt/teletics/testfiles/$1.txt"
echo "CallerID: $1" >> "/opt/teletics/testfiles/$1.txt"
echo "Context: pots" >> "/opt/teletics/testfiles/$1.txt"
echo "Extension: 5432" >> "/opt/teletics/testfiles/$1.txt"
