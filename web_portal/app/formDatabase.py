from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import Users
from . import db
import mysql.connector

def createUser(cursor, userName, password,
               querynum=0, 
               updatenum=0, 
               connection_num=0):
    try:
        sqlCreateUser = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(userName, password);
        cursor.execute(sqlCreateUser);
    except Exception as Ex:
        print("Error creating MySQL User: %s"%(Ex));

def createNewDatabase(user, password):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="MANOkompas123"
    )
    mycursor = mydb.cursor()
    
    db_name = user.uuid
    db_name = db_name.replace('-', '')
    user_sys_name = user.name.replace(' ','') + str(user.id)

    #sukuriam DB userį    
    createUser(mycursor, user_sys_name,password)

    #sukuriama duomenų bazės schema
    command = "CREATE DATABASE " + db_name + ";"
    mycursor.execute(command)

    #suteikiam useriui teises naudotis asmenine DB
    command = "grant all privileges on " + db_name +".* to " + user_sys_name + "@localhost;"
    mycursor.execute(command)

    #sukuriam lentas
    command = "CREATE TABLE "+db_name+".test (id INT NOT NULL auto_increment PRIMARY KEY, name nvarchar(100) unique NOT NULL)"
    mycursor.execute(command)

    return 'success'