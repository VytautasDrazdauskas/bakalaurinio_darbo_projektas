#!/usr/bin/lua
local mqtt = require "libraries.mqtt.init"

local deviceMAC = "unknown"
local userUID = "useruid"
local systemName = "system"

-- create mqtt client
local client = mqtt.client{
	uri = "192.168.137.53",
	clean = true,
	version = mqtt.v50,
}
print("created MQTT v5.0 client:", client)

client:on{
	connect = function(connack)
		if connack.rc ~= 0 then
			print("connection to broker failed:", connack:reason_string(), connack)
			return
		end
		print("connected:", connack) -- successful connection

		-- subscribe to test topic and publish message after it
		assert(
            client:subscribe{ topic= userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata", qos=1, callback=function(suback)
			print("subscribed:", suback)
				
			-- publish test message
			print('publishing test message "hello" to "luamqtt/simpletest" topic...')
			assert(client:publish{
				topic = userUID .. "/" .. systemName .. "/" .. deviceMAC .. "/jsondata",
				payload = "hello",
				qos = 1,
				properties = {
					payload_format_indicator = 1,
					content_type = "text/plain",
				},
				user_properties = {
					hello = "world",
				},
			})
		end})
	end,

	message = function(msg)
		assert(client:acknowledge(msg))

		print("received:", msg)
		print("disconnecting...")
		assert(client:disconnect())
	end,

	error = function(err)
		print("MQTT client error:", err)
	end,
}

print("running ioloop for it")
mqtt.run_ioloop(client)

print("done, ioloop is stopped")