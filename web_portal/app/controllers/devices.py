from app.helpers.sessionMaker import create_table, create_user_session, table_exists
from app.models import Test, UserDevices
from app.helpers.enums import DeviceState
from _datetime import datetime
from flask import flash

def add_new_device(code):
    session = create_user_session()
    try:   
        #sukuriam prietaisu lenta, jei tokios nera
        if not table_exists("user_devices"):                 
            UserDevices.__table__.create(session.bind)
                
        #patikrinam, ar toks prietaisas egzistuoja MainDB
        device = session.query(UserDevices).filter_by(uuid=code).first()
        #pridedam prietaisa i userio DB
        if not device:
            new_device = UserDevices(
                device_name="Prietaisas",
                uuid=code,
                status=DeviceState.registered.value,
                device_type=1
                )

            session.add(new_device)
            session.commit()
        else:
            flash("Toks prietaisas jau pridėtas!","danger")
            session.rollback()

    except Exception as Ex:
        raise
    
