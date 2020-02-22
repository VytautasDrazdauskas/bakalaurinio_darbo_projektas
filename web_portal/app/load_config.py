import json, os

#absoliutus kelias iki programos
dir_path = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY')

#configu uzkrovimas
with open(dir_path + '/../config.json') as config_file:
    config = json.load(config_file)

#duomenu baze
database_config = config['database']
db_ip = database_config['host']
db_port = database_config['port']
db_user = database_config['user']
db_password = database_config['password']

#restful servisas
restful = config['restful']
rest_ip = restful['ip']
rest_port = restful['port']
rest_publish_resp = restful['publishresp']