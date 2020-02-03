from app import db
from app.helpers.userBase import *
from app.models import *
from app.deviceTypes.heater import *
from app.deviceTypes.defaultDevice import *
import app.deviceTypes.heater as heater
import app.deviceTypes.defaultDevice as defaultDevice
from app.viewModels import UserDevicesView
import app.helpers.enums as enums
import app.helpers.messaging as messenger
from _datetime import datetime
from flask import flash, jsonify
from flask_login import current_user
import paho.mqtt.publish as publish
import app.loadConfig as config

def add_new_device(code, deviceName, deviceType):   
    session = create_user_session()
    mainDbSession = db.session.session_factory()  
      
    try:   
        #sukuriam prietaisu lenta, jei tokios nera
        if not table_exists("user_devices"):                 
            UserDevices.__table__.create(session.bind)
            session.commit()
                
        #patikrinam, ar toks prietaisas egzistuoja MainDB        
        deviceInMain = mainDbSession.query(Devices).filter_by(uuid=code).first()
        
        if deviceInMain is None:
            flash("Toks prietaisas neegzistuoja!","danger")
            session.rollback()
            mainDbSession.rollback()
        elif deviceInMain.user_id is not None and deviceInMain.user_id != current_user.id:
            flash("Prietaisas priklauso kitam naudotojui!","danger")
            session.rollback()
            mainDbSession.rollback()
        elif deviceInMain.user_id is None:
            device = session.query(UserDevices).filter_by(mac=deviceInMain.mac).first()
            #pridedam prietaisa i userio DB
            if not device:
                new_device = UserDevices(
                    device_name=deviceName,
                    mac=deviceInMain.mac,
                    status=enums.DeviceState.Registered.value,
                    device_type=deviceType,
                    )
                    
                session.add(new_device) 

                deviceInMain.user_id = current_user.id 
                
                if (new_device.device_type == enums.DeviceType.Heater.value): 
                    #sukuriam lentas, jei tokios nera
                    heater.createTablesIfNeeded(session)
                   
                if (new_device.device_type == enums.DeviceType.Default.value): 
                    #sukuriam lentas, jei tokios nera
                    defaultDevice.createTablesIfNeeded(session)
                                
                session.commit()
                mainDbSession.commit()

                flash('Prietaisas sėkmingai užregistruotas!','success')
            else:
                flash("Toks prietaisas jau pridėtas!","danger")
                session.rollback()
                mainDbSession.rollback()
        else:
            flash("Toks prietaisas jau pridėtas!","danger")
            session.rollback()
            mainDbSession.rollback()

    except Exception as Ex:
        flash('Nenumatyta klaida: ' + Ex.args,'danger')

    finally:
        session.close()


def getUserDevices():
    try:
        session = create_user_session() 

        #sukuriam prietaisu lenta, jei tokios nera
        if not table_exists("user_devices"):                 
            UserDevices.__table__.create(session.bind)

        devices = session.query(UserDevices).all()  

        session.close()

        devicesArr = []
        for device in devices:
            deviceObj = UserDevicesView(
                id=device.id,  
                deviceName=device.device_name,
                mac=device.mac,
                state=enums.DeviceState(device.status).name,
                dateAdded=str(device.date_added_local),
                deviceType=device.device_type,
                deviceTypeName=enums.DeviceType(device.device_type).name
            )
            devicesArr.append(deviceObj)

        return jsonify({
                'data': [result.serialize for result in devicesArr]
            })
    except Exception as ex:
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def getUserDeviceData(deviceId):
    session = create_user_session() 
    
    device = session.query(UserDevices).filter_by(id=deviceId).first()

    result = None
    if (device.device_type == enums.DeviceType.Heater.value):
        result = heater.getData(session,device.id)
    elif (device.device_type == enums.DeviceType.Default.value):
        result = defaultDevice.getData(session,device.id)

    session.close()
    return result

def getLastData(deviceId):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=deviceId).first()
    lastData = None

    if (device.device_type == enums.DeviceType.Heater.value):
        lastData = heater.getMostRecentData(session, device.id)
    elif (device.device_type == enums.DeviceType.Default.value):
        lastData = defaultDevice.getMostRecentData(session, device.id)
    
    session.close()
    return lastData
    
