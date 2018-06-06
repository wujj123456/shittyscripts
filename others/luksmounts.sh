#!/bin/bash

if [ $(whoami) != 'root' ]; then
	echo "This script requires root permission"
	exit 1
fi

# media directory
cryptsetup open /dev/sda1 hdd1 --key-file /home/wujj/.lukskeyfile
mount /dev/mapper/hdd1 /mnt/hdd1

# pxe directory
cryptsetup open /data/pxe.img pxe --key-file /home/wujj/.lukskeyfile
mount /dev/mapper/pxe /mnt/pxe
systemctl restart tftpd-hpa
systemctl restart nfs-kernel-server
