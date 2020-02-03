import os
from flask import Blueprint, render_template, request, redirect, flash, url_for, json
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from app.helpers.userBase import table_exists
import app.controllers.profiles as profiles
import app.controllers.devices as userDevice
import app.helpers.enums as enums
from app.helpers.codeDecode import decode
from app.helpers.messaging import RaiseNotification
from app.forms import NewDeviceForm, ProfileForm
import numpy as np
import cv2
from PIL import Image

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/editProfile', methods=['GET','POST'])
@login_required
def editProfile():
    form = ProfileForm()
    name = current_user.name

    if form.validate_on_submit():
        profiles.saveUserProfile(form)

    return render_template('editProfile.html', form=form, name=name)

@main.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    model = profiles.loadUserProfile()
    
    return render_template('profile.html', model=model)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/newDevice', methods=['GET','POST'])
@login_required
def newDevice():
    form = NewDeviceForm()

    if form.validate_on_submit():
        newDevice_post(request,form.deviceName.data,form.deviceType.data.value)
        
    return render_template('devices/newDevice.html',form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
def newDevice_post(request,deviceName,deviceType):
    if 'file' not in request.files:
        flash('Neįkeltas failas','danger')
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        flash('Neįkeltas failas','danger')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        try:
            response = file.read()
            
            image = cv2.imdecode(np.fromstring(response, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.resize(image,(360,480))
            code = decode(img)
            if code:
                userDevice.add_new_device(code,deviceName,deviceType)
            else:
                flash("QR kodas nenuskaitytas!","danger")
                return redirect(request.url) 

        except Exception as Ex:
            flash("Prietaiso nepavyko užregistruoti!","danger")
            return redirect(request.url)
        
    else:
        flash("Failas nėra tinkamo formato!","danger")

@main.route('/userDevices')
@login_required
def userDevices():
    return render_template('devices/userDevicesList.html')

@main.route('/getUserDevicesList', methods=['POST','GET'])
@login_required
def getUserDevicesList():
    return userDevice.getUserDevices()

@main.route('/getUserDeviceData/<id>', methods=['POST','GET'])
@login_required
def getUserDeviceData(id):
    return userDevice.getUserDeviceData(id)

@main.route('/getUserDeviceConfigs/<id>', methods=['POST','GET'])
@login_required
def getUserDeviceConfigs(id):
    return userDevice.getUserDeviceConfigurations(id)  

@main.route('/userDevices/deviceConfigs/<id>', methods=['POST','GET'])
@login_required
def deviceConfigs(id):
    device = userDevice.getUserDeviceViewModel(id)
    return render_template('devices/deviceConfigs.html', device=device)


@main.route('/userDevices/deviceConfigs/edit/<deviceId>/<configUUID>', methods=['POST','GET'])
@login_required
def editDeviceConfig(deviceId,configUUID):
    device = userDevice.getUserDeviceViewModel(deviceId)
    config = userDevice.getConfig(deviceId,configUUID)
    form = userDevice.getConfigForm(device)

    if form.validate_on_submit():
        if userDevice.validateConfigForm(form):
            return render_template('devices/editDeviceConfig.html', form=form, device=device, config=config)

        userDevice.saveDeviceConfig(form, device, configUUID)        
    else:        
        form = userDevice.appendConfigDataToForm(device,config,form)
            
    return render_template('devices/editDeviceConfig.html', form=form, device=device, config=config)

@main.route('/userDevices/deviceConfigs/create/<id>', methods=['POST','GET'])
@login_required
def createDeviceConfig(id):
    device = userDevice.getUserDeviceViewModel(id)
    form = userDevice.getConfigForm(device)
        
    if form.validate_on_submit():
        if userDevice.validateConfigForm(form):
            return render_template('devices/createDeviceConfig.html', form=form, device=device)

        userDevice.saveDeviceConfig(form, device, None)
        return redirect(url_for('main.deviceConfigs',id=id))
    
    return render_template('devices/createDeviceConfig.html', form=form, device=device)
    

@main.route('/userDevices/deviceControlPanel/<id>', methods=['POST','GET'])
@login_required
def deviceControlPanel(id):
    device = userDevice.getUserDeviceViewModel(id)    
    lastData = userDevice.getLastData(id)

    return render_template('devices/userDeviceControlPanel.html', device=device, data=lastData)

@main.route('/userDevices/deviceHistory/<id>', methods=['POST','GET'])
@login_required
def deviceHistory(id):
    device = userDevice.getUserDeviceViewModel(id)
    return render_template('devices/userDeviceHistory.html', device=device)

@main.route('/deviceAction/<id>/<command>', methods=['GET'])
@login_required
def deviceAction(id,command):  
    return userDevice.executeDeviceAction(id,command)


@main.route('/activateDeviceConfig/<deviceId>/<configUUID>', methods=['GET'])
@login_required
def activateDeviceConfig(deviceId,configUUID):
    device = userDevice.getUserDevice(deviceId)       
    return userDevice.activateDeviceConfig(device, configUUID)

@main.route('/deleteDeviceConfig/<deviceId>/<configUUID>', methods=['GET'])
@login_required
def deleteDeviceConfig(deviceId,configUUID):
    device = userDevice.getUserDevice(deviceId)       
    return userDevice.deleteDeviceConfig(device, configUUID)
    