def getUserDevice(deviceId):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=deviceId).first() 

    session.close()

    return device

def getUserDeviceViewModel(deviceId):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=deviceId).first() 
    
    session.close()

    model = UserDevicesView(
            id=device.id,
            deviceName=device.device_name,
            mac=device.mac,
            state=enums.DeviceState(device.status).name,
            dateAdded=str(device.date_added_local),
            deviceType=device.device_type,
            deviceTypeName=enums.DeviceType(device.device_type).name
        )

    return model

def appendConfigDataToForm(device,config,form):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device.id).first()

    if (device.device_type == enums.DeviceType.Heater.value):
        form = heater.apppendConfigToForm(config, form)
    elif (device.device_type == enums.DeviceType.Default.value):
        form = defaultDevice.apppendConfigToForm(config, form)
    
    return form

#Prietaisų konfigūracijos
def getConfig(deviceId, uuid=None):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=deviceId).first()
    config = None
    
    if (uuid is None):
        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(device_id=deviceId,is_active=True).order_by(start_time).first()
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(device_id=deviceId,is_active=True).first()
    else:
        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=uuid).first()
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=uuid).first()
    
    session.close()
    return config

#Prietaisų konfigūracijos
def getConfigForm(device): 
    if (device.deviceType == enums.DeviceType.Heater.value):
        return HeaterConfigForm()
    elif (device.deviceType == enums.DeviceType.Default.value):
        return DefaultDeviceConfigForm()    
    return None

def getUserDeviceConfigurations(deviceId):
    try:
        session = create_user_session() 
        device = session.query(UserDevices).filter_by(id=deviceId).first() 
            
        configArray = []
        if (device.device_type == enums.DeviceType.Heater.value):        
            configArray = heater.getConfigViewList(session, device.id)
        elif (device.device_type == enums.DeviceType.Default.value):
            configArray = defaultDevice.getConfigViewList(session, device.id)

        session.close()    
        return jsonify({
                'data': [result.serialize for result in configArray]
            })
        
    except Exception as ex:
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def saveDeviceConfig(form, device, configUUID):
    try:
        session = create_user_session()
        deviceConfig = None
                
        if (device.deviceType == enums.DeviceType.Heater.value):        
            deviceConfig = heater.saveConfig(session, form, device.id, configUUID)
        elif (device.deviceType == enums.DeviceType.Default.value):
            deviceConfig = defaultDevice.saveConfig(session, form, device.id, configUUID) 

        if (configUUID is None):
            session.add(deviceConfig)
            response = configureDeviceJobs(device,deviceConfig,deviceConfig.is_active)                       
        else:
            response = configureDeviceJobs(device,deviceConfig,deviceConfig.is_active)

        if (response is not None):            
            session.rollback()     
            flash('Vidinė klaida! Konfigūracija "' + deviceConfig.name + '" pagrindinėje duomenų bazėje neišsaugota!','danger')     
                    
        session.commit()
        flash('Konfigūracija "' + deviceConfig.name + '" išsaugota!','success')        
    except Exception as ex:
        flash('Nenumatyta klaida išsaugant "' + deviceConfig.name + '" prietaisą! Klaida: ' + ex.args,'success')
        session.rollback()
    finally:
        session.close()

def validateConfigForm(form):
    if (not form.configName.data):
        flash('Įveskite konfigūracijos pavadinimą!','danger')
        return True
    elif (not form.startTime.data):
        flash('Įveskite programos pradžios laiką!','danger')
        return True
    elif (not form.finishTime.data):
        flash('Įveskite programos pabaigos laiką!','danger')
        return True
    elif (not form.monday.data and not form.tuesday.data and not form.thursday.data and not form.wednesday.data and not form.friday.data and not form.saturday.data and not form.sunday.data):
        flash('Įveskite bent vieną savaitės dieną!','danger')
        return True
    else:
        return False

