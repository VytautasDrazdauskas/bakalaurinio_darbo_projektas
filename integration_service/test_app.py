#!/usr/bin/python3.6
from service.helpers.cryptography import AESCipher
import binascii
import json
import os
# from service.aes_scheduler_service import AesScheduler

# scheduler_service = AesScheduler()
# scheduler_service.start()  

aes = AESCipher()

# #key = aes.generate_key("slaptas laptazodis")
# #print(len(key))

# #aes.save_key(key, "C493000EFEA1")
payload = '{"data":"EA8CF363C33F552E8DEC77A0CDB4FE101C5C280F6DE77D72B085A9FD82036BC1FB2AD5BBC213CF568BA44B2953F9C3D4D3087DF3CBC7D5DC924CCA8886421BB843D870B03E1171C86AD32934BF5DBDD2632BE3B08251B7C71C83C6BB0E60F1AB","iv":[1,85,106,86,211,95,94,51,191,154,5,206,75,210,87,128]};;asfasfasf'
#key = aes.load_key("key1")
# #message = "ACT ALL ON;"

# #enc = aes.encrypt(message,key)

# #data = json.dumps(enc)

# loaded_key = aes.load_key("C493000EFEA1")
# enc2 = json.loads(payload)

# if('iv' in enc2):
#     print('t')

# dec = aes.decrypt(enc2,loaded_key)

# #dec1 = aes.decrypt(enc,loaded_key)

dec = payload.split(';;')[0]

print(dec)
import subprocess

res = subprocess.check_call(["ls","-al"])
print(res)

isDir = os.path.isdir("./tmp")

print(isDir)