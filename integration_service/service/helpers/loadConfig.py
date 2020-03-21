import json, os
from service.lib.json2obj import JsonParse

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__package__))

#configu uzkrovimas
with open(dir_path +'/config.json') as config_file:
    config = json.load(config_file)

#brokeris
broker = JsonParse(config['broker'])

#duomenu baze
database = JsonParse(config['database'])

#scheduleris
scheduler = JsonParse(config['scheduler'])

#restful servisas
restful = JsonParse(config['restful'])

#AES raktai
keys = JsonParse(config['keys'])