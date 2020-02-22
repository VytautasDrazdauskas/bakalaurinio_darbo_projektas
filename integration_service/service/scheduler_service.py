#!/usr/bin/python3
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
from decimal import *
import schedule
import time

def Str2Bool(input):
  return input.lower() in ("yes", "true", "t", "1")

class Scheduler():
  def job(self):
      try:
        session = Session()
        weekday = str(datetime.datetime.today().weekday())

        #paleidimo langas 1 minutė
        max_time = datetime.datetime.now().time()
        min_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        min_time = min_time.time()

        #istraukiam tik tuos jobus, kurie siandien turi buti paleisti
        jobs_to_start = session.query(model.DeviceJobs).filter(model.DeviceJobs.weekdays.contains('%'+weekday+'%'), model.DeviceJobs.start_time <= max_time, model.DeviceJobs.start_time >= min_time).filter_by(running=False).all()
        for job in jobs_to_start:
          logger.log_scheduler("Starting job UUID: " + job.config_uuid)
          device = session.query(model.Devices).filter_by(id=job.device_id).first()
          user = session.query(model.Users).filter_by(id=device.user_id).first()
          
          user_session = userDB.create_user_session(user)
          user_device = user_session.query(model.UserDevices).filter_by(mac=device.mac).first()
          
          configuration = device_controller.get_device_config(user_session, user_device, job)

          if (device_controller.execute_job(user, user_device, configuration)):
            job.running = True
            configuration.job_state = enums.ConfigJobState.Running.value
            job.finish_date = datetime.datetime.now() + datetime.timedelta(hours=job.duration.hour, minutes=job.duration.minute)

            #irasom devaiso istorijos irasa
            device_controller.save_device_history(user_session,user_device,"Rutininis darbas pradėtas pagal konfigūraciją \"" + configuration.name + "\". Darbas baigsis: " + str(job.finish_date))
            user_session.commit()
            session.commit()         
          else:
            device_controller.save_device_history(user_session,user_device,"Rutininis darbas pagal konfigūraciją \"" + configuration.name + "\" nebuvo paleistas, nes nebuvo ryšio su prietaisu!")
            user_session.commit()
            user_session.close()
            continue
          user_session.close()

        #jobai, kurie turi buti uzbaigti
        today = datetime.datetime.now()
        jobs_to_stop = session.query(model.DeviceJobs).filter(model.DeviceJobs.finish_date <= today).filter_by(running=True).all()

        for job in jobs_to_stop:
          logger.log_scheduler("Stopping job UID: " + job.config_uuid)

          device = session.query(model.Devices).filter_by(id=job.device_id).first()
          user = session.query(model.Users).filter_by(id=device.user_id).first()
          
          user_session = userDB.create_user_session(user)
          user_device = user_session.query(model.UserDevices).filter_by(mac=device.mac).first()
          
          configuration = device_controller.get_device_config(user_session, user_device, job)

          if (device_controller.execute_job(user, user_device, configuration, True)):
            job.running = False
            job.finish_date = None
            configuration.job_state = enums.ConfigJobState.Idle.value
            device_controller.save_device_history(user_session,user_device,"Rutininis darbas pagal konfigūraciją \"" + configuration.name + "\" sustabdytas!")
            user_session.commit()
            session.commit()          
          else:         
            device_controller.save_device_history(user_session,user_device,"Rutininis darbas pagal konfigūraciją \"" + configuration.name + "\" nebuvo paleistas, nes nebuvo ryšio su prietaisu!")
            user_session.commit()
            user_session.close()
            continue
          user_session.close()

      except Exception as ex:
        logger.log_scheduler(ex.args)
      finally:
        session.close()

  def start(self):
    scheduler = Scheduler()
    schedule.every(config.scheduler_interval).seconds.do(scheduler.job)

    while 1:
        schedule.run_pending()
        time.sleep(1)
    


