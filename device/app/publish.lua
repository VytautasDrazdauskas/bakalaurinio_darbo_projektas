#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"
local json = require "libraries.json"
local fileParser = require "libraries.file_parser"
local serialController = require "libraries.rs232_controller"

function Path()
        local str = debug.getinfo(2, "S").source:sub(2)
        return str:match("(.*/)")
end
PATH = Path();

--pagrindiniai parametrai
local deviceMAC = "unknown"  --useruid/system/C493000EFE35/control

--nuskaitom is config failo
local userUID = fileParser.ReadFileData(PATH .. "broker.conf","useruuid")
local systemName = fileParser.ReadFileData(PATH .. "broker.conf","systemname")
IsSignalLost = false

function Is_openwrt()
        return(os.getenv("USER") == "root" or os.getenv("USER") == nil)
end

if (Is_openwrt()) then 
        local handle = io.popen("ifconfig -a | grep wlan0 | head -1")
        local result = handle:read("*a")
        --jei prietaisas yra su openwrt OS, tuomet irasom prietaiso MAC adresa
        deviceMAC = string.match(result, "HWaddr(.*)")
        deviceMAC = deviceMAC:gsub("%:", "") --pasalinam dvitaskius
        deviceMAC = deviceMAC:gsub("%s+", "") --pasalinam tarpus
        handle:close()
end

--tema user/system/prietaisoMAC/duomenuTipas
local topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata"

--parametrai nuskaitomi is konfiguracinio failo
local brokerIP = fileParser.ReadFileData(PATH .. "broker.conf","ip")

--MQTT publish
function PublishData(client,topic,message)
        client:publish{
                topic = topic,
                payload = message,
                qos = 0,
                properties = {
                        payload_format_indicator = 1,
                        content_type = "json",
                },
        }     
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
                        print("Connection with MQTT broker " .. brokerIP .. " established!") -- sekmingas prijungimas
                        IsSignalLost = false
                end  

                local response = Loop(client,2)

                --dingo signalas
                if(response == -2)then
                        client:close_connection()  
                        RestoreConnection("8.8.8.8") --bandom atstatyti rysi
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
                local message = ReadData()

                if (CheckPing("8.8.8.8") == true) then 
                        PublishData(client,topic,message)
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
        --duomenu nuskaitymas    
        
        local data = serialController.Get_serial_data("/dev/ttyUSB0")

        local temp = fileParser.GetData(data,"t")  --test
        local value = fileParser.GetData(data,"val")     
        local ledState = fileParser.GetData(data,"ledState")      

        --formuojama duomenu lenta, kuri veliau parsinama i 
        local dataTable = { 
                deviceMAC=deviceMAC,
                data={
                        temp=temp,
                        value=value,
                        ledState=ledState
                        }
                }
        
        return json.encode(dataTable)
end

--startuojam
Main()