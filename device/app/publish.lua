#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local fileParser = require "libraries.file_parser"
local common = require "libraries.common"
local socket = require "libraries.socket"
local aes = require "libraries.cryptography"

function Path()
        local str = debug.getinfo(2, "S").source:sub(2)
        return str:match("(.*/)")
end

PATH = Path();
IsSignalLost = false
IsProgramRunning = true

local configPath = PATH .. "../config.conf"

--pagrindiniai parametrai
local deviceMAC = "unknown"  --useruid/system/C493000EFE35/control

--nuskaitom is config failo
local userUID = fileParser.ReadFileData(configPath,"useruuid")
local systemName = fileParser.ReadFileData(configPath,"systemname")
local cafilePath = fileParser.ReadFileData(configPath,"cafile")
local clientCertPath = fileParser.ReadFileData(configPath,"clientCert")
local clientKeyPath = fileParser.ReadFileData(configPath,"clientKey")
local brokerIP = fileParser.ReadFileData(configPath,"ip")
local delay = tonumber(fileParser.ReadFileData(configPath,"delay"))
local aesKeyPath = fileParser.ReadFileData(configPath,"aesKey")

function Is_openwrt()
        return(os.getenv("USER") == "root" or os.getenv("USER") == nil)
end

if (Is_openwrt()) then 
        local handle = io.popen("ifconfig -a | grep mesh0 | head -1")
        local result = handle:read("*a")
        --jei prietaisas yra su openwrt OS, tuomet irasom prietaiso MAC adresa
        deviceMAC = string.match(result, "HWaddr(.*)")
        deviceMAC = deviceMAC:gsub("%:", "") --pasalinam dvitaskius
        deviceMAC = deviceMAC:gsub("%s+", "") --pasalinam tarpus
        handle:close()
end

--tema user/system/prietaisoMAC/duomenuTipas
local topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata"

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
        
        print("Program starting...")        
                       
        while IsProgramRunning do
                local result = client:start_connecting()

                if result == false then
                        print("Connection to broker " .. brokerIP .. " failed!")
                        IsProgramRunning = false
                else
                        print("Connection with MQTT broker " .. brokerIP .. " established!") -- sekmingas prijungimas
                        IsSignalLost = false
                end  

                local response = Loop(client,delay)

                --dingo signalas
                if(response == -1)then
                        client:close_connection()  
                        common.RestoreConnection("8.8.8.8") --bandom atstatyti rysi
                else --kitos priezastys                        
                        client:close_connection()                         
                        IsProgramRunning = false
                end
        end
        print("Program stopped")  

        return
end

function Loop(client,sleepDelay)

        local running = true
        while (running) do  
                local message = common.ReadData(deviceMAC)

                if (common.CheckPing("8.8.8.8") == true) then 
                        common.PublishData(client,topic,message,aes.loadKey(aesKeyPath))
                        common.sleep(sleepDelay)
                else
                        print("Signal is lost.")
                        IsSignalLost = true
                        return -1
                end
        end 
end
--startuojam
Main()