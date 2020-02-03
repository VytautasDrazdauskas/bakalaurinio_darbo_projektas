from app import db
from sqlalchemy.sql.schema import MetaData
from _datetime import datetime
from sqlalchemy.dialects.mysql import BINARY
import app.helpers.enums as enums
import app.helpers.codeDecode as codeDecode
from app.helpers.userBase import *
from flask import jsonify
from app.forms import DeviceConfigBaseForm
from flask_wtf import FlaskForm
from wtforms import *
from app.models import DeviceConfigBase, DeviceDataBase
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

#view models
class HeaterDataView():
    def __init__(self, id, temp, date, actuator1, actuator2, actuator3):
        self.id = id
        self.temp = temp
        self.date = date
        self.actuator1 = actuator1
        self.actuator2 = actuator2
        self.actuator3 = actuator3

    @property
    def serialize(self):
        return {
            'id': self.id,
            'temp': self.temp,
            'date': self.date,
            'actuator1': self.actuator1,
            'actuator2': self.actuator2,
            'actuator3': self.actuator3
        }

class HeaterConfigView():
    def __init__(self, uuid, name, isActive, temp, channels, weekdays, startTime, finishTime, creationDate):
        self.uuid = uuid
        self.name = name
        self.isActive = isActive
        self.temp = temp
        self.channels = channels
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
            'channels': self.channels,
            'weekdays' : self.weekdays,
            'startTime': self.startTime,
            'finishTime': self.finishTime,
            'creationDate': self.creationDate
        }

#formos, paveldim bazine klase
class HeaterConfigForm(DeviceConfigBaseForm):    
    tempTreshold = DecimalField('Maksimali temperatūra')
    channel1 = BooleanField('Pirmas kanalas')
    channel2 = BooleanField('Antras kanalas')
    channel3 = BooleanField('Trečias kanalas')

#METODAI
def createTablesIfNeeded(session):
    if not table_exists("heater_config"):                 
        HeaterConfig.__table__.create(session.bind)

    if not table_exists("heater_data"):                 
        HeaterData.__table__.create(session.bind)

    if not table_exists("heater_config"):                 
        HeaterConfig.__table__.create(session.bind)

#devaisu duomenys
def getData(session,deviceId):
    dataList = session.query(HeaterData).filter_by(device_id=deviceId).all() 

    dataArr = []
    for data in dataList:
        dataObj = HeaterDataView(
            id=data.id,
            actuator1=str(data.actuator1_state),
            actuator2=str(data.actuator2_state),
            actuator3=str(data.actuator3_state),
            temp=str(data.temp) + " C°",
            date=str(data.date)
        )
        dataArr.append(dataObj)

    return jsonify({
            'data': [result.serialize for result in dataArr]
        })

def getMostRecentData(session,deviceId):
    return session.query(HeaterData).filter_by(device_id=deviceId).order_by(HeaterData.date.desc()).first()

#Konfigūracijos
def getConfigViewList(session, deviceId):
    configArray = []
    configList = session.query(HeaterConfig).filter_by(device_id=deviceId).all()   
    
    for config in configList:     
        configObj = HeaterConfigView(
            uuid=config.uuid,
            name=config.name,
            isActive=enums.ConfigState(config.is_active).name,
            temp = str(config.temp_treshold),
            channels = enums.ConfigState(config.actuator1_state).name + ' ' + enums.ConfigState(config.actuator2_state).name + ' ' + enums.ConfigState(config.actuator3_state).name,
            weekdays = codeDecode.decodeWeekdaysLt(config.weekdays),
            startTime = str(config.start_time),
            finishTime = str(config.finish_time),
            creationDate = str(config.create_date)
        )
        configArray.append(configObj)

    return configArray
    
def getConfigView(session, deviceId):
    config = session.query(DefaultDeviceConfig).filter_by(id=configId).first()          
    return HeaterConfigView(
            uuid=config.uuid,
            name=config.config_name,
            isActive=enums.ConfigState(config.is_active).name,
            temp = config.temp_treshold,
            channels = enums.ConfigState(config.actuator1_state).name + ' ' + enums.ConfigState(config.actuator2_state).name + ' ' + enums.ConfigState(config.actuator3_state).name,
            weekdays = config.weekdays,
            startTime = config.start_time,
            finishTime = config.finish_time,
            creationDate = config.create_date,
            modificationDate = config.modification_date
        )

def saveConfig(session, form, deviceId, configUUID):    
    #nauja prietaiso konfiguracija
    if (configUUID is None):
        return HeaterConfig(
            temp_treshold=form.tempTreshold.data,
            actuator1_state=form.channel1.data,
            actuator2_state=form.channel2.data,
            actuator3_state=form.channel3.data,
            name=form.configName.data,
            is_active=form.isActive.data,
            weekdays=codeDecode.codeWeekdays(form),
            start_time=form.startTime.data,
            finish_time=form.finishTime.data,
            device_id=deviceId
        )
    #egzistuojanti konfiguracija
    else:
        config = session.query(HeaterConfig).filter_by(uuid=configUUID).first()

        config.temp_treshold=form.tempTreshold.data
        config.actuator1_state=form.channel1.data
        config.actuator2_state=form.channel2.data
        config.actuator3_state=form.channel3.data
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
    form.channel1.data = config.actuator1_state
    form.channel2.data = config.actuator2_state
    form.channel3.data = config.actuator3_state
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


#valdymas
def formMqttPayload(session, command, deviceId):
    lastData = session.query(HeaterData).filter_by(device_id=deviceId).order_by(HeaterData.date.desc()).first()
    
    if (lastData is not None):
        if (command == '1OFF' and lastData.actuator1_state == True):
            return "ACT1 OFF"
        elif (command == '1ON' and lastData.actuator1_state == False):
            return "ACT1 ON"
        elif (command == '2OFF' and lastData.actuator2_state == True):
            return "ACT2 OFF"
        elif (command == '2ON' and lastData.actuator2_state == False):
            return "ACT2 ON"
        elif (command == '3OFF' and lastData.actuator3_state == True):
            return "ACT3 OFF"
        elif (command == '3ON' and lastData.actuator3_state == False):
            return "ACT3 ON"
    
    if (command == 'ALLON'):
        return "ACT ALL ON"
    elif (command == 'ALLOFF'):
        return "ACT ALL OFF"

    return None


        