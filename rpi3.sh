#!/bin/bash

if [ $EUID -ne 0 ]; then
  echo "Please run this script with the root privilege"
  exit
fi

if [ $# -ne 1 ]; then
  echo "Illegal number of parameters"
  echo "Run this script with the serial number"
  echo "ex) ./rpi.sh 1"
  exit
fi

ip tuntap add victim-tap$1 mode tap
ip link set victim-tap$1 up
iptables -t filter -I FORWARD 1 -i victim-tap$1 -o victim-tap$1 -j ACCEPT
ip link set victim-tap$1 master internet

wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/native-emulation/dtbs/bcm2710-rpi-3-b-plus.dtb
wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/native-emulation/5.4.51%20kernels/kernel8.img
wget https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2020-08-24/2020-08-20-raspios-buster-arm64.zip
unzip 2020-08-20-raspios-buster-arm64.zip
rm 2020-08-20-raspios-buster-arm64.zip
qemu-img resize 2020-08-20-raspios-buster-arm64.img 4G

qemu-system-aarch64 -machine raspi3b -cpu cortex-a7 -smp 4 -m 1G -dtb bcm2710-rpi-3-b-plus.dtb -kernel kernel8.img -drive file=2020-08-20-raspios-buster-arm64.img,format=raw -serial stdio -display none -device usb-net,netdev=network$1,mac=2b:c7:bb:80:ca:28 -netdev tap,id=network$1,ifname=victim-tap$1,script=no,downscript=no -append 'rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1'