def configureDeviceJobs(device,config,isActive):
    try:
        mainDbSession = db.session.session_factory()
        mainDbDevice = mainDbSession.query(Devices).filter_by(mac=device.mac,user_id=current_user.id).first()

        if (mainDbDevice is None): #jei prietaisas nepriskirtas useriui
            return messenger.RaiseNotification(False, 'Naudotojas neturi priskirto prietaiso pagrindinėje duomenų bazėje!')

        if (isActive): 
            job = mainDbSession.query(DeviceJobs).filter_by(config_uuid=config.uuid,device_id=mainDbDevice.id).first()

            if (job is None): #jei jobas neegzistuoja, kuriam nauja         
                job = DeviceJobs(
                    device_id=mainDbDevice.id,
                    start_time=config.start_time,
                    finish_time=config.finish_time,
                    weekdays=config.weekdays,
                    config_uuid=config.uuid
                )
                mainDbSession.add(job)  
            else:
                job.device_id=mainDbDevice.id,
                job.start_time=config.start_time,
                job.finish_time=config.finish_time,
                job.weekdays=config.weekdays,
                job.config_uuid=config.uuid
        else: #jobo naikinimas
            job = mainDbSession.query(DeviceJobs).filter_by(config_uuid=config.uuid,device_id=mainDbDevice.id).first()

            if (job is not None):
                mainDbSession.delete(job)

        mainDbSession.commit()
        return None
    except Exception as ex:
        raise
    finally:
        mainDbSession.close()
    
def activateDeviceConfig(device, configUUID):
    try:
        session = create_user_session()

        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=configUUID).first()    
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=configUUID).first() 

        if (config.is_active):
            config.is_active = False
            response = configureDeviceJobs(device,config,False)

            if (response is not None):
                session.rollback()
                return response

            session.commit()
            return messenger.RaiseNotification(True, 'Konfigūracija "' + config.name + '" deaktyvuota!')
        else:
            config.is_active = True
            response = configureDeviceJobs(device,config,True)

            if (response is not None):
                session.rollback()
                return response

            session.commit()
            return messenger.RaiseNotification(True, 'Konfigūracija "' + config.name + '" aktyvuota!')
    
    except Exception as ex:
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def deleteDeviceConfig(device, configUUID):
    try:
        session = create_user_session()

        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=configUUID).first() 
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=configUUID).first()

        configName = config.name

        configureDeviceJobs(device,config,False)
        session.delete(config)
        session.commit()
        return messenger.RaiseNotification(True, 'Konfigūracija "' + configName + '" panaikinta!')    
    except Exception as ex:
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def executeDeviceAction(id, command):    
    if current_user.is_authenticated:    
        try:
            session = create_user_session()     
            device = session.query(UserDevices).filter_by(id=id).first()

            if (device.status != enums.DeviceState.Active.value and device.status != enums.DeviceState.Registered.value):
                return messenger.RaiseNotification(False,'Prietaisas nėra aktyvus! Negalima operacija!', )
                    
            systemName = "system"
            topic = current_user.uuid + "/" + systemName + "/" + device.mac + "/control"

            payload = None

            #komandos parinkimas
            if (device.device_type == enums.DeviceType.Heater.value): #kaitintuvas             
                payload = heater.formMqttPayload(session, command, device.id)
            elif (device.device_type == enums.DeviceType.Default.value): #default             
                payload = defaultDevice.formMqttPayload(session, command, device.id)

            #common commands
            if (command == 'REBOOT'):
                device.status = enums.DeviceState.Rebooting.value
                session.commit()           
                payload = "reboot"   
            
            #publishinam komanda
            if (payload is not None):
                publish.single(topic=topic, payload=payload, hostname=config.broker_ip, port=config.broker_port, qos=2)
            #else:
                #return messenger.RaiseNotification(True, 'Neatlikti jokie veiksmai! Pakeiskite parametrus ir bandykite vėl.')

        except Exception as ex:
            return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
        finally:
            session.close()
            
    else:
        return messenger.RaiseNotification(False, 'Naudotojas nėra autentifikuotas!')
    
    return messenger.RaiseNotification(True, 'Komanda įvykdyta sėkmingai!')

    


