#!/usr/local/bin/python3.7
import paho.mqtt.client as mqtt
import json, datetime, os
import sqlalchemy as db
import loadConfig as config
import logger as logger
import paho.mqtt.publish as publish
import helper.userBase as userDB
from helper.base import Session, engine, Base
from helper.jsonParser import Parse
from helper.schemaBuilder import table_exists
from models import Users, Devices, DeviceData, UserDevices
from decimal import *

class MQTT_service():
    
    def on_connect(self, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.subscribe("+/+/+/jsondata")

    def on_message(self, userdata, msg):
        payload = Parse(msg.payload)

        #logai
        logger.Log(datetime.datetime.now())
        logger.Log('Sender MAC address: ' + payload.deviceMAC)
        logger.Log(str(msg.payload))

        #sukuriam sesija
        try:    
            #parenkam dominancius duomenis is isparsinto JSON dict objekto
            deviceMac = payload.deviceMAC
            temp = Decimal(payload.data['temp'])
            
            #atidarom pagrindines DB sesija
            session = Session()

            #surandam DB iregistruota prietaisa, prietaiso savininka ir paskutinius duomenis
            device = session.query(Devices).filter_by(mac=deviceMac).first()
            user = session.query(Users).filter_by(id=device.user_id).first()

            #naudotojo asmenines DB sesijas
            userSession = userDB.create_user_session(user)

            #jei neegzistuoja lenta, ja sukuriam
            if not userDB.table_exists(user,"device_data"):                
                DeviceData.__table__.create(userSession.bind)

            #sistemos naudotojo DB randame uzregistruota prietaisa
            userDevice = userSession.query(UserDevices).filter_by(mac=device.mac).first()

            if (userDevice is not None):
                #paskutiniai duomenys
                lastData = userSession.query(DeviceData).filter_by(device_id=userDevice.id).order_by(DeviceData.date.desc()).first()

                #suformuojam tema
                systemName = "system"
                topic = user.uuid + "/" + systemName + "/" + device.mac + "/control"
                tempTreshold = 30.00

                #jei temperatura per didele, ijungiam LED
                if (temp >= tempTreshold and lastData is not None and lastData.temp < tempTreshold):
                    logger.Log('Temperature treshold exceeded: ' + str(temp))
                    command = "LED ON"
                    #publishinam komanda
                    publish.single(topic=topic, payload=command, hostname=config.broker_ip, port=config.broker_port, qos=2)
                elif (temp < tempTreshold and lastData is not None and lastData.temp >= tempTreshold):
                    logger.Log('Temperature lowered below treshold: ' + str(temp))                
                    command = "LED OFF"
                    #publishinam komanda
                    publish.single(topic=topic, payload=command, hostname=config.broker_ip, port=config.broker_port, qos=2)
                
                #sukuriam duomenu irasa ir issaugom DB
                new_data = DeviceData(
                    device_id=userDevice.id,
                    temp=temp
                    )

                userSession.add(new_data) 
                userSession.commit()
            else:
                logger.Log('Device was not found in user account! User UUID: ' + user.uuid + ' Device MAC: ' + device.mac )
                userSession.rollback()
                session.rollback()

        except Exception as Ex:
            logger.Log(Ex)
            session.rollback()
            userSession.rollback()
            raise

        finally:
            session.close()
            userSession.close()
               
    #paleidzia mqtt servisa su eventais
    def start(self):       
        try:
            client = mqtt.Client()
            client.on_connect = MQTT_service.on_connect
            client.on_message = MQTT_service.on_message

            #prisijungiam prie brokerio su confige esanciais parametrais
            client.connect(config.broker_ip, config.broker_port, 60)

            client.loop_forever()
        except Exception as Ex:
            logger.Log(Ex)
            raise


