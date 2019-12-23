#!/bin/sh

#INTERNAL_IP=`ip a | grep 192.168 | grep wlan0 | awk '{print $2}'`
INTERNAL_IP='192.168.43.128/24'
SUBNET=`echo $INTERNAL_IP | cut -d '.' -f 3`

for i in {1..255}
do
    ping '192.168.'+$INTERNAL_IP+'.'+$i
done