import json, os
from app.helpers.json2obj import JsonParse

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY')

#configu uzkrovimas
with open(dir_path + '/../config.json') as config_file:
    config = json.load(config_file)

#duomenu baze
database = JsonParse(config['database'])

#restful servisas
restful = JsonParse(config['restful'])