#!/usr/bin/lua
local binascii = require "libraries.binascii"
local aes = require "libraries.cryptography"
local bit = require "libraries.mqtt.bitwrap"
local json = require "libraries.json"

--duomenys
local inbound = '{"data": "8f4b683256f77eae608c1eea", "iv": [233, 37, 158, 212, 36, 168, 149, 230, 129, 196, 44, 189, 211, 189, 133, 184],"response_id": "as1f23sa1f3a1sf32as1f23asf13as2f"}'
local key = aes.loadKey("/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/certs/aeskey.key")
local aesKeyPath = "/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/certs/aeskey.key"
local keyKey = "657726a5fcb4363622bd6b6aadb83497b456922ff384fa24f2b9159a94abbce4"

local res = aes.decryptPayload(inbound, keyKey)

local response_id = json.decode(inbound).response_id
print(response_id)


-- local payload = {}
-- payload = json.decode(inbound)

-- local encrypted_data = aes.encrypt(key,"ACT ALL ON")

print(res)
-- print(encrypted_data)





