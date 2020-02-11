from app import db
from app import Logger
from app.helpers.user_base import *
from app.models import *
from app.device_types.heater import *
from app.device_types.default_device import *
import app.device_types.heater as heater
import app.device_types.default_device as default_device
from app.view_models import UserDevicesView
import app.helpers.enums as enums
import app.helpers.messaging as messenger
from _datetime import datetime
from flask import flash, jsonify, json
from flask_login import current_user
import paho.mqtt.publish as publish
import app.load_config as config
from app.services.mqqt_service import MqttService

class Parse(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)

def add_new_device(code, device_name, device_type):   
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
                    device_name=device_name,
                    mac=deviceInMain.mac,
                    status=enums.DeviceState.Registered.value,
                    device_type=device_type,
                    publish_interval=30
                    )
                    
                session.add(new_device) 

                deviceInMain.user_id = current_user.id 
                
                if (new_device.device_type == enums.DeviceType.Heater.value): 
                    #sukuriam lentas, jei tokios nera
                    heater.create_tables(session)
                   
                if (new_device.device_type == enums.DeviceType.Default.value): 
                    #sukuriam lentas, jei tokios nera
                    default_device.create_tables(session)

                #konfiguruojam devaisa. Nustatome devaiso confige naudotojo uuid
                systemName = "system"
                defaultUUID = "00000000-0000-0000-0000-000000000000"
                
                payload = "useruuid=" + current_user.uuid
                topic = defaultUUID + "/" + systemName + "/" + deviceInMain.mac + "/setconfig"
                response_topic = topic + "/response"

                response = Parse(MqttService.publish_with_response(topic, response_topic, payload, 10))

                if(response.success):
                    session.commit()
                    mainDbSession.commit()
                    flash('Prietaisas sėkmingai užregistruotas!','success')
                else:
                    flash('Prietaisas neužregistruotas!','danger')

                #REIKIA VALIDACIJOS, kad devaisas paupdatino savo userio uuid
                #Dar geriau butu per RESTful API daryti. Gal reiketu panaudoti QR koda patvirtinimui is devaiso puses.
                                
                
            else:
                flash("Toks prietaisas jau pridėtas!","danger")
                session.rollback()
                mainDbSession.rollback()
        else:
            flash("Toks prietaisas jau pridėtas!","danger")
            session.rollback()
            mainDbSession.rollback()

    except Exception as Ex:
        Logger.log_error(Ex.args)
        flash('Nenumatyta klaida: ' + Ex.args,'danger')

    finally:
        session.close()


def get_user_devices():
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
                device_name=device.device_name,
                mac=device.mac,
                state=enums.DeviceState(device.status).name,
                date_added=str(device.date_added_local),
                device_type=device.device_type,
                device_type_name=enums.DeviceType(device.device_type).name,
                publish_interval=device.publish_interval
            )
            devicesArr.append(deviceObj)

        return jsonify({
                'data': [result.serialize for result in devicesArr]
            })
    except Exception as ex:
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def get_device_data(device_id):
    session = create_user_session() 
    
    device = session.query(UserDevices).filter_by(id=device_id).first()

    result = None
    if (device.device_type == enums.DeviceType.Heater.value):
        result = heater.get_data(session,device.id)
    elif (device.device_type == enums.DeviceType.Default.value):
        result = default_device.get_data(session,device.id)

    session.close()
    return result

def get_last_data(device_id):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device_id).first()
    lastData = None

    if (device.device_type == enums.DeviceType.Heater.value):
        lastData = heater.get_last_data(session, device.id)
    elif (device.device_type == enums.DeviceType.Default.value):
        lastData = default_device.get_last_data(session, device.id)
    
    session.close()
    return lastData
    
def get_user_device(device_id):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device_id).first() 

    session.close()

    return device

def get_device_view_model(device_id):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device_id).first() 
    
    session.close()

    model = UserDevicesView(
            id=device.id,
            device_name=device.device_name,
            mac=device.mac,
            state=enums.DeviceState(device.status).name,
            date_added=str(device.date_added_local),
            device_type=device.device_type,
            device_type_name=enums.DeviceType(device.device_type).name,
            publish_interval=device.publish_interval
        )

    return model

