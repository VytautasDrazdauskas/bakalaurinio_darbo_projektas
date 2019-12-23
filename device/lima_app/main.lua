#!/usr/bin/lua

local MQTT = require "mqtt"
local socket = require "socket"
local lapp = require("pl.lapp")

function Is_openwrt()
        return(os.getenv("USER") == "root")
      end

if (not Is_openwrt()) then require("luarocks.require") end

function Main()
       Temp = ReadFileData("/root/test.txt","temp")
       
       print(Temp)
       return
end

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

function SendDataToServer(data)

end

Main()