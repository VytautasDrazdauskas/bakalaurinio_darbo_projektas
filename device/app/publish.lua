#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local json = require "libraries.json"
local fileParser = require "libraries.file_parser"

local deviceMAC = "unknown"  --useruid/system/C493000EFE35/control
local userUID = "useruid"
local systemName = "system"
IsSignalLost = false

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

--tema user/system/prietaisoMAC/
local topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata"
--local controlTopic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/control"
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
                        content_type = "text/plain",
                },
                user_properties = {
                        hello = "world",
                },
        })
        socket.sleep(5.0)  -- seconds      
end

function Main()
        --sukuriamas sujungimas su MQTT brokeriu        
        local client = mqtt.client{
                uri = brokerIP,
                clean = false,
                username = deviceMAC .. "_publisher",
                version = mqtt.v50,
        }
        
        print("Program starting...")        
               
        while true do
                local result = client:start_connecting()

                if result == false then
                        print("Connection to broker " .. brokerIP .. " failed:")
                        return
                else
                        print("Connection with MQTT broker " .. brokerIP .. " established!") -- successful connection
                        IsSignalLost = false
                end  

                local response = Loop(client,2)

                --dingo signalas
                if(response == -2)then
                        client:close_connection()  
                        RestoreConnection(brokerIP)
                else --kitos priezastys                        
                        client:close_connection()                         
                        break
                end
        end
        print("Program stopped")  

        return
end

function Loop(client,sleepDelay)

        Running = true
        while (Running) do  
                local Message = ReadData()

                if (CheckPing(brokerIP) == true) then 
                        client:publish{
                                topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata",
                                payload = Message,
                                qos = 0,
                                properties = {
                                        payload_format_indicator = 1,
                                        content_type = "json",
                                },
                        }
                        socket.sleep(sleepDelay)
                else
                        print("Signal is lost.")
                        IsSignalLost = true
                        return -2
                end
        end 
end

function RestoreConnection(ip)
        
        print("Trying to restore connection...")                
        while (CheckPing(ip) == false) do
                socket.sleep(5.0)
        end

        IsSignalLost = false
        print("Connection with " .. ip .. " restored!")
        return true
end

function CheckPing(IP)
        local command = "ping -c 1 -W 1 " .. IP
        local handler = io.popen(command)
        local response = handler:read("*a")
        handler:close()
        
        if (string.match(response, " 0%% packet loss") and 
        not string.match(response, "Network unreachable")) 
        then return true else return false end
end

function ReadData()
        --duomenu nuskaitymas, etc                
        local innerTemp = 252.25  --test
        local heater_1_state = true
        local heater_2_state = false
        local heater_3_state = false
        local fanState = true
        local outerTemp = fileParser.ReadFileData("test.txt","temp")

        --formuojama duomenu lenta, kuri veliau parsinama i 
        local dataTable = { 
                deviceMAC=deviceMAC,
                innerTemp=innerTemp,
                outerTemp=outerTemp,
                heaterStates={
                        heater_1=heater_1_state,
                        heater_2=heater_2_state,
                        heater_3=heater_3_state
                        },
                fanState = fanState
                }
        

        return json.encode(dataTable)
end

--startuojam
Main()