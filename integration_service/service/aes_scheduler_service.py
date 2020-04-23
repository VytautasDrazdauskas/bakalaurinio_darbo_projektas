#!/usr/bin/python3.6
import paho.mqtt.client as mqtt
import json, datetime, os
import sqlalchemy as db
import service.helpers.loadConfig as config
import service.logger as logger
import paho.mqtt.publish as publish
import service.helpers.userBase as userDB
import service.helpers.enums as enums
from service.helpers.base import Session, engine, Base
from service.lib.json2obj import JsonParse
from service.helpers.schemaBuilder import table_exists
import service.models as model
import service.device_types.default_device as default_device
import service.device_types.heater as heater
import service.controller.devices as device_controller
from service.helpers.cryptography import AESCipher
from decimal import *
import schedule
import time, secrets, binascii
from datetime import timedelta

class AesScheduler():
  def job(self):
      try:
        session = Session()
        aes = AESCipher()

        today = datetime.datetime.now()
        #surenkam irenginius, kuriem reikia keisti AES rakta
        devices_to_update = session.query(model.Devices).filter(model.Devices.aes_key_change_date <= today).all()
        
        for device in devices_to_update:
          try:
            user = session.query(model.Users).filter_by(id=device.user_id).first()

            #sukuriama naudotojo db sesija          
            user_session = userDB.create_user_session(user)
            user_device = user_session.query(model.UserDevices).filter_by(mac=device.mac).first()
            
            #busena turi buti aktyvi
            if (user_device.status != enums.DeviceState.Active.value):
              device.aes_key_change_date = today + timedelta(seconds=user_device.aes_key_interval)
              device_controller.save_device_history(user_session,user_device, "Prietaiso AES raktas nepakeistas. Kitas bandymas: " + str(device.aes_key_change_date))
              user_session.close()
              session.commit()
              continue

            #sugeneruojamas naujas AES raktas ir konvertuojama i HEX
            passphrase = secrets.token_hex(16)
            new_key = aes.generate_key(passphrase)
            key_hex = binascii.hexlify(new_key).decode('utf-8')

            #nusiunciame i irengini rakta, laukiam atsakymo
            response = device_controller.send_device_configuration(user, user_device, "newaeskey", key_hex)
            if (response):
              aes.save_key(new_key, device.mac)
              device.aes_key_change_date = today + timedelta(seconds=user_device.aes_key_interval)
              
              device_controller.save_device_history(user_session,user_device, "Prietaiso AES raktas sėkmingai pakeistas! Rakto fragmentas: " + key_hex[0:10])
              logger.log_aes_scheduler("Device AES key has been updated. Device MAC: " + device.mac + "AES key fragment:" + key_hex[0:10])
              
            session.commit()
            user_session.commit()
          except Exception as ex:
            logger.log_aes_scheduler(ex.args)
            user_session.rollback()
          finally:
            user_session.close()
      except Exception as ex:
        logger.log_aes_scheduler(ex.args)
        session.rollback()
      finally:
        session.close()

  def start(self):
    scheduler = AesScheduler()
    schedule.every(config.scheduler.interval).seconds.do(scheduler.job)

    while 1:
        schedule.run_pending()
        time.sleep(1)
    


