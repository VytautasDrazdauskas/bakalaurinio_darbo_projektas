local rs232_controller = {}
Serial = require ("luars232")
local socket = require "socket"

function file_exists(name)
    local f=io.open(name,"r")
    if f~=nil then io.close(f) return true else return false end
 end

--Sukuria klienta
function rs232_controller.Serial_connect(port_name)
    local e, c = nil
    while true do
        if (file_exists(port_name)) then
            e, c = Serial.open(port_name)
            if e ~= Serial.RS232_ERR_NOERROR then
                local err = Serial.error_tostring(e)
                print("Serial port opening error: " .. err)
                return nil,-1
            end
            break
        end
        print("neegzistuoja failas " .. port_name)
        socket.sleep(5)
    end
    return c,1
end

--RS232 setupas
function rs232_controller.Serial_setup(client)
    client:set_baud_rate(Serial.RS232_BAUD_9600)
    client:set_data_bits(Serial.RS232_DATA_8)
    client:set_parity(Serial.RS232_PARITY_NONE)
    client:set_stop_bits(Serial.RS232_STOP_1)
    client:set_flow_control(Serial.RS232_FLOW_OFF)
end


function rs232_controller.Serial_create_client(port_name)

    local serialClient, err = rs232_controller.Serial_connect(port_name)
    if err == -1 then
            return nil
    else        
            rs232_controller.Serial_setup(serialClient) --9600,8,none,1,off
    end

    return serialClient
end

function rs232_controller.Get_serial_data(port_name)

    local serialClient = rs232_controller.Serial_create_client(port_name)

	local data = nil

	--nuskaitom duomenis per serial porta
	while data == nil do
			data = rs232_controller.Serial_read(serialClient)
	end

    serialClient:close()
    
    return data
end

--nuskaitymas
function rs232_controller.Serial_read(Client)
    local read_len = 500
    local timeout = 500
    local err, data = nil

	--nuskaitom duomenis per serial porta
	while data == nil do
        err, data = Client:read(read_len, timeout)
    end

    return data
end

function rs232_controller.Serial_write(serialClient, message)    
    --palaukiam, kol bus inicijuotas rysys, ir tik tada siunciam
    local timeout = 100
    local read_len = 100
    local err, data_read = nil
    
    while data_read == nil do
        err, data_read = serialClient:read(read_len, timeout)
    end

    serialClient:write(message .. "\n", timeout)
    
end

return rs232_controller