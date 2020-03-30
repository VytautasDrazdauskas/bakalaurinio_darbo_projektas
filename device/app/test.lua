#!/usr/bin/lua
local binascii = require "libraries.binascii"
local aes = require "libraries.cryptography"
local bit = require "libraries.mqtt.bitwrap"
local json = require "libraries.json"
local common = require "libraries.common"

--duomenys
local inbound = '{"command": "ACT ALL ON", "response_id": "491ab101-9bf9-460d-a1c5-2366ba277206"};;▒▒Mr▒▒ы▒'
-- local key = aes.loadKey("/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/certs/aeskey.key")
-- local aesKeyPath = "/mnt/d/VGTU_bakalauras/IV_kursas/bakalaurinis_darbas/Repository/device/certs/aeskey.key"
-- local keyKey = "657726a5fcb4363622bd6b6aadb83497b456922ff384fa24f2b9159a94abbce4"

--local res = aes.decryptPayload(inbound, keyKey)

--local response_id = json.decode(inbound).response_id
--print(response_id)

--local test = string.match(inbound, "(.+)%;;(.+)")
local test = common.split(inbound,";;")[1]
print(test)


-- local payload = {}
-- payload = json.decode(inbound)

-- local encrypted_data = aes.encrypt(key,"ACT ALL ON")

--print(res)
-- print(encrypted_data)





