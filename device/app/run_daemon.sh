#!/bin/ash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

mkdir -p tmp

startDaemon()
{    
    FILE=$SCRIPTPATH/$1'_daemon.pid'
    if [ -f "$FILE" ]; then
        echo "Daemon $1 is already started! Stop or restart process."
    else 
        echo "Starting $1 daemon..."
        echo "Starting $1 daemon..." >> $SCRIPTPATH/log.txt
        #startuojam publish deamona
        nohup $SCRIPTPATH/$1.lua >> $SCRIPTPATH/log.txt 2>&1 &

        #issaugom PID i tmp faila
        echo $! > $SCRIPTPATH/tmp/$1'_daemon.pid'
        echo "Daemon $1 $! is started."
        echo "Daemon $1 $! is started." >> $SCRIPTPATH/log.txt
    fi
}

stopDaemon()
{    
    FILE=$SCRIPTPATH/tmp/$1'_daemon.pid'
    if [ -f "$FILE" ]; then
        echo "Stopping $1 daemon..."
        echo "Stopping $1 daemon..." >> $SCRIPTPATH/log.txt
        
        PID=`cat $SCRIPTPATH/tmp/$1'_daemon.pid'`
        #killinam procesa
        kill -9 $PID
        
        if [ $? -eq 0 ]; then
            #istrinam PID faila
            echo "$1 Daemon $PID is stopped." 
            echo "$1 Daemon $PID is stopped." >> $SCRIPTPATH/log.txt
        fi  
        rm $SCRIPTPATH/tmp/$1'_daemon.pid'
    else       
        echo "Daemon $1 is not started! Start process."
        echo "Daemon $1 is not started! Start process." >> $SCRIPTPATH/log.txt
    fi
}

startRestarter()
{    
    FILE=$SCRIPTPATH/tmp/restarter_daemon.pid
    if [ -f "$FILE" ]; then
        echo "Restarter daemon is already started! Stop or restart process."
    else 
        echo "Starting Restarter daemon ..."
        echo "Starting Restarter daemon ..." >> $SCRIPTPATH/log.txt
        #startuojam publish deamona
        nohup $SCRIPTPATH/restarter.sh >> $SCRIPTPATH/restarter_log.txt 2>&1 &

        #issaugom PID i tmp faila
        echo $! > $SCRIPTPATH/tmp/restarter_daemon.pid
        echo "Restarter daemon  $! is started."
        echo "Restarter daemon  $! is started." >> $SCRIPTPATH/log.txt
    fi
}

stopRestarter()
{    
    FILE=$SCRIPTPATH/tmp/restarter_daemon.pid
    if [ -f "$FILE" ]; then
        echo "Stopping restarter daemon..." >> $SCRIPTPATH/log.txt
        
        PID=`cat $SCRIPTPATH/tmp/restarter_daemon.pid`
        #killinam procesa
        kill -9 $PID
        
        if [ $? -eq 0 ]; then
            #istrinam PID faila
            echo "Restarter daemon $PID is stopped." 
            echo "Restarter daemon $PID is stopped." >> $SCRIPTPATH/log.txt
        fi  
        rm $SCRIPTPATH/tmp/restarter_daemon.pid
    else       
        echo "Daemon restarter is not started! Start process." >> $SCRIPTPATH/log.txt
    fi
}

startBothDaemons()
{        
    startDaemon "publish"
    sleep 5
    startDaemon "subscribe"

    startRestarter
}

stopBothDaemons()
{    
    stopRestarter

    stopDaemon "publish"
    stopDaemon "subscribe"
}

restorePublisher()
{
    stopDaemon "publish" 
    startDaemon "publish"
}

restoreSubscriber()
{
    stopDaemon "subscribe" 
    startDaemon "subscribe"
}

restartDaemons()
{
    #pakeiciam working directory i skripto vieta ir istrinam senus logus, kad neissipustu
    cd $SCRIPTPATH
    rm $SCRIPTPATH/log.txt
    
    #BROKER_IP=`cat $SCRIPTPATH/config.conf | grep ip= | awk -F= '{print $2}'`

    #patikrinam, ar yra interneto rysys
    while ! ping -c 1 -W 1 8.8.8.8 > /dev/null 2>&1; do
        echo "Waiting for ping. Network interface might be down..." 
        echo "Waiting for ping (8.8.8.8). Network interface might be down..." >> $SCRIPTPATH/log.txt
        sleep 5
    done

    #restartinam
    stopBothDaemons
    startBothDaemons

    #programu atstatytojas
    stopRestarter
    startRestarter
}

if [ $# == 1 ]
then
    case $1 in
        'start')  startBothDaemons;;
        'stop')   stopBothDaemons;;
        'restart')    restartDaemons;;
        'restorePublisher') restorePublisher;;
        'restoreSubscriber') restoreSubscriber;;
    esac
else
    echo "Use start|stop|restart"
fi