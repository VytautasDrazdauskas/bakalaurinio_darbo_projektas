#!/bin/bash

while getopts m:i: option
do
case "${option}"
in
m) MAC=${OPTARG};;
i) IP=${OPTARG};;
esac
done

if [ -z "$MAC" ] && [ -z "$IP" ]
then
    echo "Provide MAC and IP"
else
    echo "Downloading $MAC keys"
    scp vytdra@35.228.206.255:~/int_app/device_keys/$MAC ./aeskey.key
    scp vytdra@35.228.206.255:~/int_app/device_certs/$MAC/client.crt .
    scp vytdra@35.228.206.255:~/int_app/device_certs/$MAC/client.key .
    scp vytdra@35.228.206.255:~/server-certs/ca.crt .

    echo "Transfering keys $MAC device keys to $IP"
    scp aeskey.key client.key client.crt ca.crt root@$IP:~/device_app/certs
    rm ca.crt client.* aeskey.key
fi