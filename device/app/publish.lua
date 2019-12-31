#!/usr/bin/lua
local socket = require "include.socket"
local http = require "include.http"
local MQTT = require "include.mqtt_library"
local json = require "include.json"

local deviceMAC = "unknown"
local userUID = "useruid"
local systemName = "system"

local brokerIP = "192.168.137.53"

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

function GetPublicIP()
        --is ipinfo.io gaunam json objekta
        local resp,code = http.request("http://ipinfo.io/json")
        
        --jei uzklausos kodas yra ne 200 (success)
        if code ~= 200 
        then 
                return nil 
        end

        --dekoduojam atsakymo json
        local data = json.decode(resp)
        if data ~= nil
        then                
                if data.ip ~= nil
                then
                        return data.ip --Realus ip adresas
                else
                        return nil
                end 
        else
                return nil
        end  
                
end

--MQTT callbackas
Running = false  
function Callback(topic, message)
        print("Received: " .. topic .. ": " .. message)
        if (message == "quit") then Running = false end
end

--MQTT publish
function PublishData(mqtt_client,topic,message,deviceName)
        --true, jei norim loguose matyti debug info
        MQTT.Utility.set_debug(false)
        mqtt_client:connect(deviceName)
        
        mqtt_client:handler()
        mqtt_client:publish(topic,message)
        socket.sleep(5.0)  -- seconds        
end

function Main()
        --sukuriamas sujungimas su MQTT brokeriu
        local mqtt_client = MQTT.client.create(brokerIP, nil, Callback)
        print("Connection with MQTT broker " .. brokerIP .. " established!")

        --kol nenutraukiamas rysys, tol sukasi
        Running = true
        IsSignalLost = false
        while (Running) do
                --duomenu nuskaitymas, etc                
                local innerTemp = 252.25  --test
                local heater_1_state = true
                local heater_2_state = false
                local heater_3_state = false
                local fanState = true
                local outerTemp = ReadFileData("test.txt","temp")

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

                local Message = json.encode(dataTable)
                --tema user/system/prietaisoMAC/
                Topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata"
                
                --patikrinam ar yra rysys su brokeriu
                
                if (CheckPing(brokerIP) == true) then   
                        --nusiunciame duomenis    
                        --pcall - protected call. Jei ivyksta klaida, nenulauzia programos (vietoje try catch bloko)                     
                        if (pcall(PublishData,mqtt_client,Topic,Message,"MQTT publisher " .. deviceMAC)) then
                        else
                                print("Trying to restore connection...")                
                                while (CheckPing(brokerIP) == false) do
                                        socket.sleep(5.0)
                                end
                                print("Connection with " .. brokerIP .. " restored!")
                                Main()
                        end        
                else
                        --jei nera rysio, nutraukiam perdavima
                        print("Conncetion lost with " .. brokerIP)
                        Running = false
                        IsSignalLost = true
                end 
        end
       

        mqtt_client:destroy()

        if (IsSignalLost == true)then
                print("Trying to restore connection...")

                while (CheckPing(brokerIP) == false) do
                        socket.sleep(5.0)
                end
                print("Connection with " .. brokerIP .. " restored!")
                Main()
        end
        return
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

--failu nuskaitymas
function ReadFileData(pathToFile, type)
        local file, err = io.open(pathToFile,"r")
        if err then print("File is empty"); return; end
        local data = ""
        while true do
                local line = file:read()                
                if line == nil then break else data = data .. line end
        end        
        file:close()

        local result = nil

        --Isparsinam is failo temperatura
        if type == "temp"
        then
                local temperature = string.match(data, "t=(.*)")
                result = temperature / 1000
        end

        return result
end

--startuojam
Main()