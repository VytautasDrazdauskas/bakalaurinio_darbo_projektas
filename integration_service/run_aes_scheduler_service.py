#!/usr/bin/python3.6
import datetime
import os
import time
import sys
import json
from service.lib.daemon import Daemon
from service.aes_scheduler_service import AesScheduler
import service.logger as logger

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__file__))

class AESServiceDaemon(Daemon):
    def run(self):
        while True:
            with open(dir_path + '/service/logs/aes_scheduler_log.txt', 'a') as fh:
                try:
                    logger.log("Starting AES Scheduler service...")
                    scheduler_service = AesScheduler()
                    scheduler_service.start()                  
                except Exception as e:
                    logger.log(e)
                    raise

if __name__ == "__main__":
    daemon = AESServiceDaemon(dir_path + '/tmp/aes_scheduler_daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print ("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: start|stop|restart")
        sys.exit(2)