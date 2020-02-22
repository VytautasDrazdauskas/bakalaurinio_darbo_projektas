import json, os

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__package__))

#configu uzkrovimas
with open(dir_path +'/config.json') as config_file:
    config = json.load(config_file)

#brokeris
broker_config = config['broker']
broker_ip = broker_config['host']
broker_port = broker_config['port']