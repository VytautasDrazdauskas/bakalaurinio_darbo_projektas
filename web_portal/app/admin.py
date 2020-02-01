import os
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from app.forms import DeviceForm
from app.controllers.adminPanel import getProfiles, getAllDevices, saveDeviceForm
from werkzeug.utils import secure_filename


admin = Blueprint('admin', __name__)

@admin.route('/adminPanel')
@login_required
def adminPanel():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('errorPage.html')

    return render_template('admin/_profilesList.html')

@admin.route('/adminPanel/profilesList')
@login_required
def profilesList():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('errorPage.html')

    return render_template('admin/_profilesList.html')

@admin.route('/adminPanel/getProfilesList')
@login_required
def getProfilesList():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')

    return getProfiles()

@admin.route('/adminPanel/getDevicesList')
@login_required
def getDevicesList():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')

    return getAllDevices()

@admin.route('/adminPanel/analytics')
@login_required
def analytics():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('errorPage.html')

    return render_template('admin/_analytics.html')

@admin.route('/adminPanel/systemDevices')
@login_required
def systemDevices():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('errorPage.html')

    return render_template('admin/_systemDevices.html')

@admin.route('/adminPanel/editDevice', methods=('GET', 'POST'))
@login_required
def editDevice():
    if (not current_user.is_admin):
        flash('Neteisėtas naudotojo veiksmas!')
        return render_template('errorPage.html')

    form = DeviceForm()
    if form.is_submitted():
        response = saveDeviceForm(form)
        return redirect('/admin/_systemDevices')
    return render_template('admin/_editDevice.html', form=form)