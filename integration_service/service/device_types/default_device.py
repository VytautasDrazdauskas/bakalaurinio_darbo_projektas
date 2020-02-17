from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
import service.helpers.userBase as user_db
import sqlalchemy as db
import service.helpers.enums as enums
from service.models import DeviceConfigBase, DeviceDataBase
import uuid as uuid

class DefaultDeviceData(DeviceDataBase):
    __tablename__ = "default_device_data"

    temp = db.Column(db.Numeric(8,2), nullable=False)
    led_state = db.Column(db.Boolean, nullable=True)

    def __init__(self, device_id, temp, led_state):
        self.device_id = device_id  
        self.temp = temp
        self.led_state = led_state

class DefaultDeviceConfig(DeviceConfigBase):
    __tablename__ = "default_device_config"
   
    temp_treshold = db.Column(db.Numeric(8,2), nullable=True)
    led_state = db.Column(db.Boolean, nullable=True)   

    def __init__(self, device_id, temp_treshold, led_state, name, is_active, weekdays, start_time, finish_time):
        self.temp_treshold = temp_treshold
        self.led_state = led_state        
        self.name = name        
        self.device_id = device_id
        self.start_time = start_time
        self.finish_time = finish_time
        self.weekdays = weekdays
        self.is_active = is_active
        self.uuid = str(uuid.uuid4())

def create_tables(session):
    if not user_db.table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

    if not user_db.table_exists("default_device_data"):                 
        DefaultDeviceData.__table__.create(session.bind)

    if not user_db.table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

def get_last_data(session,deviceId):
    return session.query(DefaultDeviceData).filter_by(device_id=deviceId).order_by(DefaultDeviceData.date.desc()).first()

def get_config(session, uuid):
    return session.query(DefaultDeviceConfig).filter_by(uuid=uuid).first()

def form_config_mqtt_payload(config, stop_job):
    payload = []
    if (stop_job):
        payload.append(form_mqtt_payload("CH1OFF"))
    elif (config.led_state):
        payload.append(form_mqtt_payload("CH1ON"))
    else:
        payload.append(form_mqtt_payload("CH1OFF"))
    
    return payload

def form_mqtt_payload(command):
    
    if (command == 'CH1OFF'):
        return "LED OFF"
    elif (command == 'CH1ON'):
        return "LED ON"

    return "NO ACT"