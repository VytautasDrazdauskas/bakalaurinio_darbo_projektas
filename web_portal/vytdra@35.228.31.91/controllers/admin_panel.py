from app import db
from app import Logger
from app.models import Users, Devices#DB lentu modeliai
from app.view_models import ProfilesView, DevicesView
from flask import Flask,json,render_template,jsonify,Markup
from sqlalchemy.orm import lazyload

def get_profiles():
    session = db.session.session_factory()  
    users = session.query(Users).all()  

    usersArr = []
    for user in users:
        userObj = ProfilesView(
            id=user.id,
            email=user.email,
            name=user.name,
            device_count=0,
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
            user=device.user.name,
            state="Aktyvus"
        )
        devicesArr.append(deviceObj)

    return jsonify({
            'data': [result.serialize for result in devicesArr]
        })

def save_device_form(form, device_id=None):
    try:
        session = db.session.session_factory() 
        session.autocommit = False #neleis daryti auto commit, po kiekvieno objekto pakeitimo bus daromas flush.
        session.autoflush = True

        if (device_id is None):           

            deviceObj = Devices(
                mac = form.mac.data
            )
            session.add(stationObj)
        else:
            device = session.query(Devices).filter(Devices.id == device_id).first()
            device.mac = form.mac.data
            
        session.commit()
    except Exception as ex:
        session.rollback()
        Logger.log_error(ex.args)
        return False
    finally:
        session.close()

    return True