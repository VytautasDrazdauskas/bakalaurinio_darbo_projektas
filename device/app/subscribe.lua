#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local json = require "libraries.json"
local fileParser = require "libraries.file_parser"
local serial = require "libraries.rs232_controller"

function Path()
        local str = debug.getinfo(2, "S").source:sub(2)
        return str:match("(.*/)")
end

PATH = Path();

local deviceMAC = "unknown"  --useruid/system/C493000EFE02/control
local userUID = fileParser.ReadFileData(PATH .. "broker.conf","useruuid")
local systemName = fileParser.ReadFileData(PATH .. "broker.conf","systemname")

local serialClient = serial.Serial_create_client("/dev/ttyUSB0")

function Is_openwrt()
        return(os.getenv("USER") == "root" or os.getenv("USER") == nil)
end

if (Is_openwrt()) then 
        local handle = io.popen("ifconfig -a | grep wlan0 | head -1")
        local result = handle:read("*a")
        deviceMAC = string.match(result, "HWaddr(.*)")
        deviceMAC = deviceMAC:gsub("%:", "") --pasalinam dvitaskius
        deviceMAC = deviceMAC:gsub("%s+", "") --pasalinam tarpus
        handle:close()
end

--tema user/system/prietaisoMAC/control
local topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/control"

--parametrai nuskaitomi is konfiguracinio failo
local brokerIP = fileParser.ReadFileData(PATH .. "broker.conf","ip")

function Main()
        --sukuriamas sujungimas su MQTT brokeriu        
        local client = mqtt.client{
                uri = brokerIP,
                clean = false,
                username = deviceMAC .. "_subscriber",
                version = mqtt.v50,
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
                        
                        client:subscribe{ topic=topic, qos=2, callback=function(suback)end}
                end,

                message = function(msg)
                    assert(client:acknowledge(msg))        
                    --print("received:", msg)
                    
                    if (msg.payload == "reboot") then 
                        Running = false
                        io.popen("reboot")
                    elseif (msg.payload == "LED ON") then
                        serial.Serial_write(serialClient,"ON")
                    elseif (msg.payload == "LED OFF") then
                        serial.Serial_write(serialClient,"OFF")
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