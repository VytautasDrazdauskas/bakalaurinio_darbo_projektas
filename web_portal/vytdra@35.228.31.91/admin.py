import os
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from app.forms import DeviceForm
from app.controllers.admin_panel import get_profiles, get_system_devices, save_device_form
from werkzeug.utils import secure_filename


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
def get_system_devices():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')

    return get_all_devices()

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

@admin.route('/admin-panel/admin-edit-device', methods=('GET', 'POST'))
@login_required
def admin_edit_device():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('error_page.html')

    form = DeviceForm()
    if form.is_submitted():
        response = save_device_form(form)
        return redirect('/admin/_systemDevices')
    return render_template('admin/_edit_device.html', form=form)