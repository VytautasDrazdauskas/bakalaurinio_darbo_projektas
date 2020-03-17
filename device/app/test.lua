#!/usr/bin/lua
local binascii = require "libraries.binascii"
local aes = require "libraries.cryptography"
local bit = require "libraries.mqtt.bitwrap"
local json = require "libraries.json"

--duomenys
local inbound = '{"data": "589ed7ee99b26ed90183dc", "iv": [55, 210, 243, 217, 4, 54, 104, 13, 142, 93, 182, 78, 216, 16, 240, 93]}'
local key = aes.loadKey("/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/app/aeskey.key")
local aesKeyPath = "/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/app/aeskey.key"

local res = aes.decryptPayload(inbound, aes.loadKey(aesKeyPath))


local payload = {}
payload = json.decode(inbound)

local encrypted_data = aes.encrypt(key,"ACT ALL ON")

print(res)
print(encrypted_data)





