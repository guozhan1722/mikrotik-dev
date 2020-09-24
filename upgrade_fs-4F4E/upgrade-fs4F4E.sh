#!/bin/bash
sudo killall dnsmasq
sudo ifconfig eth0 169.254.4.200 up
sudo dnsmasq -i eth0 --dhcp-range=169.254.4.100,169.254.4.150 \
--dhcp-boot=pxelinux.0 \
--enable-tftp --tftp-root=$(pwd) -d -u $USER -p0 -K --log-dhcp --bootp-dynamic
