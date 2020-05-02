#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local json = require "libraries.json"
local fileParser = require "libraries.file_parser"
local serial = require "libraries.rs232_controller"
local socket = require "libraries.socket"
local common = require "libraries.common"
local aes = require "libraries.cryptography"

function Path()
        local str = debug.getinfo(2, "S").source:sub(2)
        return str:match("(.*/)")
end

PATH = Path();
local configPath = PATH .. "../config.conf"

local deviceMAC = "unknown"  --useruid/system/C493000EFE02/control
local userUID = fileParser.ReadFileData(configPath,"useruuid")
local systemName = fileParser.ReadFileData(configPath,"systemname")
local cafilePath = fileParser.ReadFileData(configPath,"cafile")
local clientCertPath = fileParser.ReadFileData(configPath,"clientCert")
local clientKeyPath = fileParser.ReadFileData(configPath,"clientKey")
local aesKeyPath = fileParser.ReadFileData(configPath,"aesKey")

local emptyUserUID = "00000000-0000-0000-0000-000000000000"

--sukuriamas rysys su Arduino Nano per UART sasaja
local serialClient = serial.Serial_create_client("/dev/ttyUSB0")

function Is_openwrt()
        return(os.getenv("USER") == "root" or os.getenv("USER") == nil)
end

if (Is_openwrt()) then 
        local handle = io.popen("ifconfig -a | grep mesh0 | head -1")
        local result = handle:read("*a")
        deviceMAC = string.match(result, "HWaddr(.*)")
        deviceMAC = deviceMAC:gsub("%:", "") --pasalinam dvitaskius
        deviceMAC = deviceMAC:gsub("%s+", "") --pasalinam tarpus
        handle:close()
end

--tema user/system/prietaisoMAC/control
--Subscribe topics
local device_root_topic = userUID .. "/" .. systemName .. "/" .. deviceMAC
local topic = device_root_topic .. "/control"
local config_topic = device_root_topic .. "/setconfig"

--Publish topics
local pub_topic = device_root_topic .. "/jsondata"
local control_response_topic = device_root_topic .. "/control/response/"
local setconfig_response_topic = device_root_topic .. "/setconfig/response/"

--parametrai nuskaitomi is konfiguracinio failo
local brokerIP = fileParser.ReadFileData(configPath,"ip")

