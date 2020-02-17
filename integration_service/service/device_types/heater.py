from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
import service.helpers.enums as enums
import service.helpers.userBase as user_db
import sqlalchemy as db 
from service.models import DeviceConfigBase, DeviceDataBase
import uuid as uuid

#Kaitintuvo duomenys ir config lenta
#models
class HeaterData(DeviceDataBase):
    __tablename__ = "heater_data"
    
    temp = db.Column(db.Numeric(8,2), nullable=False)
    actuator1_state = db.Column(db.Boolean, nullable=True)
    actuator2_state = db.Column(db.Boolean, nullable=True)
    actuator3_state = db.Column(db.Boolean, nullable=True) 

    def __init__(self, device_id, temp, actuator1_state, actuator2_state, actuator3_state):
        self.temp = temp
        self.actuator1_state = actuator1_state
        self.actuator2_state = actuator2_state
        self.actuator3_state = actuator3_state
        self.device_id = device_id
        
class HeaterConfig(DeviceConfigBase):
    __tablename__ = "heater_config"
      
    temp_treshold = db.Column(db.Numeric(8,2), nullable=True)
    actuator1_state = db.Column(db.Boolean, nullable=False)
    actuator2_state = db.Column(db.Boolean, nullable=False)
    actuator3_state = db.Column(db.Boolean, nullable=False)
    
    def __init__(self, device_id, temp_treshold, actuator1_state, actuator2_state, actuator3_state, name, is_active, weekdays, start_time, finish_time):
        self.temp_treshold = temp_treshold
        self.actuator1_state = actuator1_state
        self.actuator2_state = actuator2_state
        self.actuator3_state = actuator3_state
        self.name = name        
        self.device_id = device_id
        self.start_time = start_time
        self.finish_time = finish_time
        self.weekdays = weekdays
        self.is_active = is_active
        self.uuid = str(uuid.uuid4())

#METODAI
def create_tables(session):
    if not user_db.table_exists("heater_config"):                 
        HeaterConfig.__table__.create(session.bind)

    if not user_db.table_exists("heater_data"):                 
        HeaterData.__table__.create(session.bind)

    if not user_db.table_exists("heater_config"):                 
        HeaterConfig.__table__.create(session.bind)

def get_last_data(session,deviceId):
    return session.query(HeaterData).filter_by(device_id=deviceId).order_by(HeaterData.date.desc()).first()

def get_config(session, uuid):
    return session.query(HeaterConfig).filter_by(uuid=uuid).first()

def form_config_mqtt_payload(config, stop_job):
    payload = []
    if (stop_job):
        payload.append(form_mqtt_payload('ALLCHOFF'))
    elif (config.actuator1_state and config.actuator2_state and config.actuator3_state):
        payload.append(form_mqtt_payload('ALLCHON'))
    elif (not config.actuator1_state and not config.actuator2_state and not config.actuator3_state):
        payload.append(form_mqtt_payload('ALLCHOFF'))
    else:    
        if (config.actuator1_state):
            payload.append(form_mqtt_payload('CH1ON'))
        else:
            payload.append(form_mqtt_payload('CH1OFF'))

        if (config.actuator2_state):
            payload.append(form_mqtt_payload('CH2ON'))
        else:
            payload.append(form_mqtt_payload('CH2OFF'))

        if (config.actuator3_state):
            payload.append(form_mqtt_payload('CH3ON'))
        else:
            payload.append(form_mqtt_payload('CH3OFF'))
    
    return payload
#valdymas
def form_mqtt_payload(command):
    
    if (command == 'CH1OFF'):
        return "ACT1 OFF"
    elif (command == 'CH1ON'):
        return "ACT1 ON"
    elif (command == 'CH2OFF'):
        return "ACT2 OFF"
    elif (command == 'CH2ON'):
        return "ACT2 ON"
    elif (command == 'CH3OFF'):
        return "ACT3 OFF"
    elif (command == 'CH3ON'):
        return "ACT3 ON"
    
    if (command == 'ALLCHON'):
        return "ACT ALL ON"
    elif (command == 'ALLCHOFF'):
        return "ACT ALL OFF"

    return "NO ACT"


        