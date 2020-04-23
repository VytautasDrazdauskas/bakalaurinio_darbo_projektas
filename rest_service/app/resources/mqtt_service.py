from flask_restful import Resource
from flask import request
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import app.loadConfig as config
from app.json2obj import JsonParse
from app.cryptography import AESCipher
import time
import os
import ssl
from uuid import uuid4

response = ""

class MQTTPublishWithResponse(Resource):

    def get(self):
        return {"success": False, "reason": "No data provided"}, 400

    def put(self):
        try:
            data = JsonParse(request.get_json(force=True))

            if not data:
                return {"success": False, "reason": "No data provided"}, 400

            topic = data.topic
            response_id = str(uuid4())
            response_topic = data.response_topic + "/" + response_id          
            mac = data.mac        
            timeout = data.timeout
            
            payload = {
                "command":data.message,
                "response_id":response_id
            }

            #tikriname, ar egzistuoja AES raktas
            aes = AESCipher()
            if (mac is not None):
                key = aes.load_key(filename=mac)
                if key is not None:
                    enc = aes.encrypt(plain_text=json.dumps(payload), key=key)
                    message = json.dumps(enc)
                else:
                    return {"success": False, "reason": "AES key not found."}, 400
            else:
                return {"success": False, "reason": "Mac is empty."}, 400
                

            global response
            response = ""

            def on_message(self, userdata, msg):
                global response
                resp = json.loads(msg.payload.decode('utf-8'))

                #tikrinam, ar duomenys yra uzsifruoto paketo formato
                if('iv' in resp and 'data' in resp):
                    key = aes.load_key(mac)
                    dec = aes.decrypt(enc=resp, key=key)
                    response = json.loads(dec)
                else: #jei ne, laikom, jog nera sifruotes
                    response = resp

                self.disconnect()

            # sukuriam klienta
            client = mqtt.Client()
            client.on_message = on_message
            client.tls_set(ca_certs=config.broker.cafile, certfile=config.broker.clientCert, keyfile=config.broker.clientKey)

            # prisijungiam prie brokerio su confige esanciais parametrais
            client.connect(host=config.broker.host, port=config.broker.port)
            client.subscribe(topic=response_topic, qos=2)
            client.publish(topic=topic, payload=message, qos=2)

            # timeris
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

            return {"success": False, "reason": "Time is up."}, 400

        except Exception as ex:
            return {"success": False, "reason": ex.args}, 400

class MQTTPublish(Resource):

    def get(self):
        return {"success": False, "reason": "No data provided"}, 400

    def put(self):
        try:
            data = JsonParse(request.get_json(force=True))

            if not data:
                return {"success": False, "reason": "No data provided"}, 400

            response_id = str(uuid4())  
            topic = data.topic
            mac = data.mac   
               

            payload = {
                "command":data.message,
                "response_id":response_id
            }
            
            #tikriname, ar egzistuoja AES raktas
            aes = AESCipher()
            if (mac is not None):
                key = aes.load_key(filename=mac)
                if key is not None:
                    enc = aes.encrypt(plain_text=json.dumps(payload), key=key)
                    message = json.dumps(enc)
                else:
                    return {"success": False, "reason": "AES key not found."}, 400
            else:
                return {"success": False, "reason": "Mac is empty."}, 400
                       
            # prisijungiam prie brokerio su confige esanciais parametrais
            tls_config = {
                'ca_certs':config.broker.cafile, 
                'certfile':config.broker.clientCert, 
                'keyfile':config.broker.clientKey
            }

            publish.single(topic=topic, payload=message, qos=2, hostname=config.broker.host, port=config.broker.port,tls=tls_config)

            return {"success": True, "reason": "Completed"}, 200

        except Exception as ex:
            return {"success": False, "reason": ex.args}, 400    
            

        
