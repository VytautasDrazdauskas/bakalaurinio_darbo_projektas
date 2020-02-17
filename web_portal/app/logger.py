import os
from _datetime import datetime


class Logger:
    def __init__(self):
        self.Log
        self.log_error

    def log_error(input):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/logs/error.txt', 'a') as fh:
            fh.write("{}\n".format(datetime.now()))
            fh.write("{}\n".format(input))

    def Log(input):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/logs/log.txt', 'a') as fh:
            fh.write("{}\n".format(datetime.now()))
            fh.write("{}\n".format(input))