local serial = require "libraries.rs232_controller"
local socket = require "libraries.socket"

local serialPort = "/dev/ttyUSB0"
local serialClient, err = serial.Serial_connect(serialPort)
if err == -1 then
                return nil
else        
        serial.Serial_setup(serialClient) --9600,8,none,1,off
end

-- local i = 0
-- while true do
-- 	print(i)
-- 	i = i + 1
	serial.Serial_write(serialClient,"ON")
-- 	socket.sleep(1)
-- 	serial.Serial_write(serialClient,"OFF")
-- 	socket.sleep(1)
-- end