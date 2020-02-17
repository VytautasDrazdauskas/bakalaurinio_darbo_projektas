#!/usr/local/bin/python3.7
import datetime
import os
import time
import sys
import json
from service.lib.daemon import Daemon
from service.integration_service import IntegrationService
import service.logger as logger

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__file__))

class IntegrationDaemon(Daemon):
    def run(self):
        while True:
            with open(dir_path + '/service/logs/log.txt', 'a') as fh:
                try:
                    logger.log("Starting MQTT service...")
                    mqtt_service = IntegrationService()
                    mqtt_service.start()                    
                except Exception as e:
                    logger.log(e)
                    raise

if __name__ == "__main__":
    daemon = IntegrationDaemon(dir_path + '/tmp/integration_daemon.pid')
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