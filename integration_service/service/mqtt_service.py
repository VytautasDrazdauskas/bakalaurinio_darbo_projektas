from flask import jsonify
import service.helpers.loadConfig as config
import time
import requests

class MQTTService():    
    def publish_with_response(topic,response_topic,message, timeout): 
        
        url = "http://" + config.restful.host + ":" + config.restful.port + "/api" + config.restful.publishResp

        data = {
            "topic":topic,
            "response_topic":response_topic,
            "message":message,
            "timeout":timeout
        }

        with requests.Session() as session:
            response = session.put(url=url, json=data)            
            return response.text