import os
from _datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))

def log(input):
    with open(dir_path + '/logs/log.txt', 'a') as fh:
        fh.write("{}\n".format(datetime.now()))
        fh.write("{}\n".format(input))

def log_scheduler(input):
    with open(dir_path + '/logs/scheduler_log.txt', 'a') as fh:
        fh.write("{}\n".format(datetime.now()))
        fh.write("{}\n".format(input))