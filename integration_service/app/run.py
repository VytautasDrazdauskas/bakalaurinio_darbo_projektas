#!/usr/local/bin/python3.7
import datetime
import os
import time
import sys
from lib.daemon import Daemon
from service import MQTT_service

#reliatyvus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__file__))

class MQTT_daemon(Daemon):
    def run(self):
        while True:
            with open(dir_path + '/logs/log.txt', 'a') as fh:
                try:
                    fh.write("{}\n".format(datetime.datetime.now()))
                    fh.write("{}\n".format("Starting MQTT service..."))
                    service = MQTT_service()
                    service.start()
                except Exception as e:
                    fh.write("{}\n".format(datetime.datetime.now()))
                    fh.write("{}\n".format(e))
                    raise


                #logai
                # with open(dir_path + '/app/logs/log.txt', 'a') as fh:
                #     fh.write("{}\n".format(datetime.datetime.now()))
                #     fh.write("{}\n".format("test"))

if __name__ == "__main__":
    daemon = MQTT_daemon(dir_path + '/tmp/daemon.pid')
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