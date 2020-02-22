from flask_restful import Resource
from flask import request
import json
import paho.mqtt.client as mqtt
import app.loadConfig as config
from app.json2obj import JsonParse
import time

response = ""

class MQTTPublishWithResponse(Resource):

    def get(self):
        return {"success":False,"reason":"No data provided"}, 400

    def put(self): 
        data = JsonParse(request.get_json(force=True))
        
        if not data:
            return {"success":False,"reason":"No data provided"}, 400

        topic = data.topic
        response_topic = data.response_topic
        message = data.message
        timeout = data.timeout

        global response
        response = ""

        def on_message(self, userdata, msg):   
            global response
            response = json.loads(msg.payload.decode('utf-8'))
            self.disconnect()
        
        #sukuriam klienta
        client = mqtt.Client()
        client.on_message = on_message

        #prisijungiam prie brokerio su confige esanciais parametrais
        client.connect(config.broker_ip, config.broker_port, 60)
        client.subscribe(topic=response_topic,qos=2)
        client.publish(topic=topic, payload=message, qos=2)
        
        #timeris
        start_time = time.time()
        wait_time = timeout
        while True:
            client.loop()      
            if (response == ""):
                elapsed_time = time.time() - start_time
                if elapsed_time > wait_time:
                    client.disconnect()
                    break
            else:
                client.disconnect()
                return response, 200
        
        return {"success":False,"reason":"Time is up."}, 400