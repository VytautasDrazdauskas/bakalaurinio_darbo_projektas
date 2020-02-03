from app import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
from app.helpers.userBase import *
import app.helpers.enums as enums
from flask import jsonify
from app.forms import DeviceConfigBaseForm
from flask_wtf import FlaskForm
from wtforms import *
from app.forms import *
from app.models import DeviceConfigBase, DeviceDataBase
import app.helpers.codeDecode as codeDecode
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
    def __init__(self, id, ledState, temp, date):
        self.id = id
        self.ledState = ledState
        self.temp = temp
        self.date = date

    @property
    def serialize(self):
        return {
            'id': self.id,
            'ledState': self.ledState,
            'temp': self.temp,
            'date': self.date
        }

class DefaultDeviceConfigView():
    def __init__(self, uuid, name, temp, isActive, ledState, weekdays, startTime, finishTime, creationDate):
        self.uuid = uuid
        self.name = name
        self.isActive = isActive
        self.temp = temp
        self.ledState = ledState
        self.weekdays = weekdays
        self.startTime = startTime
        self.finishTime = finishTime
        self.creationDate = creationDate
        
    @property
    def serialize(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'isActive': self.isActive,
            'temp': self.temp,
            'ledState': self.ledState,
            'weekdays' : self.weekdays,
            'startTime': self.startTime,
            'finishTime': self.finishTime,
            'creationDate': self.creationDate
        }

#formos, paveldim bazine klase
class DefaultDeviceConfigForm(DeviceConfigBaseForm):    
    tempTreshold = DecimalField('Maksimali temperatūra')
    ledState = BooleanField('LED būsena')

def createTablesIfNeeded(session):
    if not table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

    if not table_exists("default_device_data"):                 
        DefaultDeviceData.__table__.create(session.bind)

    if not table_exists("default_device_config"):                 
        DefaultDeviceConfig.__table__.create(session.bind)

#metodai
def getData(session, deviceId):
    dataList = session.query(DefaultDeviceData).filter_by(device_id=deviceId).all()  

    dataArr = []
    for data in dataList:
        dataObj = DeviceDataView(
            data.id,
            str(data.led_state),
            str(data.temp) + " C°",
            str(data.date)
        )
        dataArr.append(dataObj)

    return jsonify({
            'data': [result.serialize for result in dataArr]
        })

def getMostRecentData(session,deviceId):
    return session.query(DefaultDeviceData).filter_by(device_id=deviceId).order_by(DefaultDeviceData.date.desc()).first()

def getConfigViewList(session, deviceId):
    configArray = []
    configList = session.query(DefaultDeviceConfig).filter_by(device_id=deviceId).all()
    for config in configList:     
        configObj = DefaultDeviceConfigView(
            uuid=config.uuid,
            name=config.name,
            isActive=enums.ConfigState(config.is_active).name,
            temp=str(config.temp_treshold),
            ledState=enums.ConfigState(config.led_state).name,
            weekdays=codeDecode.decodeWeekdaysLt(config.weekdays),
            startTime=str(config.start_time),
            finishTime=str(config.finish_time),
            creationDate=str(config.create_date)
        )
        configArray.append(configObj)
        
    return configArray

def getConfigView(session, deviceId):
    config = session.query(HeaterConfig).filter_by(id=configId).first()
    return DefaultDeviceConfigView(
    ) 

def saveConfig(session, form, deviceId, configUUID):    
    #nauja prietaiso konfiguracija
    if (configUUID is None):
        return DefaultDeviceConfig(
            temp_treshold=form.tempTreshold.data,
            led_state=form.ledState.data,
            name=form.configName.data,
            is_active=form.isActive.data,
            weekdays=codeDecode.codeWeekdays(form),
            start_time=form.startTime.data,
            finish_time=form.finishTime.data,
            device_id=deviceId
        )
    #egzistuojanti konfiguracija
    else:
        config = session.query(DefaultDeviceConfig).filter_by(uuid=configUUID).first()

        config.temp_treshold=form.tempTreshold.data
        config.led_state=form.ledState.data
        config.name=form.configName.data
        config.is_active=form.isActive.data
        config.weekdays=codeDecode.codeWeekdays(form)
        config.start_time=form.startTime.data
        config.finish_time=form.finishTime.data
        config.device_id=deviceId

        return config

def apppendConfigToForm(config, form):
    form.configName.data = config.name
    form.tempTreshold.data = config.temp_treshold
    form.ledState.data = config.led_state
    form.startTime.data = config.start_time
    form.finishTime.data = config.finish_time
    form.isActive.data = config.is_active
    form.monday.data = "1" in config.weekdays
    form.tuesday.data = "2" in config.weekdays
    form.wednesday.data = "3" in config.weekdays
    form.thursday.data = "4" in config.weekdays
    form.friday.data = "5" in config.weekdays
    form.saturday.data = "6" in config.weekdays
    form.sunday.data = "7" in config.weekdays

    return form

def formMqttPayload(command, deviceId):
    lastData = session.query(DefaultDeviceData).filter_by(device_id=deviceId).order_by(HeaterData.date.desc()).first()

    if (lastData is not None):
        if (command == '1'):  
            if (lastData.led_state == True):
                return "LED OFF"
            else:
                return "LED ON"

    return None