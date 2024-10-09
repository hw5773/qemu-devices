#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run with the root privilege"
  exit
fi

if [ $# -ne 1 ]; then
  echo "Illegal number of parameters"
  echo "Run this script with the name of the main interface"
  echo "ex) ./setting.sh eth0"
  exit
fi
ip link add internet type bridge
ip addr add 172.31.0.1/16 dev internet
apt-get install dnsmasq
dnsmasq --interface=internet --except-interface=$1 --bind-interfaces --listen-address=172.31.0.1 --dhcp-range=172.31.0.2,172.31.255.255,12h --port=0
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o $1 -j MASQUERADE
iptables -A FORWARD -i $1 -o internet -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i internet -o $1 -j ACCEPT
