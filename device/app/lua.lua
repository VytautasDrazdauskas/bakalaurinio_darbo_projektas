rs232 = require("luars232")
socket = require "libraries.socket"

-- Linux
port_name = "/dev/ttyUSB0"

local out = io.stderr

-- open port
local e, p = rs232.open(port_name)
if e ~= rs232.RS232_ERR_NOERROR then
        -- handle error
        out:write(string.format("can't open serial port '%s', error: '%s'\n",
                        port_name, rs232.error_tostring(e)))
        return
end

-- set port settings
assert(p:set_baud_rate(rs232.RS232_BAUD_9600) == rs232.RS232_ERR_NOERROR)
assert(p:set_data_bits(rs232.RS232_DATA_8) == rs232.RS232_ERR_NOERROR)
assert(p:set_parity(rs232.RS232_PARITY_NONE) == rs232.RS232_ERR_NOERROR)
assert(p:set_stop_bits(rs232.RS232_STOP_1) == rs232.RS232_ERR_NOERROR)
assert(p:set_flow_control(rs232.RS232_FLOW_OFF)  == rs232.RS232_ERR_NOERROR)

out:write(string.format("OK, port open with values '%s'\n", tostring(p)))

-- read with timeout
local read_len = 20 -- read one byte
local timeout = 100 -- in miliseconds
local err, data_read, size

while data_read == nil do
err, data_read, size = p:read(read_len, timeout)
assert(e == rs232.RS232_ERR_NOERROR)
end

print(data_read)

-- write without timeout

-- write with timeout 100 msec
local i = 0
while true do
	print(i)
	i = i + 1
    err, len_written = p:write("ON\n", timeout)
    socket.sleep(1)
    err, len_written = p:write("OFF\n", timeout)
    socket.sleep(1)
end

-- close
assert(p:close() == rs232.RS232_ERR_NOERROR)
