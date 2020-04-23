from app import db
from app import Logger
from app.models import Users, Devices#DB lentu modeliai
from app.view_models import ProfilesView, DevicesView
from flask import Flask,json,render_template,jsonify,Markup
from sqlalchemy.orm import lazyload
from sqlalchemy.orm.strategy_options import joinedload
from app.services.devices_service import DevicesService
import app.helpers.messaging as messenger
import uuid
from flask.helpers import flash

def get_profiles():
    session = db.session.session_factory()  
    users = session.query(Users).all()  

    usersArr = []
    for user in users:
        userObj = ProfilesView(
            id=user.id,
            email=user.email,
            name=user.name,
            device_count=sum(1 for _ in user.assigned_devices),
            uuid=user.uuid
        )
        usersArr.append(userObj)

    return jsonify({
            'data': [result.serialize for result in usersArr]
        })

def get_system_devices():
    session = db.session.session_factory() 

    devices = session.query(Devices).all()  
    
    devicesArr = []
    for device in devices:
        deviceObj = DevicesView(
            id=device.id,
            mac=device.mac,
            uuid=device.uuid,
            user=device.user.email if device.user != None else "Nepriskirta",
            state=None
        )
        devicesArr.append(deviceObj)

    session.close()

    return jsonify({
            'data': [result.serialize for result in devicesArr]
        })

def get_system_device(id):
    session = db.session.session_factory() 
    device = session.query(Devices).filter_by(id=id).first()

    device.user = device.user
    session.close

    return device

def save_device_form(form):
    try:
        session = db.session.session_factory() 
        session.autocommit = False #neleis daryti auto commit, po kiekvieno objekto pakeitimo bus daromas flush.
        session.autoflush = True

        id = int(form.id.data) if form.id.data is not None and form.id.data != '' else None

        if (id is None):   
                    
            deviceObj = Devices(
                mac = form.mac.data
            )

            device = session.query(Devices).filter(Devices.mac == form.mac.data).first()
            if (device is not None):
                raise Exception("Prietaisas su tokiu MAC adresu jau egzistuoja!")

            service = DevicesService()
            response = service.generate_device_keys(mac=deviceObj.mac, uuid=deviceObj.uuid)

            if (not response.success):
                raise Exception(response.message)

            session.add(deviceObj)            
            flash('Prietaisas MAC: ' + deviceObj.mac + ' sukurtas!', 'success')  
        else:            
            device = session.query(Devices).filter(Devices.id == id).first()
            device.mac = form.mac.data
            
        session.commit()
    except Exception as ex:
        session.rollback()        
        Logger.log_error(ex.args[0])
        session.close()   
        flash(ex.args[0], 'danger')
        return False
    finally:
        session.close()      
        return True
    