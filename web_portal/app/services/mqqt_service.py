
from flask import json, jsonify
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import time
import app.load_config as app_config

class MqttService():
        
    def publish_with_response(topic,response_topic,message, timeout): 
        global response
        response = ""

        def on_message(self, userdata, msg):            
            global response
            response = msg.payload
            self.disconnect()
        
        #sukuriam klienta
        client = mqtt.Client()
        client.on_message = on_message

        #prisijungiam prie brokerio su confige esanciais parametrais
        client.connect(app_config.broker_ip, app_config.broker_port, 60)
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
                return response
                
        return jsonify(success=False,reason="Time is up.").data

        #callback = subscribe.simple(response_topic, qos=2, msg_count=1, retained=False, hostname=config.broker_ip, port=config.broker_port, keepalive=30)
        #return Parse(callback.payload)