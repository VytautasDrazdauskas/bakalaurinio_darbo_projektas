import os
from app import Logger
from flask import Blueprint, render_template, request, redirect, flash, url_for, json
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from app.helpers.user_base import table_exists
import app.controllers.profiles as profiles
import app.controllers.devices as user_device
import app.helpers.enums as enums
from app.helpers.code_decode import decode
from app.helpers.messaging import raise_notification
from app.forms import NewDeviceForm, ProfileForm
import numpy as np
import cv2
from PIL import Image

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    name = current_user.name

    if form.validate_on_submit():
        profiles.save_user_profile(form)

    return render_template('edit_profile.html', form=form, name=name)

@main.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    model = profiles.load_user_profile()
    
    return render_template('profile.html', model=model)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/new-device', methods=['GET','POST'])
@login_required
def new_device():
    form = NewDeviceForm()

    if form.validate_on_submit():
        new_device_post(request,form.device_name.data,form.device_type.data.value)
        
    return render_template('devices/new_device.html',form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
def new_device_post(request,device_name,device_type):
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
                user_device.add_new_device(code,device_name,device_type)
            else:
                flash("QR kodas nenuskaitytas!","danger")
                return redirect(request.url) 

        except Exception as Ex:
            flash("Prietaiso nepavyko užregistruoti!","danger")
            Logger.log_error(Ex.args)
            return redirect(request.url)
        
    else:
        flash("Failas nėra tinkamo formato!","danger")

@main.route('/user-devices')
@login_required
def user_devices():
    return render_template('devices/user_devices_list.html')

@main.route('/get-devices-list', methods=['POST','GET'])
@login_required
def get_devices_list():
    return user_device.get_user_devices()

@main.route('/get-device-data/<id>', methods=['POST','GET'])
@login_required
def get_device_data(id):
    return user_device.get_device_data(id)

@main.route('/get-device-configs/<id>', methods=['POST','GET'])
@login_required
def get_device_configs(id):
    return user_device.get_device_configurations(id)  

@main.route('/user-devices/device-configurations/<id>', methods=['POST','GET'])
@login_required
def device_configurations(id):
    device = user_device.get_device_view_model(id)
    return render_template('devices/device_configurations.html', device=device)

@main.route('/user-devices/device-configurations/edit/<device_id>', methods=['POST','GET'])
@main.route('/user-devices/device-configurations/edit/<device_id>/<config_uuid>', methods=['POST','GET'])
@login_required
def edit_config(device_id,config_uuid=None):
    if (config_uuid):
        device = user_device.get_device_view_model(device_id)
        config = user_device.get_device_config(device_id,config_uuid)
        form = user_device.get_device_config_form(device)

        if form.validate_on_submit():
            if user_device.validate_config_form(form):
                return render_template('devices/edit_device_config.html', form=form, device=device, config=config)

            user_device.save_device_config(form, device, config_uuid)        
        else:        
            form = user_device.get_config_form(device,config,form)
            
        return render_template('devices/edit_device_config.html', form=form, device=device, config=config)
    else:
        device = user_device.get_device_view_model(device_id)
        form = user_device.get_device_config_form(device)
            
        if form.validate_on_submit():
            if user_device.validate_config_form(form):
                return render_template('devices/create_device_config.html', form=form, device=device)

            user_device.save_device_config(form, device, None)
            return redirect(url_for('main.device_configurations',id=device_id))
        
        return render_template('devices/create_device_config.html', form=form, device=device)
 

@main.route('/user-devices/device-control-panel/<id>', methods=['POST','GET'])
@login_required
def device_control_panel(id):
    device = user_device.get_device_view_model(id)    
    lastData = user_device.get_last_data(id)

    return render_template('devices/user_device_control_panel.html', device=device, data=lastData)

@main.route('/user-devices/device-history/<id>', methods=['POST','GET'])
@login_required
def device_history(id):
    device = user_device.get_device_view_model(id)
    return render_template('devices/user_device_history.html', device=device)

@main.route('/device-action', methods=['POST'])
@login_required
def device_action():  
    if request.method == "POST":
          device_id=request.form['device_id']
          command=request.form['command']
    return user_device.execute_device_action(device_id,command)

@main.route('/configure-device', methods=['POST'])
@login_required
def configure_device():  
    if request.method == "POST":
          device_id=request.form['device_id']
          data_type=request.form['type']
          data=request.form['data']
    return user_device.send_device_configuration(device_id,data_type,data)

@main.route('/activate-device-configuration', methods=['POST'])
@login_required
def activate_device_configuration():
    if request.method == "POST":
          device_id=request.form['id']
          config_uuid=request.form['uuid']
    device = user_device.get_user_device(device_id)       
    return user_device.activate_device_configuration(device, config_uuid)

@main.route('/delete-device-config', methods=['POST'])
@login_required
def delete_device_config():
    if request.method == "POST":
        device_id=request.form['id']
        config_uuid=request.form['uuid']
    device = user_device.get_user_device(device_id)       
    return user_device.delete_device_config(device, config_uuid)
    