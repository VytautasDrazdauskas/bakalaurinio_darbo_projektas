import os
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app import ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/newDevice')
@login_required
def newDevice():
    return render_template('newDevice.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/newDevice', methods=['POST'])
@login_required
def newDevice_post():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Neįkeltas failas','danger')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('Neįkeltas failas','danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash('Prietaisas sėkmingai užregistruotas!','success')
               
    return render_template('newDevice.html')

@main.route('/devicesList')
@login_required
def devicesList():
    return render_template('devicesList.html')