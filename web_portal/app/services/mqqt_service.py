
from flask import json, jsonify
import time
import app.load_config as app_config
import requests

class MqttService():
        
   def publish_with_response(topic,response_topic, message, timeout, mac): 
        url = "http://" + app_config.restful.host + ":" + app_config.restful.port + "/api" + app_config.restful.publishResp

        data = {
            "topic":topic,
            "response_topic":response_topic,
            "message":message,
            "timeout":timeout,
            "mac":mac
        }

        with requests.Session() as session:
            response = session.put(url=url, json=data)            
            return response.text