def get_config_form(device,config,form):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device.id).first()

    if (device.device_type == enums.DeviceType.Heater.value):
        form = heater.append_to_config_form(config, form)
    elif (device.device_type == enums.DeviceType.Default.value):
        form = default_device.append_to_config_form(config, form)
    
    return form

#Prietaisų konfigūracijos
def get_device_config(device_id, uuid=None):
    session = create_user_session() 

    device = session.query(UserDevices).filter_by(id=device_id).first()
    config = None
    
    if (uuid is None):
        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(device_id=device_id,is_active=True).order_by(start_time).first()
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(device_id=device_id,is_active=True).first()
    else:
        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=uuid).first()
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=uuid).first()
    
    session.close()
    return config

#Prietaisų konfigūracijos
def get_device_config_form(device): 
    if (device.device_type == enums.DeviceType.Heater.value):
        return HeaterConfigForm()
    elif (device.device_type == enums.DeviceType.Default.value):
        return DefaultDeviceConfigForm()    
    return None

def get_device_configurations(device_id):
    try:
        session = create_user_session() 
        device = session.query(UserDevices).filter_by(id=device_id).first() 
            
        config_objects_list = []
        if (device.device_type == enums.DeviceType.Heater.value):        
            config_objects_list = heater.get_configuration_view_list(session, device.id)
        elif (device.device_type == enums.DeviceType.Default.value):
            config_objects_list = default_device.get_configuration_view_list(session, device.id)

        session.close()    
        return jsonify({
                'data': [result.serialize for result in config_objects_list]
            })
        
    except Exception as ex:
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def save_device_config(form, device, config_uuid):
    try:
        session = create_user_session()
        deviceConfig = None
                
        if (device.device_type == enums.DeviceType.Heater.value):        
            deviceConfig = heater.save_configuration(session, form, device.id, config_uuid)
        elif (device.device_type == enums.DeviceType.Default.value):
            deviceConfig = default_device.save_configuration(session, form, device.id, config_uuid) 

        if (config_uuid is None):
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
        Logger.log_error(ex.args)
        flash('Nenumatyta klaida išsaugant "' + deviceConfig.name + '" prietaisą! Klaida: ' + ex.args,'success')
        session.rollback()
    finally:
        session.close()

def validate_config_form(form):
    if (not form.config_name.data):
        flash('Įveskite konfigūracijos pavadinimą!','danger')
        return True
    elif (not form.start_time.data):
        flash('Įveskite programos pradžios laiką!','danger')
        return True
    elif (not form.finish_time.data):
        flash('Įveskite programos pabaigos laiką!','danger')
        return True
    elif (not form.monday.data and not form.tuesday.data and not form.thursday.data and not form.wednesday.data and not form.friday.data and not form.saturday.data and not form.sunday.data):
        flash('Įveskite bent vieną savaitės dieną!','danger')
        return True
    else:
        return False

