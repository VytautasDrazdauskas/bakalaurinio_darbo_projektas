from app import db
from app.models import Users, Devices#DB lentu modeliai
from app.viewModels import ProfilesView, DevicesView
from flask import Flask,json,render_template,jsonify,Markup
from sqlalchemy.orm import lazyload

def getProfiles():
    session = db.session.session_factory()  
    users = session.query(Users).all()  

    usersArr = []
    for user in users:
        userObj = ProfilesView(
            id=user.id,
            email=user.email,
            name=user.name,
            devCount=0,
            uuid=user.uuid
        )
        usersArr.append(userObj)

    return jsonify({
            'data': [result.serialize for result in usersArr]
        })

def getAllDevices():
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

def saveDeviceForm(form, deviceId=None):
    try:
        session = db.session.session_factory() 
        session.autocommit = False #neleis daryti auto commit, po kiekvieno objekto pakeitimo bus daromas flush.
        session.autoflush = True

        if (deviceId is None):           

            deviceObj = Devices(
                mac = form.mac.data
            )
            session.add(stationObj)
        else:
            device = session.query(Devices).filter(Devices.id == deviceId).first()
            device.mac = form.mac.data
            
        session.commit()
    except:
        session.rollback()
        return False
    finally:
        session.close()

    return True