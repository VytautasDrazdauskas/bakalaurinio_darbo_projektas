import os
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from app.forms import DeviceAdminForm
from app.controllers.admin_panel import get_profiles, get_system_devices, get_system_device, save_device_form
from werkzeug.utils import secure_filename
import pyqrcode
import io
import base64

admin = Blueprint('admin', __name__)

@admin.route('/admin-panel')
@login_required
def admin_panel():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    return render_template('admin/_profiles_list.html')

@admin.route('/admin-panel/profiles-list')
@login_required
def profiles_list():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    return render_template('admin/_profiles_list.html')

@admin.route('/admin-panel/get-system-profiles')
@login_required
def get_system_profiles():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')

    return get_profiles()

@admin.route('/admin-panel/get-system-devices')
@login_required
def get_devices_list():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')

    return get_system_devices()

@admin.route('/admin-panel/analytics')
@login_required
def analytics():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    return render_template('admin/_analytics.html')

@admin.route('/admin-panel/admin-system-devices')
@login_required
def admin_system_devices():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    return render_template('admin/_system_devices.html')

@admin.route('/admin-panel/admin-create-device', methods=('GET', 'POST'))
@login_required
def admin_create_device():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    form = DeviceAdminForm()
    if form.is_submitted():
        response = save_device_form(form=form)
        return redirect(url_for('admin.admin_system_devices'))
    
    return render_template('admin/_edit_device.html', form=form)

@admin.route('/admin-panel/admin-edit-device/<id>', methods=('GET', 'POST'))
@login_required
def admin_edit_device(id=None):
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    form = DeviceAdminForm()
    if form.is_submitted():
        response = save_device_form(form=form)
        return redirect(url_for('admin.admin_system_devices'))

    device = get_system_device(id=int(id))
    form.id.data = device.id
    form.mac.data = device.mac
    form.uuid.data = device.uuid
    form.user.data = device.user.email if device.user != None else "Nepriskirta"
    form.next_aes_key_change.data = device.aes_key_change_date

    #QR kodo sugeneravimas
    c = pyqrcode.create(device.uuid)
    s = io.BytesIO()
    c.png(s,scale=4)
    out = base64.b64encode(s.getvalue()).decode("ascii")
    return render_template('admin/_edit_device.html', form=form, qr_code=out)