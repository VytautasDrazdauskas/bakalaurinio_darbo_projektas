from app import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
from app.helpers.user_base import *
import app.helpers.enums as enums
from flask import jsonify
from app.forms import DeviceConfigBaseForm
from flask_wtf import FlaskForm
from wtforms import *
from app.forms import *
from app.models import DeviceConfigBase, DeviceDataBase
import app.helpers.code_decode as code_decode
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

#view models
class DeviceDataView():
    def __init__(self, id, led_state, temp, date):
        self.id = id
        self.led_state = led_state
        self.temp = temp
        self.date = date

    @property
    def serialize(self):
        return {
            'id': self.id,
            'led_state': self.led_state,
            'temp': self.temp,
            'date': self.date
        }

class DefaultDeviceConfigView():
    def __init__(self, uuid, name, temp, is_active, led_state, weekdays, start_time, finish_time, creation_date):
        self.uuid = uuid
        self.name = name
        self.is_active = is_active
        self.temp = temp
        self.led_state = led_state
        self.weekdays = weekdays
        self.start_time = start_time
        self.finish_time = finish_time
        self.creation_date = creation_date
        
    @property
    def serialize(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'is_active': self.is_active,
            'temp': self.temp,
            'led_state': self.led_state,
            'weekdays' : self.weekdays,
            'start_time': self.start_time,
            'finish_time': self.finish_time,
            'creation_date': self.creation_date
        }

#formos, paveldim bazine klase
class DefaultDeviceConfigForm(DeviceConfigBaseForm):    
    temp_treshold = DecimalField('Maksimali temperatūra')
    led_state = BooleanField('LED būsena')

def create_tables(session):
    if not table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

    if not table_exists("default_device_data"):                 
        DefaultDeviceData.__table__.create(session.bind)

    if not table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

#metodai
def get_data(session, device_id):
    data_list = session.query(DefaultDeviceData).filter_by(device_id=device_id).all()  

    data_object_list = []
    for data in data_list:
        data_object = DeviceDataView(
            data.id,
            str(data.led_state),
            str(data.temp) + " C°",
            str(data.date)
        )
        data_object_list.append(data_object)

    return jsonify({
            'data': [result.serialize for result in data_object_list]
        })

def get_last_data(session,device_id):
    return session.query(DefaultDeviceData).filter_by(device_id=device_id).order_by(DefaultDeviceData.date.desc()).first()

def get_configuration_view_list(session, device_id):
    config_objects_list = []
    config_list = session.query(DefaultDeviceConfig).filter_by(device_id=device_id).all()
    for config in config_list:     
        config_object = DefaultDeviceConfigView(
            uuid=config.uuid,
            name=config.name,
            is_active=enums.ConfigState(config.is_active).name,
            temp=str(config.temp_treshold),
            led_state=enums.ConfigState(config.led_state).name,
            weekdays=code_decode.decode_weekdays(config.weekdays),
            start_time=str(config.start_time),
            finish_time=str(config.finish_time),
            creation_date=str(config.create_date)
        )
        config_objects_list.append(config_object)
        
    return config_objects_list

def get_configuration_view(session, device_id):
    config = session.query(HeaterConfig).filter_by(id=configId).first()
    return DefaultDeviceConfigView(
    ) 

def save_configuration(session, form, device_id, config_uuid):    
    #nauja prietaiso konfiguracija
    if (config_uuid is None):
        return DefaultDeviceConfig(
            temp_treshold=form.temp_treshold.data,
            led_state=form.led_state.data,
            name=form.config_name.data,
            is_active=form.is_active.data,
            weekdays=code_decode.code_weekdays(form),
            start_time=form.start_time.data,
            finish_time=form.finish_time.data,
            device_id=device_id
        )
    #egzistuojanti konfiguracija
    else:
        config = session.query(DefaultDeviceConfig).filter_by(uuid=config_uuid).first()

        config.temp_treshold=form.temp_treshold.data
        config.led_state=form.led_state.data
        config.name=form.config_name.data
        config.is_active=form.is_active.data
        config.weekdays=code_decode.code_weekdays(form)
        config.start_time=form.start_time.data
        config.finish_time=form.finish_time.data
        config.device_id=device_id

        return config

def append_to_config_form(config, form):
    form.config_name.data = config.name
    form.temp_treshold.data = config.temp_treshold
    form.led_state.data = config.led_state
    form.start_time.data = config.start_time
    form.finish_time.data = config.finish_time
    form.is_active.data = config.is_active
    form.monday.data = "0" in config.weekdays
    form.tuesday.data = "1" in config.weekdays
    form.wednesday.data = "2" in config.weekdays
    form.thursday.data = "3" in config.weekdays
    form.friday.data = "4" in config.weekdays
    form.saturday.data = "5" in config.weekdays
    form.sunday.data = "6" in config.weekdays

    return form

def form_mqtt_payload(session, command, device_id):
    lastData = session.query(DefaultDeviceData).filter_by(device_id=device_id).order_by(DefaultDeviceData.date.desc()).first()

    if (lastData is not None):
        if (command == 'LED OFF' and lastData.led_state == True):
            return "LED OFF"
        elif (command == 'LED ON' and lastData.led_state == False):
            return "LED ON"

    return "NO ACT"