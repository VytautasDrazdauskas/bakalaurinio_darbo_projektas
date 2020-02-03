from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from app.helpers.enums import DeviceType

class NewDeviceForm(FlaskForm):
    deviceName = StringField('Prietaiso pavadinimas', validators=[DataRequired()])
    deviceType = SelectField('Prietaiso tipas', choices = DeviceType.choices(), coerce = DeviceType.coerce)

class ProfileForm(FlaskForm):
    userName = StringField('Naujas vartotojo vardas')
    email = EmailField('Naujas el. paštas')
    password = PasswordField('Dabartinis slaptažodis', validators=[DataRequired()])
    newPassword = PasswordField('Naujas slaptažodis')
    
class DeviceForm(FlaskForm):
    deviceName = StringField('Prietaiso pavadinimas', validators=[DataRequired()])
    
class DeviceConfigBaseForm(FlaskForm):
    configName = StringField('Pavadinimas', validators=[DataRequired()])
    isActive = BooleanField('Aktyvinta')
    monday = BooleanField('Pirmadienis')
    tuesday = BooleanField('Antradienis')
    wednesday = BooleanField('Trečiadienis')
    thursday = BooleanField('Ketvirtadienis')
    friday = BooleanField('Penktadienis')
    saturday = BooleanField('Šeštadienis')
    sunday = BooleanField('Sekmadienis')    
    startTime = TimeField('Pradžios laikas', validators=[DataRequired()])
    finishTime = TimeField('Pabaigos laikas', validators=[DataRequired()])