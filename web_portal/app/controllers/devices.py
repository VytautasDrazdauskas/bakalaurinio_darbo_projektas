from app import db
from app import Logger
from app.helpers.user_base import *
import app.models as models
from app.device_types.heater import *
from app.device_types.default_device import *
import app.device_types.heater as heater
import app.device_types.default_device as default_device
from app.view_models import UserDevicesView, UserDeviceHistoryView
import app.helpers.enums as enums
import app.helpers.messaging as messenger
from _datetime import datetime
from flask import flash, jsonify, json
from flask_login import current_user
import paho.mqtt.publish as publish
import app.load_config as app_config
from app.services.mqqt_service import MqttService
from app.helpers.code_decode import JsonParse
from app import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from app.helpers.code_decode import decode
import numpy as np
import cv2
from PIL import Image

class Parse(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def select_device_type(device):
    if (device.device_type == enums.DeviceType.Heater.value): #kaitintuvas             
        return heater
    elif (device.device_type == enums.DeviceType.Default.value): #default             
        return default_device
    else:
        return None

def get_device_config_form(device): 
    device_type = select_device_type(device)
    return device_type.get_config_form()

def new_device_post(request, device_name, device_type):
    if 'file' not in request.files:
        flash('Neįkeltas failas', 'danger')
        return
    file = request.files['file']

    if file.filename == '':
        flash('Neįkeltas failas', 'danger')
        return

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        try:
            response = file.read()
            
            image = cv2.imdecode(np.fromstring(response, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.resize(image, (360, 480))
            code = decode(img)
            if code:
                add_new_device(code, device_name, device_type)
            else:
                flash("QR kodas nenuskaitytas!", "danger")
                return

        except Exception as Ex:
            flash("Prietaiso nepavyko užregistruoti!", "danger")
            Logger.log_error(Ex.args)

    else:
        flash("Failas nėra tinkamo formato!", "danger")

def save_device_history(session,device,text):
    device_history = models.UserDeviceHistory(
        device_id=device.id,
        text=text
    )
    session.add(device_history)

def add_new_device(code, device_name, device_type):   
    session = create_user_session()
    main_db_session = db.session.session_factory()  
      
    try:   
        #sukuriam prietaisu lenta, jei tokios nera
        if not table_exists("user_devices"):                 
            models.UserDevices.__table__.create(session.bind)
            session.commit()

        if not table_exists("user_device_history"):                 
            models.UserDeviceHistory.__table__.create(session.bind)
            session.commit()
                
        #patikrinam, ar toks prietaisas egzistuoja MainDB        
        deviceInMain = main_db_session.query(models.Devices).filter_by(uuid=code).first()
        
        if deviceInMain is None:
            flash("Toks prietaisas neegzistuoja!","danger")
            session.rollback()
            main_db_session.rollback()
        elif deviceInMain.user_id is not None and deviceInMain.user_id != current_user.id:
            flash("Prietaisas priklauso kitam naudotojui!","danger")
            session.rollback()
            main_db_session.rollback()
        elif deviceInMain.user_id is None:
            device = session.query(models.UserDevices).filter_by(mac=deviceInMain.mac).first()
            #pridedam prietaisa i userio DB
            if not device:
                new_device = models.UserDevices(
                    device_name=device_name,
                    mac=deviceInMain.mac,
                    status=enums.DeviceState.Registered.value,
                    device_type=device_type,
                    publish_interval=30
                    )
                    
                session.add(new_device) 

                deviceInMain.user_id = current_user.id 

                device_type = select_device_type(device)

                device_type.create_tables(session)

                #konfiguruojam devaisa. Nustatome devaiso confige naudotojo uuid
                systemName = "system"
                defaultUUID = "00000000-0000-0000-0000-000000000000"
                
                payload = "useruuid=" + current_user.uuid
                topic = defaultUUID + "/" + systemName + "/" + deviceInMain.mac + "/setconfig"
                response_topic = topic + "/response"

                response = Parse(MqttService.publish_with_response(topic, response_topic, payload, 10))

                if(response.success):
                    session.commit()
                    main_db_session.commit()
                    flash('Prietaisas sėkmingai užregistruotas!','success')
                else:
                    flash('Prietaisas neužregistruotas!','danger')

                #REIKIA VALIDACIJOS, kad devaisas paupdatino savo userio uuid
                #Dar geriau butu per RESTful API daryti. Gal reiketu panaudoti QR koda patvirtinimui is devaiso puses.
                                
                
            else:
                flash("Toks prietaisas jau pridėtas!","danger")
                session.rollback()
                main_db_session.rollback()
        else:
            flash("Toks prietaisas jau pridėtas!","danger")
            session.rollback()
            main_db_session.rollback()

    except Exception as Ex:
        Logger.log_error(Ex.args)
        flash('Nenumatyta klaida: ' + Ex.args,'danger')

    finally:
        session.close()


def get_user_devices():
    try:
        session = create_user_session() 
        
        if not table_exists("user_devices"):                 
            models.UserDevices.__table__.create(session.bind)
            session.commit()
            
        devices = session.query(models.UserDevices).all()  

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

def get_device_data_range(device_id, date_from, date_to, resolution = None):
    session = create_user_session() 
    
    device = session.query(models.UserDevices).filter_by(id=device_id).first()

    device_type = select_device_type(device)
    result = device_type.get_data_range(session, device.id, date_from, date_to, resolution)
    session.close()
    return result

def get_device_data(device_id):
    session = create_user_session() 
    
    device = session.query(models.UserDevices).filter_by(id=device_id).first()

    device_type = select_device_type(device)
    result = device_type.get_data(session,device.id)

    session.close()
    return result

def get_device_action_history(device_id):
    session = create_user_session() 

    history_data = session.query(models.UserDeviceHistory).filter_by(device_id=device_id).all()

    data_object_list = []
    for data in history_data:
        data_object = UserDeviceHistoryView(
            id=data.id,
            text=data.text,
            date=str(data.date)
        )
        data_object_list.append(data_object)

    return jsonify({
            'data': [result.serialize for result in data_object_list]
        })

def get_last_data(device_id):
    session = create_user_session() 

    device = session.query(models.UserDevices).filter_by(id=device_id).first()
    
    device_type = select_device_type(device)
    lastData = device_type.get_last_data(session, device.id)
    
    session.close()
    return lastData
    
def get_user_device(device_id):
    session = create_user_session() 

    device = session.query(models.UserDevices).filter_by(id=device_id).first() 

    session.close()

    return device

def get_device_view_model(device_id):
    session = create_user_session() 

    device = session.query(models.UserDevices).filter_by(id=device_id).first() 
    
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

def get_config_form(device,device_config,form):
    session = create_user_session() 

    device = session.query(models.UserDevices).filter_by(id=device.id).first()
    device_type = select_device_type(device)    
    form = device_type.append_to_config_form(device_config, form)
    
    return form

#Prietaisų konfigūracijos
def get_device_config(device_id, uuid=None):
    session = create_user_session() 

    device = session.query(models.UserDevices).filter_by(id=device_id).first()
    device_type = select_device_type(device)
    device_config = None
    
    if (uuid is None):
        device_config = device_type.get_device_config(session, device_id)
    else:
        device_config = device_type.get_device_config_uuid(session, uuid)
            
    session.close()
    return device_config

#Prietaisų konfigūracijos
def get_device_configurations(device_id):
    try:
        session = create_user_session() 
        device = session.query(models.UserDevices).filter_by(id=device_id).first() 
            
        config_objects_list = []
        device_type = select_device_type(device)      
        config_objects_list = device_type.get_configuration_view_list(session, device.id)

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
        
        device_type = select_device_type(device)                  
        device_config = device_type.save_configuration(session, form, device.id, config_uuid)

        if (config_uuid is None):
            session.add(device_config)
                        
        if (device_config.job_state != enums.ConfigJobState.Running.value):
            response = configure_device_jobs(device,device_config,device_config.is_active)
            if (not response):            
                session.rollback()
            else:                    
                session.commit()
                flash('Konfigūracija "' + device_config.name + '" išsaugota!','success') 
        else:
            session.rollback()
            return flash('Rutininis darbas vykdomas pagal šią konfigūraciją! Atšaukite rutininį darbą!','danger')
               
    except Exception as ex:
        Logger.log_error(ex.args)
        flash('Nenumatyta klaida išsaugant "' + device_config.name + '" prietaisą! Klaida: ' + ex.args,'danger')
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
    elif (not form.duration.data):
        flash('Įveskite programos pabaigos laiką!','danger')
        return True
    elif (not form.monday.data and not form.tuesday.data and not form.thursday.data and not form.wednesday.data and not form.friday.data and not form.saturday.data and not form.sunday.data):
        flash('Įveskite bent vieną savaitės dieną!','danger')
        return True
    else:
        return False

def configure_device_jobs(device,device_config,is_active):
    try:
        main_db_session = db.session.session_factory()
        main_db_device = main_db_session.query(models.Devices).filter_by(mac=device.mac,user_id=current_user.id).first()

        if (main_db_device is None): #jei prietaisas nepriskirtas useriui
            return JsonParse.decode_jsonify(jsonify(success=False, message="Naudotojas neturi priskirto prietaiso pagrindinėje duomenų bazėje!"))

        if (is_active): 
            job = main_db_session.query(models.DeviceJobs).filter_by(config_uuid=device_config.uuid,device_id=main_db_device.id).first()

            if (job is None): #jei jobas neegzistuoja, kuriam nauja         
                job = models.DeviceJobs(
                    device_id=main_db_device.id,
                    start_time=device_config.start_time,
                    duration=device_config.duration,
                    weekdays=device_config.weekdays,
                    config_uuid=device_config.uuid,
                    running=False
                )
                device_config.job_state = enums.ConfigJobState.Idle.value
                main_db_session.add(job)  
            else:
                if (job.running == False):
                    job.device_id=main_db_device.id,
                    job.start_time=device_config.start_time,
                    job.duration=device_config.duration,
                    job.weekdays=device_config.weekdays,
                    job.config_uuid=device_config.uuid
                else: 
                    return JsonParse.decode_jsonify(jsonify(success=False, message="Job\'as šiuo metu dirba! Negalima redaguoti konfigūracijos!"))
        else: #jobo naikinimas
            job = main_db_session.query(models.DeviceJobs).filter_by(config_uuid=device_config.uuid,device_id=main_db_device.id).first()

            device_config.job_state = enums.ConfigJobState.Disabled.value

            if (job is not None):
                main_db_session.delete(job)

        main_db_session.commit()
        return JsonParse.decode_jsonify(jsonify(success=True))
    except Exception as ex:
        Logger.log_error(ex.args)
        return JsonParse.decode_jsonify(jsonify(success=False, message="Įvyko vidinė klaida:" + ex.args))
    finally:
        main_db_session.close()

def stop_job(device, config_uuid):
    try:
        session = create_user_session()

        device_type = select_device_type(device)      
        device_config = device_type.get_device_config_uuid(session, config_uuid)
        
        response = execute_device_action(device.id,"STOP JOB")
        
        main_db_session = db.session.session_factory()
        main_db_device = main_db_session.query(models.Devices).filter_by(mac=device.mac,user_id=current_user.id).first()

        if (main_db_device is None): #jei prietaisas nepriskirtas useriui
            return JsonParse.decode_jsonify(jsonify(success=False, message="Naudotojas neturi priskirto prietaiso pagrindinėje duomenų bazėje!"))
        
        job = main_db_session.query(models.DeviceJobs).filter_by(config_uuid=device_config.uuid,device_id=main_db_device.id).first()
        if (job is not None):
            job.running = False
            job.finish_time = None
            main_db_session.commit()
        else:
            return JsonParse.decode_jsonify(jsonify(success=False, message="Rutininis darbas nerastas!"))
        
        device_config.job_state = enums.ConfigJobState.Idle.value
        
        save_device_history(session=session,device=device,text="Rutininis darbas pagal konfigūraciją \"" + device_config.name + "\" sustabdytas naudotojo iniciatyva!")

        session.commit()
        return response
    except Exception as ex:
        session.rollback()
        main_db_session.rollback()
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        main_db_session.close()
        session.close()
    
def activate_device_configuration(device, config_uuid):
    try:
        session = create_user_session()

        device_type = select_device_type(device)
        device_config = device_type.get_device_config_uuid(session, config_uuid)

        if (device_config.job_state != enums.ConfigJobState.Running.value):
            if (device_config.is_active):
                device_config.is_active = enums.ConfigState.Disabled.value
                device_config.job_state = None

                response = configure_device_jobs(device,device_config,False)

                if (not response.success):
                    session.rollback()
                    return messenger.raise_notification(response.success, response.message)

                session.commit()
                return messenger.raise_notification(True, 'Konfigūracija "' + device_config.name + '" deaktyvuota!')
            else:
                device_config.is_active = enums.ConfigState.Active.value
                device_config.job_state = enums.ConfigJobState.Idle.value
                response = configure_device_jobs(device,device_config,True)

                if (not response.success):
                    session.rollback()
                    return messenger.raise_notification(response.success, response.message)

                session.commit()
                return messenger.raise_notification(True, 'Konfigūracija "' + device_config.name + '" aktyvuota!')
        else:
            session.rollback()
            return messenger.raise_notification(False, 'Rutininis darbas vykdomas pagal šią konfigūraciją! Atšaukite rutininį darbą!')

    except Exception as ex:
        session.rollback()
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def delete_device_config(device, config_uuid):
    try:
        session = create_user_session()

        device_type = select_device_type(device)
        device_config = device_type.get_device_config_uuid(session, config_uuid)

        config_name = device_config.name
        if (device_config.job_state != enums.ConfigJobState.Running.value):
            configure_device_jobs(device,device_config,False)
            session.delete(device_config)
            session.commit()
            return messenger.raise_notification(True, 'Konfigūracija "' + config_name + '" panaikinta!')   
        else:
            session.rollback()
            return messenger.raise_notification(False, 'Rutininis darbas vykdomas pagal šią konfigūraciją! Atšaukite rutininį darbą!')
        
    except Exception as ex:
        session.rollback()
        Logger.log_error(ex.args)
        return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
    finally:
        session.close()

def execute_device_action(id, command):    
    if current_user.is_authenticated:    
        try:
            session = create_user_session()     
            device = session.query(models.UserDevices).filter_by(id=id).first()

            if (device.status != enums.DeviceState.Active.value and device.status != enums.DeviceState.Registered.value):
                return messenger.raise_notification(False,'Prietaisas nėra aktyvus! Negalima operacija!', )
                    
            systemName = "system"
            topic = current_user.uuid + "/" + systemName + "/" + device.mac + "/control"
            response_topic = topic + "/response"

            payload = None

            #komandos parinkimas
            device_type = select_device_type(device)
            payload = device_type.form_mqtt_payload(command)

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
            session.rollback()
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
            device = session.query(models.UserDevices).filter_by(id=device_id).first()

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
            session.rollback()
            Logger.log_error(ex.args)
            return messenger.raise_notification(False, 'Įvyko vidinė klaida:' + ex.args)
        finally:
            session.close()
            
    else:
        return messenger.raise_notification(False, 'Naudotojas nėra autentifikuotas!')

