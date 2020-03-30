import json, os
from app.json2obj import JsonParse

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__package__))

#configu uzkrovimas
with open(dir_path +'/config.json') as config_file:
    config = json.load(config_file)

#brokeris
broker = JsonParse(config['broker'])

#raktai
keys = JsonParse(config['keys'])

#irenginiu sertifikatai
device_certs = JsonParse(config['deviceCerts'])