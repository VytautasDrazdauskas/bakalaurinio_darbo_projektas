from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.models import Users
from app import db
import mysql.connector
import app.load_config as app_config

def get_root_connection():    
    connection = mysql.connector.connect(
    host=app_config.db_ip,
    port=app_config.db_port,
    user=app_config.db_user,
    passwd=app_config.db_password
    )
    return connection

#sukuriam DB userį    
#create_user(mycursor, user_sys_name, password, db_name)
def create_db_user(user_name, password, db_name):
    connection = get_root_connection()
    cursor = connection.cursor()

    try:
        sqlCreateUser = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(user_name, password)
        cursor.execute(sqlCreateUser)

        grantPrivelegesCmd = "grant all privileges on " + db_name +".* to " + user_name + "@localhost;"
        cursor.execute(grantPrivelegesCmd)
    except Exception as Ex:
        raise

def create_new_user_db(user, password):
    connection = get_root_connection()
    cursor = connection.cursor()

    db_name = user.uuid
    db_name = db_name.replace('-', '') #DB pavadinimas
    user_sys_name = user.name.replace(' ','') + str(user.id) #DB userio vardas

    #sukuriama duomenų bazės schema. Sukuriama, jei prisijungta pirma karta.
    try:     
        command = "CREATE DATABASE IF NOT EXISTS db_" + db_name + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        cursor.execute(command)
        cursor.close()
        connection.close()
    #jei duomenu baze jau egzistuoja:
    except Exception as Ex: 
        return 0

    #toliau kuriam schema.