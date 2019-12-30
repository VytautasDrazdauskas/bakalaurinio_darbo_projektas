#!/bin/ash

startDaemon()
{    
    FILE=/root/app/publish_daemon.pid
    if [ -f "$FILE" ]; then
        echo "Daemon is already started! Stop or restart process."
    else 
        echo "Starting daemon..."
        echo "Starting daemon..." >> /root/app/log.txt
        #startuojam deamona
        nohup /root/app/publish.lua >> /root/app/log.txt 2>&1 >/dev/null &

        #issaugom PID i tmp faila
        echo $! > /root/app/publish_daemon.pid
        echo "Daemon $! is started."
        echo "Daemon $! is started." >> /root/app/log.txt
    fi
}

stopDaemon()
{    
    FILE=/root/app/publish_daemon.pid
    if [ -f "$FILE" ]; then
        echo "Stopping daemon..."
        echo "Stopping daemon..." >> /root/app/log.txt
        #viska pilam i null, nes turim labai ribota atminti
        PID=`cat /root/app/publish_daemon.pid`
        #killinam procesa
        kill -9 $PID
        
        if [ $? -eq 0 ]; then
            #istrinam PID faila
            echo "Daemon $PID is stopped." 
            echo "Daemon $PID is stopped." >> /root/app/log.txt
        fi  
        rm /root/app/publish_daemon.pid
    else        
        echo "Daemon is not started! Start process."
        echo "Daemon is not started! Start process." >> /root/app/log.txt
    fi
}

restartDaemon()
{
    #pakeiciam working directory i skripto vieta ir istrinam senus logus, kad neissipustu
    cd /root/app
    rm /root/app/log.txt

    #patikrinam, ar yra interneto rysys
    while ! ping -c 1 -W 1 8.8.8.8 > /dev/null 2>&1; do
        echo "Waiting for 8.8.8.8. Network interface might be down..." 
        echo "Waiting for 8.8.8.8. Network interface might be down..." >> /root/app/log.txt
        sleep 1
    done

    #restartinam
    echo "stopping daemon" >> /root/app/log.txt
    stopDaemon
    echo "starting daemon" >> /root/app/log.txt
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