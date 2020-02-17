from flask import jsonify
import paho.mqtt.client as mqtt
import service.helpers.loadConfig as config
import time

class MQTTService():
    
    def publish_with_response(topic,response_topic,message, timeout): 
        global res
        res = ""

        def on_message(self, userdata, msg):            
            global res
            res = msg.payload
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
            if (res == ""):
                elapsed_time = time.time() - start_time
                if elapsed_time > wait_time:
                    client.disconnect()
                    break
            else:
                return res
        
        result = jsonify(success=False,reason="Time is up.")
        return result.data