function Main()
        --sukuriamas sujungimas su MQTT brokeriu        
        local parameters = {
                mode = "client",
                protocol = "tlsv1_2",
                cafile = cafilePath,
                certificate=clientCertPath,
                key=clientKeyPath,
                verify = {"peer", "fail_if_no_peer_cert"},
                options = "all",
             }
        
        local client = mqtt.client{
                uri = brokerIP,
                clean = false,
                version = mqtt.v311,
                secure = parameters
        }
      
        --kol nenutraukiamas rysys, tol sukasi
        client:on{
                connect = function(connack)   
                        if connack.rc ~= 0 then
                                print("Subscribe connection to broker " .. brokerIP .. " failed:", connack:reason_string(), connack)
                                return
                        else
                                print("Subscribe connection with MQTT broker " .. brokerIP .. " established! Topic: " .. topic, connack) -- successful connection
                        end    
                        
                        --uzprenumeruojama tema valdymui. QoS 2 reiskia, jog zinute privalo buti pristatyta lygiai viena karta.
                        client:subscribe{ topic=topic, qos=2, callback=function(suback)end}
                        client:subscribe{ topic=config_topic, qos=2, callback=function(suback)end}
                end,

                message = function(msg)
                    --nusiunciam brokeriui ACK
                        assert(client:acknowledge(msg)) 
                        local json_payload = aes.decryptPayload(msg.payload, aes.loadKey(aesKeyPath))
                        print(json_payload)
                        local data = json.decode(json_payload)
                        local aesKey = aes.loadKey(aesKeyPath)
                        local command = data.command
                        local response_id = data.response_id

                        --patikrinam, ar paketas nera dubliuotas
                        if (response_id ~= nil and fileParser.IsDublicate(response_id)) then
                                return -1
                        end
                        
                        --prie response temos pridedam sesijos id
                        if (response_id ~= nil) then
                                control_response_id_topic = control_response_topic .. response_id
                                setconfig_response_id_topic = setconfig_response_topic .. response_id
                        end

                        if (command == nil) then 
                                print("Duomenys neiššifruoti")
                                return -1
                        end

                        print("Komanda: " .. command)
                        local topic_type = string.match(msg.topic, ".+(/.+)$")                        
                        local sendResponse = false

                        if (userUID ~= emptyUserUID and topic_type == "/control") then
                                --Arduino valdymas per UART
                                if (command == "reboot") then 
                                        Running = false
                                        --viską išjungiam
                                        serial.Serial_write(serialClient,"ACT1 OFF")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT2 OFF")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT3 OFF")
                                        --Responsas
                                        if(response_id ~= nil) then
                                                common.PublishData(client,control_response_id_topic,common.ResponseJson(true,"Command successfully executed!"), aesKey)
                                        end
                                        -- tik po to perkraunam
                                        io.popen("reboot")
                                elseif (command == "ACT ALL ON") then
                                        serial.Serial_write(serialClient,"ACT1 ON")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT2 ON")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT3 ON")
                                        sendResponse = true
                                elseif (command == "ACT ALL OFF") then
                                        serial.Serial_write(serialClient,"ACT1 OFF")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT2 OFF")
                                        socket.sleep(1)
                                        serial.Serial_write(serialClient,"ACT3 OFF")
                                        sendResponse = true
                                else 
                                        serial.Serial_write(serialClient,command)
                                        sendResponse = true
                                end
                                
                                if (sendResponse == true and response_id ~= nil) then
                                        local message = common.ReadData(deviceMAC)
                                        common.PublishData(client,control_response_id_topic,common.ResponseJson(true,"Command successfully executed!"), aesKey)
                                        common.PublishData(client,pub_topic,message, aesKey)
                                end
                        elseif (topic_type == "/setconfig") then
                                local config_type = string.match(command, "(.+)%=(.+)")
                                local config_value = string.match(command, "=(.*)")
                                local res = nil

                                print(config_type)

                                if (config_type == "useruuid") then 
                                        res = fileParser.UpdateFileData(configPath,config_type,config_value)
                                elseif (config_type == "systemname") then 
                                        res = fileParser.UpdateFileData(configPath,config_type,config_value)
                                elseif (config_type == "delay") then
                                        res = fileParser.UpdateFileData(configPath,config_type,config_value)
                                elseif (config_type == "newaeskey") then --atnaujinamas aes raktas. Pirma issiunciam patvirtinima, po to keiciam ir perkraunam
                                        print("Keiciamas AES raktas...")
                                        res = fileParser.OverwriteFileData(aesKeyPath,config_value)

                                        --isvalomas paketu identifikatoriu failas
                                        fileParser.ResetDublicateFile()

                                        if res == 0 and response_id ~= nil then
                                                common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(true,"AES key has been changed!"), aesKey)    
                                        else
                                                common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(false,"AES key has not been changed!"), aesKey) 
                                        end
                                        return
                                end

                                if (res == 0 and response_id ~= nil) then
                                        common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(true,config_type .. " changed to " .. config_value .. ". Restarting."), aesKey)
                                        io.popen("./run_daemon.sh restart")
                                elseif (res == 1) then
                                        common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(false,config_type .. " was not changed to " .. config_value,"Same value."), aesKey)
                                elseif (res == -1) then
                                        common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(false,config_type .. " was not changed to " .. config_value,"File does not exist."), aesKey)
                                else
                                        common.PublishData(client,setconfig_response_id_topic,common.ResponseJson(false,config_type .. " was not changed to " .. config_value,"Unknown reason."), aesKey)
                                end                        
                        end
                        
                end
        }

        print("Starting program")
        while true do
        mqtt.run_ioloop(client)
        end
        print("Program stopped")
           
        return
end

--startuojam
Main()