#!/usr/local/bin/python3.7
from service import MQTT_service
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

service = MQTT_service()
service.start()