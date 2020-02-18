from flask_wtf import FlaskForm
import wtforms as form
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from app.helpers.enums import DeviceType

class NewDeviceForm(FlaskForm):
    device_name = form.StringField('Prietaiso pavadinimas', validators=[DataRequired()])
    device_type = form.SelectField('Prietaiso tipas', choices = DeviceType.choices(), coerce = DeviceType.coerce)

class ProfileForm(FlaskForm):
    user_name = form.StringField('Naujas vardas')
    email = EmailField('Naujas el. paštas')
    password = form.PasswordField('Dabartinis slaptažodis', validators=[DataRequired()])
    new_password = form.PasswordField('Naujas slaptažodis')
    
class DeviceForm(FlaskForm):
    device_name = form.StringField('Prietaiso pavadinimas', validators=[DataRequired()])
    
class DeviceConfigBaseForm(FlaskForm):
    config_name = form.StringField('Pavadinimas', validators=[DataRequired()])
    is_active = form.BooleanField('Aktyvinta')
    monday = form.BooleanField('Pirmadienis')
    tuesday = form.BooleanField('Antradienis')
    wednesday = form.BooleanField('Trečiadienis')
    thursday = form.BooleanField('Ketvirtadienis')
    friday = form.BooleanField('Penktadienis')
    saturday = form.BooleanField('Šeštadienis')
    sunday = form.BooleanField('Sekmadienis')    
    start_time = form.TimeField('Pradžios laikas', validators=[DataRequired()])
    duration = form.TimeField('Trukmė', validators=[DataRequired()])