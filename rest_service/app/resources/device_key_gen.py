from flask_restful import Resource
from flask import request
import json
import app.loadConfig as config
from app.json2obj import JsonParse
from app.cryptography import AESCipher
import time
import os
from uuid import uuid4
import subprocess


class DeviceKeyGen(Resource):    
    def put(self):
        try:
            data = JsonParse(request.get_json(force=True))

            if not data:
                raise Exception ("No data provided.")

            #tikrinam, ar jau nera sukurto sertifikato
            does_exist = os.path.isdir(config.device_certs.directory + data.mac)
            if (does_exist):
                raise Exception("Certificates already exist.")

            path_to_bash = config.device_certs.directory + "gen_client_certs.sh"
            #TLS sertifikato sukūrimas
            result = subprocess.check_call([path_to_bash,"-m",data.mac,"-p",config.broker.caPassword, "-d", config.device_certs.directory])

            if (result != 0):
                raise Exception("Certificates not generated.")

            #AES rakto sukūrimas
            aes = AESCipher()
            key = aes.generate_key(str(uuid4()))
            aes.save_key(key,data.mac)            
            
            return {"success": True, "reason": "Success"}, 200

        except Exception as ex:
            return {"success": False, "reason": ex.args}, 400