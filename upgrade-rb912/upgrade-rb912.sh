#!/bin/bash
FLASH_CHIP1_NAME=gd25d05
FLASH_CHIP2_NAME=w25x05
ROOTFS_DIR=../bin/targets/ar71xx/mikrotik
RAM_FS_NAME=openwrt-ar71xx-mikrotik-vmlinux-initramfs-lzma.elf
ROOTFS_NAME=openwrt-ar71xx-mikrotik-nand-large-ac-squashfs-sysupgrade.bin
sudo mkdir -p /var/www/html/${FLASH_CHIP1_NAME}
sudo mkdir -p /var/www/html/${FLASH_CHIP2_NAME}

sudo cp ${ROOTFS_DIR}/${RAM_FS_NAME} .
sudo cp ${ROOTFS_DIR}/${ROOTFS_NAME} /var/www/html/${FLASH_CHIP1_NAME}/.
sudo cp ./${ROOTFS_NAME} /var/www/html/${FLASH_CHIP2_NAME}/.

sudo killall dnsmasq
sudo ifconfig eth0 169.254.4.200 up
sudo dnsmasq -i eth0 --dhcp-range=169.254.4.100,169.254.4.150 \
--dhcp-boot=${RAM_FS_NAME} \
--enable-tftp --tftp-root=$(pwd) -d -u $USER -p0 -K --log-dhcp --bootp-dynamic



