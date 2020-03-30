
from flask import json, jsonify
import time
import app.load_config as app_config
import requests

class MqttService():

    def __init__(self):
        self.url = "http://" + app_config.restful.host + ":" + app_config.restful.port + "/api" + app_config.restful.publishResp

        
    def publish_with_response(self, topic, response_topic, message, timeout, mac): 
        data = {
            "topic":topic,
            "response_topic":response_topic,
            "message":message,
            "timeout":timeout,
            "mac":mac
        }

        with requests.Session() as session:
            response = session.put(url=self.url, json=data)            
            return response.text