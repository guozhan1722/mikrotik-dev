#!/bin/ash

case $# in
1)
  case $1 in
  [1-9]*)
        #echo
        #echo Systems active in subnet: $1
        K=11
        while [ $K -lt 31 ]; do
        # grep -v delivers 0 on no matches
                #echo -ne "testing:" $1$K "...    \r"
                (if ping -c 1 -w 1 -n $1$K 2>&1 | grep -q '64 bytes' ; then
                echo $1$K "                "
                fi) &
                K=$((K + 1))
        done
        #sleep 1
        exit 0
        ;;
  esac;;
esac