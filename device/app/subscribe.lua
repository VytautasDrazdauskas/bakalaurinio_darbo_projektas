#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local json = require "libraries.json"
local fileParser = require "libraries.file_parser"

local deviceMAC = "unknown"  --useruid/system/C493000EFE35/control
local userUID = "useruid"
local systemName = "system"

function Path()
        local str = debug.getinfo(2, "S").source:sub(2)
        return str:match("(.*/)")
     end

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
local topic = userUID .. "/" .. systemName .. "/" .. "+" .. "/control"
PATH = Path();
--parametrai nuskaitomi is konfiguracinio failo
local brokerIP = fileParser.ReadFileData(PATH .. "/broker.conf","ip")

--MQTT publish
function PublishData(client,topic,message)
        assert(client:publish{
                topic = topic,
                payload = message,
                qos = 1,
                properties = {
                        payload_format_indicator = 1,
                        content_type = "json",
                },
        })
        socket.sleep(5.0)  -- seconds      
end

function CreateClientInstance(ip)
        local client = mqtt.client{
                uri = ip,
                clean = true,
                version = mqtt.v50,
        }
        return client
end

function Main()
        --sukuriamas sujungimas su MQTT brokeriu        
        local client = CreateClientInstance(brokerIP)
      
        --kol nenutraukiamas rysys, tol sukasi
        client:on{
                connect = function(connack)   
                        if connack.rc ~= 0 then
                                print("Connection to broker " .. brokerIP .. " failed:", connack:reason_string(), connack)
                                return
                        else
                                print("Connection with MQTT broker " .. brokerIP .. " established!", connack) -- successful connection
                        end    
                        
                        client:subscribe{ topic=topic, qos=1, callback=function(suback)end}
                end,

                message = function(msg)
                    assert(client:acknowledge(msg))        
                    print("received:", msg)
                    
                    if (msg.payload == "reboot") then 
                            Running = false
                            io.popen("reboot")
                    end
                end,

                error = function(err)
                        print("MQTT client error:", err)
                end,
        }

        print("Starting program")
        mqtt.run_ioloop(client)
        print("Program stopped")
           
        return
end

function RestoreConnection(ip,client)
        
        print("Trying to restore connection...")                
        while (CheckPing(ip) == false) do
                socket.sleep(5.0)
        end

        client:disconnect()
        print("Connection with " .. ip .. " restored!")
        Main()
end

function CheckPing(IP)
        if (Is_openwrt() == false) 
        then return true end

        local command = "ping -c 1 -W 1 " .. IP
        local handler = io.popen(command)
        local response = handler:read("*a")
        handler:close()
        
        if (string.match(response, " 0%% packet loss") and 
        not string.match(response, "Network unreachable")) 
        then return true else return false end
end

--startuojam
Main()