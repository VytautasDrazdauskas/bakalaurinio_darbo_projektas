#!/usr/local/bin/python3.7
import paho.mqtt.client as mqtt
import json, datetime, os

dir_path = os.path.dirname(os.path.realpath(__file__))

class Parse(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)

class MQTT_service():
    def on_connect(self, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.subscribe("useruid/system/+/jsondata")

    def on_message(self, userdata, msg):
        data = Parse(msg.payload)
        print(str(msg.payload))

        with open(dir_path + '/logs/log.txt', 'a') as fh:
            fh.write("{}\n".format(datetime.datetime.now()))
            fh.write("{}\n".format('Sender MAC address: ' + data.deviceMAC))
            fh.write("{}\n".format(str(msg.payload)))

    def start(self):
        broker_ip = "192.168.137.53"
        broker_port = 1883   

        try:
            client = mqtt.Client()
            client.on_connect = MQTT_service.on_connect
            client.on_message = MQTT_service.on_message

            client.connect(broker_ip, broker_port, 60)

            client.loop_forever()
        except Exception as e:
            raise e