def configureDeviceJobs(device,config,is_active):
    try:
        mainDbSession = db.session.session_factory()
        mainDbDevice = mainDbSession.query(Devices).filter_by(mac=device.mac,user_id=current_user.id).first()

        if (mainDbDevice is None): #jei prietaisas nepriskirtas useriui
            return messenger.raise_notification(False, 'Naudotojas neturi priskirto prietaiso pagrindinėje duomenų bazėje!')

        if (is_active): 
            job = mainDbSession.query(DeviceJobs).filter_by(config_uuid=config.uuid,device_id=mainDbDevice.id).first()

            if (job is None): #jei jobas neegzistuoja, kuriam nauja         
                job = DeviceJobs(
                    device_id=mainDbDevice.id,
                    start_time=config.start_time,
                    finish_time=config.finish_time,
                    weekdays=config.weekdays,
                    config_uuid=config.uuid,
                    running=False
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
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        mainDbSession.close()
    
def activate_device_configuration(device, config_uuid):
    try:
        session = create_user_session()

        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=config_uuid).first()    
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=config_uuid).first() 

        if (config.is_active):
            config.is_active = False
            response = configureDeviceJobs(device,config,False)

            if (response is not None):
                session.rollback()
                return response

            session.commit()
            return messenger.raise_notification(True, 'Konfigūracija "' + config.name + '" deaktyvuota!')
        else:
            config.is_active = True
            response = configureDeviceJobs(device,config,True)

            if (response is not None):
                session.rollback()
                return response

            session.commit()
            return messenger.raise_notification(True, 'Konfigūracija "' + config.name + '" aktyvuota!')
    
    except Exception as ex:
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def delete_device_config(device, config_uuid):
    try:
        session = create_user_session()

        if (device.device_type == enums.DeviceType.Heater.value):
            config = session.query(HeaterConfig).filter_by(uuid=config_uuid).first() 
        elif (device.device_type == enums.DeviceType.Default.value):
            config = session.query(DefaultDeviceConfig).filter_by(uuid=config_uuid).first()

        config_name = config.name

        configureDeviceJobs(device,config,False)
        session.delete(config)
        session.commit()
        return messenger.raise_notification(True, 'Konfigūracija "' + config_name + '" panaikinta!')    
    except Exception as ex:
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def execute_device_action(id, command):    
    if current_user.is_authenticated:    
        try:
            session = create_user_session()     
            device = session.query(UserDevices).filter_by(id=id).first()

            if (device.status != enums.DeviceState.Active.value and device.status != enums.DeviceState.Registered.value):
                return messenger.raise_notification(False,'Prietaisas nėra aktyvus! Negalima operacija!', )
                    
            systemName = "system"
            topic = current_user.uuid + "/" + systemName + "/" + device.mac + "/control"
            response_topic = topic + "/response"

            payload = None

            #komandos parinkimas
            if (device.device_type == enums.DeviceType.Heater.value): #kaitintuvas             
                payload = heater.form_mqtt_payload(session, command, device.id)
            elif (device.device_type == enums.DeviceType.Default.value): #default             
                payload = default_device.form_mqtt_payload(session, command, device.id)

            #common commands
            if (command == 'REBOOT'):
                device.status = enums.DeviceState.Rebooting.value
                session.commit()           
                payload = "reboot"   
            
            #publishinam komanda
            response = Parse(MqttService.publish_with_response(topic, response_topic, payload, 10))

            if (response.success):
                return messenger.raise_notification(True, 'Komanda įvykdyta sėkmingai!')
            if (response.success is False and response.reason == "Time is up."):
                device.status = enums.DeviceState.Offline.value
                session.commit()
                Logger.log_error(response.reason)
                return messenger.raise_notification(False, 'Baigėsi laikas! Komunikacijos su prietaisu klaida.')
            else:
                return messenger.raise_notification(False, 'Komanda nebuvo įvykdyta.')

        except Exception as ex:
            Logger.log_error(ex.args)
            return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
        finally:
            session.close()
            
    else:
        return messenger.raise_notification(False, 'Naudotojas nėra autentifikuotas!')

    
def send_device_configuration(device_id,data_type,data):
    if current_user.is_authenticated:    
        try:
            session = create_user_session()     
            device = session.query(UserDevices).filter_by(id=device_id).first()

            if (device.status != enums.DeviceState.Active.value and device.status != enums.DeviceState.Registered.value):
                return messenger.raise_notification(False,'Prietaisas nėra aktyvus! Negalima operacija!', )
                    
            #parenkamos temos configo siuntimui ir atsakymo gavimui
            systemName = "system"
            topic = current_user.uuid + "/" + systemName + "/" + device.mac + "/setconfig"
            response_topic = topic + "/response"

            payload = None

            #common commands
            if (data_type == 'interval'):                        
                payload = "delay=" + data 
            else:
                return messenger.raise_notification(False, 'Komanda netinkamo tipo!')
            
            #publishinam komanda
            response = Parse(MqttService.publish_with_response(topic, response_topic, payload, 10))

            if (response.success):
                if (data_type == 'interval'):
                    device.publish_interval = data
                    session.commit()   
                return messenger.raise_notification(True, 'Komanda įvykdyta sėkmingai!')
            if (response.success is False and response.reason == "Time is up."):
                device.status = enums.DeviceState.Offline.value
                session.commit()
                Logger.log_error(response.reason)
                return messenger.raise_notification(False, 'Baigėsi laikas! Komunikacijos su prietaisu klaida.')
            else:
                return messenger.raise_notification(False, 'Komanda nebuvo įvykdyta.')

        except Exception as ex:
            Logger.log_error(ex.args)
            return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
        finally:
            session.close()
            
    else:
        return messenger.raise_notification(False, 'Naudotojas nėra autentifikuotas!')

