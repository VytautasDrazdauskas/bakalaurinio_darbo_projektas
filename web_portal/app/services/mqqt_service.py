
from flask import json, jsonify
import time
import app.load_config as app_config
import requests

class MqttService():
        
   def publish_with_response(topic,response_topic,message, timeout): 
        url = "http://" + app_config.rest_ip + ":" + app_config.rest_port + "/api" + app_config.rest_publish_resp

        data = {
            "topic":topic,
            "response_topic":response_topic,
            "message":message,
            "timeout":timeout
        }

        with requests.Session() as session:
            response = session.put(url=url, json=data)            
            return response.text