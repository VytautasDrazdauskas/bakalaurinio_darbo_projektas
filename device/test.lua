#!/usr/bin/lua

local handle = io.popen("echo 'test'")
local result = handle:read("*a")
handle:close()

print(result)