import os

dir_path = os.path.dirname(os.path.realpath(__file__))

def Log(input):
    with open(dir_path + '/logs/log.txt', 'a') as fh:
        fh.write("{}\n".format(input))