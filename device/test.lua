local handler = io.popen("ping -c 1 -W 1 192.168.137.253")
local response = handler:read("*a")
handler:close()

if string.match(response, "1 packets transmitted, 1 packets received, 0%% packet loss") then
    print ("success")
  else
    print ("no link")
  end
