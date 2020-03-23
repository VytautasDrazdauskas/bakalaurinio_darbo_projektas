#!/usr/bin/python3.6
from service.helpers.cryptography import AESCipher
import binascii
import json
from service.aes_scheduler_service import AesScheduler

scheduler_service = AesScheduler()
scheduler_service.start()  

# aes = AESCipher()

# #key = aes.generate_key("slaptas laptazodis")
# #print(len(key))

# #aes.save_key(key, "C493000EFEA1")
# payload = '{"data":"B64A2C06F4FB31A0E11209F3EFC702EC445F11372D240ACD0390B6E4685447D0527BDBA0A6E8666D7B08C96E412AA0E89E06209C26F647664C7D3F7E7A22A72AD3A80EBF064E54E5EA26F178D9837751FA59043EF3415296E87BA6FB98B5AAE2","iv":[237,225,245,67,226,76,194,231,193,123,87,104,126,100,183,22]}'
# #key = aes.load_key("key1")
# #message = "ACT ALL ON;"

# #enc = aes.encrypt(message,key)

# #data = json.dumps(enc)

# loaded_key = aes.load_key("C493000EFEA1")
# enc2 = json.loads(payload)

# if('iv' in enc2):
#     print('t')

# dec = aes.decrypt(enc2,loaded_key)

# #dec1 = aes.decrypt(enc,loaded_key)

# print(dec)
# #print(dec1)