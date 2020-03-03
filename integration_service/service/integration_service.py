#!/usr/bin/python3
import paho.mqtt.client as mqtt
import datetime, os
import sqlalchemy as db
import service.helpers.loadConfig as config
import service.logger as logger
import paho.mqtt.publish as publish
import service.helpers.userBase as userDB
import service.helpers.enums as enums
from service.helpers.base import Session, engine, Base
from service.helpers.schemaBuilder import table_exists
from service.models import Users, Devices, UserDevices
import service.controller.devices as device_controller
import service.device_types.default_device as default_device
import service.device_types.heater as heater
from decimal import Decimal
import time
from service.lib.json2obj import JsonParse

def Str2Bool(input):
  return input.lower() in ("yes", "true", "t", "1")

class IntegrationService():
    
    def on_connect(self, userdata, flags, rc):
        logger.log("Connected with result code "+str(rc))
        self.subscribe("+/+/+/jsondata")

    def on_message(self, userdata, msg):
        try:
            payload = JsonParse(msg.payload.decode('utf-8'))    
            #logai
            logger.log('Sender MAC address: ' + payload.deviceMAC)
            logger.log(str(msg.payload))

            #sukuriam sesija   
            #parenkam dominancius duomenis is isparsinto JSON dict objekto
            device_mac = payload.deviceMAC
                        
            #atidarom pagrindines DB sesija
            session = Session()

            #surandam DB iregistruota prietaisa, prietaiso savininka ir paskutinius duomenis
            device = session.query(Devices).filter_by(mac=device_mac).first()
            user = session.query(Users).filter_by(id=device.user_id).first()
            
            #naudotojo asmenines DB sesijas
            user_session = userDB.create_user_session(user)
            #sistemos naudotojo DB randame uzregistruota prietaisa
            user_device = user_session.query(UserDevices).filter_by(mac=device.mac).first()

            #tikrinam, ar devaisas aktyvus
            if (user_device.status != enums.DeviceState.Active.value and user_device.status != enums.DeviceState.Deleted.value and user_device.status != enums.DeviceState.Blocked.value):
                user_device.status = enums.DeviceState.Active.value 

            if (user_device is not None):
                #-------- SILDYTUVAS ----------------
                if (user_device.device_type == enums.DeviceType.Heater.value):                     
                    #uzkraunam devaiso config irasa
                    
                    #paskutiniai devaiso duomenys
                    last_data = user_session.query(heater.HeaterData).filter_by(device_id=user_device.id).order_by(heater.HeaterData.date.desc()).first()

                    #suformuojam tema
                    system_name = "system"
                    topic = user.uuid + "/" + system_name + "/" + device.mac + "/control"

                    configuration = user_session.query(heater.HeaterConfig).filter_by(device_id=user_device.id,is_active=True, job_state=enums.ConfigJobState.Running.value).first()

                    if (configuration is not None):
                        temp_treshold = configuration.temp_treshold
                        temp = Decimal(payload.data.temp)

                        if (temp_treshold is not None):
                            #jei temperatura per didele, ijungiam LED
                            if (temp >= temp_treshold and last_data is not None and last_data.temp < temp_treshold):
                                logger.log('Temperature treshold exceeded: ' + str(temp))
                                device_controller.save_device_history(user_session,user_device,"Temperatūros riba (" + str(temp_treshold) + ") viršyta pagal konfigūraciją \"" + configuration.name + "\"! Temperatūra: " + str(temp) + " Išjungiama programa.")
            
                                #riba virsyta
                                device_controller.execute_job(user, user_device, configuration, True)
                            elif (temp < temp_treshold and last_data is not None and last_data.temp >= temp_treshold):
                                logger.log('Temperature lowered below treshold: ' + str(temp))    
                                device_controller.save_device_history(user_session,user_device,"Temperatūra " + str(temp) + " žemesnė už nustatytą ribą (" + str(temp_treshold) + "). Atstatoma konfigūracijos \"" + configuration.name + "\" programa.")
                                #temperatura sumazejo, bet jobas nesibaige
                                device_controller.execute_job(user, user_device, configuration)
                    
                    temp = Decimal(payload.data.temp)
                    actuator1 = Str2Bool(payload.data.act1)
                    actuator2 = Str2Bool(payload.data.act2)
                    actuator3 = Str2Bool(payload.data.act3)

                    #sukuriam duomenu irasa ir issaugom DB
                    new_data = heater.HeaterData(
                        device_id=user_device.id,
                        temp=temp,
                        actuator1_state=actuator1,
                        actuator2_state=actuator2,
                        actuator3_state=actuator3
                        )

                    user_session.add(new_data) 
                    user_session.commit()
                #---------- CIA KITU TIPU DEVAISAI ---------------
                elif (user_device.device_type == enums.DeviceType.Default.value):
                                                        
                    #paskutiniai devaiso duomenys
                    last_data = user_session.query(default_device.DefaultDeviceData).filter_by(device_id=user_device.id).order_by(default_device.DefaultDeviceData.date.desc()).first()

                    #suformuojam tema
                    system_name = "system"
                    topic = user.uuid + "/" + system_name + "/" + device.mac + "/control"

                    temp = Decimal(payload.data.temp)
                    ledState = Str2Bool(payload.data.ledState)

                    #sukuriam duomenu irasa ir issaugom DB
                    new_data = default_device.DefaultDeviceData(
                        device_id=user_device.id,
                        temp=temp,
                        led_state=ledState,
                        )

                    user_session.add(new_data) 
                    user_session.commit()
                else:
                    logger.log('Wrong device type! User UUID: ' + user.uuid + ' Device MAC: ' + device.mac)
            else:
                logger.log('Device have not assigned type! User UUID: ' + user.uuid + ' Device MAC: ' + device.mac )
                user_session.rollback()
                session.rollback()
        except Exception as Ex:
            logger.log(Ex)
            session.rollback()
            user_session.rollback()
            raise

        finally:
            session.close()
            user_session.close()
               
    #paleidzia mqtt servisa su eventais
    def start(self):       
        try:
            client = mqtt.Client()
            client.tls_set(ca_certs=config.broker.cafile, certfile=config.broker.clientCert, keyfile=config.broker.clientKey)
            client.on_connect = IntegrationService.on_connect
            client.on_message = IntegrationService.on_message
            
            #prisijungiam prie brokerio su confige esanciais parametrais
            client.connect(config.broker.host, config.broker.port, 60)
            client.loop_forever()
        except Exception as Ex:
            logger.log(Ex)
            raise




