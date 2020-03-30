
from flask import json, jsonify
import time
import app.load_config as app_config
import requests
from app.helpers.json2obj import JsonParse

class DevicesService():

    def __init__(self):
        self.url = "http://" + app_config.restful.host + ":" + app_config.restful.port + "/api" + app_config.restful.deviceKeyGen
        
    def generate_device_keys(self, mac, uuid):         
        data = {
            "mac":mac,
            "uuid":uuid
        }

        with requests.Session() as session:
            response = session.put(url=self.url, json=data)            
            return JsonParse(response.text)