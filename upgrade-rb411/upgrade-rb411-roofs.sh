#!/bin/bash

ROOTFS_DIR=../bin/targets/ar71xx/mikrotik
ROOTFS_NAME=Teletics-RB411-upgrade-rootfs.bin
cp ${ROOTFS_DIR}/${ROOTFS_NAME} /var/www/html/.

sudo killall dnsmasq
sudo ifconfig eth0 169.254.4.200 up
sudo dnsmasq -i eth0 --dhcp-range=169.254.4.100,169.254.4.150 \
--dhcp-boot=openwrt-ar71xx-mikrotik-vmlinux-initramfs-lzma.elf \
--enable-tftp --tftp-root=$(pwd) -d -u $USER -p0 -K --log-dhcp --bootp-dynamic 

