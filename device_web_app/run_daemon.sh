#!/bin/ash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

mkdir -p tmp

startDaemon()
{    
    FILE=$SCRIPTPATH/'daemon.pid'
    if [ -f "$FILE" ]; then
        echo "Daemon is already started! Stop or restart process."
    else 
        echo "Starting daemon..."
        echo "Starting daemon..." >> $SCRIPTPATH/log.txt
        #startuojam publish deamona
        nohup python $SCRIPTPATH/app/__init__.py >> $SCRIPTPATH/log.txt 2>&1 &

        #issaugom PID i tmp faila
        echo $! > $SCRIPTPATH/tmp/'daemon.pid'
        echo "Daemon $! is started."
        echo "Daemon $! is started." >> $SCRIPTPATH/log.txt
    fi
}

stopDaemon()
{    
    FILE=$SCRIPTPATH/tmp/'daemon.pid'
    if [ -f "$FILE" ]; then
        echo "Stopping daemon..."
        echo "Stopping daemon..." >> $SCRIPTPATH/log.txt
        
        PID=`cat $SCRIPTPATH/tmp/'daemon.pid'`
        #killinam procesa
        kill -9 $PID
        
        if [ $? -eq 0 ]; then
            #istrinam PID faila
            echo "Daemon $PID is stopped." 
            echo "Daemon $PID is stopped." >> $SCRIPTPATH/log.txt
        fi  
        rm $SCRIPTPATH/tmp/'daemon.pid'
    else       
        echo "Daemon is not started! Start process."
        echo "Daemon is not started! Start process." >> $SCRIPTPATH/log.txt
    fi
}

restartDaemon()
{
    #pakeiciam working directory i skripto vieta ir istrinam senus logus, kad neissipustu
    cd $SCRIPTPATH
    rm $SCRIPTPATH/log.txt

    #restartinam
    stopDaemon

    startDaemon
}

if [ $# == 1 ]
then
    case $1 in
        'start')  startDaemon;;
        'stop')   stopDaemon;;
        'restart')    restartDaemon;;
    esac
else
    echo "Use start|stop|restart"
fi