from app import db
from app.helpers.userBase import *
from app.models import UserDevices, Devices, Users
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
                    device_type=deviceType
                    )
                session.add(new_device) 

                deviceInMain.user_id = current_user.id 
                
                if (new_device.device_type == enums.DeviceType.Heater.value): 
                    #sukuriam lentas, jei tokios nera
                    heater.createTablesIfNeeded()
                   
                if (new_device.device_type == enums.DeviceType.Default.value): 
                    #sukuriam lentas, jei tokios nera
                    defaultDevice.createTablesIfNeeded()
                
                mainDbSession.commit()
                session.commit()

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
        raise

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
                device.id,
                device.device_name,
                device.mac,
                enums.DeviceState(device.status).name,
                str(device.date_added_local),
                device.device_type,
                enums.DeviceType(device.device_type).name
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
            device.id,
            device.device_name,
            device.mac,
            enums.DeviceState(device.status).name,
            str(device.date_added_local),
            device.device_type,
            enums.DeviceType(device.device_type).name
        )

    return model

#Prietaisų konfigūracijos
def getConfig(deviceId):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=deviceId).first()
    config = None
    

    if (device.device_type == enums.DeviceType.Heater.value):
        config = session.query(HeaterConfig).filter_by(device_id=deviceId,is_active=True).order_by(start_time).first()
    elif (device.device_type == enums.DeviceType.Default.value):
        config = session.query(DefaultDeviceConfig).filter_by(device_id=deviceId,is_active=True).first()
    
    session.close()
    return config

#Prietaisų konfigūracijos
def getConfigForm(device): 
    if (device.deviceType == enums.DeviceType.Heater.value):
        return HeaterConfigForm()
    elif (device.deviceType == enums.DeviceType.Default.value):
        return DeviceConfigForm()    
    return None

def getUserDeviceConfigurations(deviceId):
    try:
        session = create_user_session() 
        device = session.query(UserDevices).filter_by(id=deviceId).first() 
            
        if (device.device_type == enums.DeviceType.Heater.value):        
            configArray = heater.getConfigViewList(session, device.id)
        elif (device.device_type == enums.DeviceType.Default.value):
            onfigArray = defaultDevice.getConfigViewList(session, device.id)

        session.close()    
        return jsonify({
                'data': [result.serialize for result in configArray]
            })
        
    except Exception as ex:
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def saveDeviceConfig(form, device, isNewConfig):
    try:
        session = create_user_session()

        if (device.device_type == enums.DeviceType.Heater.value):        
            deviceConfig = heater.saveConfig(session, form, device.id, isNewConfig)
        elif (device.device_type == enums.DeviceType.Default.value):
            deviceConfig = defaultDevice.saveConfig(session, form, device.id, isNewConfig)        

        #prideti joba MainDB!

        session.add(deviceConfig)
        session.commit()
    except Exception as ex:
        session.rollback()
        return messenger.RaiseNotification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()
    return 0

def getUserDeviceConfigModel(deviceId,configId):
    try:
        session = create_user_session() 
        device = session.query(UserDevices).filter_by(id=deviceId).first() 
    
        if (device.device_type == enums.DeviceType.Heater.value):
            config = heater.getConfig(session, device.id)
        elif (device.device_type == enums.DeviceType.Default.value):
            config = defaultDevice.getConfig(session, device.id)
   
        return config

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

    


