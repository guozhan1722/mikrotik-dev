#!/bin/bash

KER_DIR=../bin/targets/ar71xx/mikrotik
KER_NAME=Teletics-RB411-upgrade-kernel.bin
cp ${KER_DIR}/${KER_NAME} /var/www/html/.

sudo killall dnsmasq
sudo ifconfig eth0 169.254.4.200 up
sudo dnsmasq -i eth0 --dhcp-range=169.254.4.100,169.254.4.150 \
--dhcp-boot=old_openwrt-ar71xx-mikrotik-vmlinux-initramfs-lzma.elf \
--enable-tftp --tftp-root=$(pwd) -d -u $USER -p0 -K --log-dhcp --bootp-dynamic 

