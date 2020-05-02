#!/bin/ash

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

mkdir -p restarter_logs
rm restarter_logs/*
rm restarter_log.txt

while :
do  
    sleep 10

    SUB_PID=`cat $SCRIPTPATH/tmp/subscribe_daemon.pid`
    PUB_PID=`cat $SCRIPTPATH/tmp/publish_daemon.pid`

    DATE=$(date '+%Y-%m-%dT%H%M')

    if kill -s 0 $SUB_PID &>/dev/null
    then
        echo 'ok' > /dev/null
    else
        echo "does not exist $SUB_PID"
        cp log.txt $SCRIPTPATH/restarter_logs/log_$DATE
        $SCRIPTPATH/run_daemon.sh restoreSubscriber
    fi

    if kill -s 0 $PUB_PID &>/dev/null
    then
        echo 'ok' > /dev/null
    else
        echo "does not exist $PUB_PID"
        cp log.txt $SCRIPTPATH/restarter_logs/log_$DATE
        $SCRIPTPATH/run_daemon.sh restorePublisher
    fi
done