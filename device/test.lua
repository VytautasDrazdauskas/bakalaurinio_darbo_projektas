local fileParser = require("app.include.file_parser")

BrokerIP = fileParser.ReadFileData("./app/broker.conf","ip")
print("Lua " .. BrokerIP)