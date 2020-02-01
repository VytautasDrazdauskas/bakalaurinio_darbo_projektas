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

class DefaultDeviceData(DeviceDataBase):
    __tablename__ = "default_device_data"

    temp = db.Column(db.Numeric(8,2), nullable=False)
    led_state = db.Column(db.Boolean, nullable=True)

class DefaultDeviceConfig(DeviceConfigBase):
    __tablename__ = "default_device_config"
   
    temp_treshold = db.Column(db.Numeric(8,2), nullable=True)
    led_state = db.Column(db.Boolean, nullable=True)    

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
    def __init__(self, id, name, temp, isActive, cron, date):
        self.id = id
        self.name = name
        self.temp = temp
        self.isActive = isActive
        self.cron = cron
        self.date = date
        
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'temp': self.temp,
            'isActive': self.isActive,
            'cron': self.cron,
            'date': self.date
        }

class DefaultDeviceConfigForm(DeviceConfigBaseForm):
    tempTreshold = DecimalField('Temperatūros riba')
    ledState = BooleanField('LED būsena')

def createTablesIfNeeded():
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
    return session.query(DefaultDeviceData).filter_by(device_id=device.id).order_by(DefaultDeviceData.date.desc()).first()

def getConfigViewList(session, deviceId):
    configArray = []
    configList = session.query(DefaultDeviceConfig).filter_by(device_id=deviceId).all()
    for config in configList:     
        configObj = DefaultDeviceConfigView(
            id=config.id,
            name=config.config_name,
            temp=str(config.temp_treshold),
            cron=config.cron,
            isActive=enums.ConfigState(config.is_active).name,
            date=config.config_create_date
        )
        configArray.append(configObj)
        
    return configArray

def getConfigView(session, deviceId):
    config = session.query(HeaterConfig).filter_by(id=configId).first()
    return HeaterConfigView(
        config.id,
        config.config_name,
        config.cron,
        enums.ConfigState(config.is_active).name,
        config.config_create_date
    ) 

def saveConfig(session, form, deviceId, isNewConfig):
    #nauja prietaiso konfiguracija
    if (isNewConfig):
        return HeaterConfig(

        )
    #egzistuojanti konfiguracija
    else:
        return 

def formMqttPayload(command, deviceId):
    lastData = session.query(DefaultDeviceData).filter_by(device_id=deviceId).order_by(HeaterData.date.desc()).first()

    if (lastData is not None):
        if (command == '1'):  
            if (lastData.led_state == True):
                return "LED OFF"
            else:
                return "LED ON"

    return None