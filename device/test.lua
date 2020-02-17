local fileParser = require("app.libraries.file_parser")
local pathToFile = "./broker.conf"
local type = "useruuid"
local data = "380c1f12-a74b-4a9d-9560-27335e54f7d3"

local res, err = fileParser.ReadFileData(pathToFile, type)
print(res)
print(err)

fileParser.UpdateFileData(pathToFile, type, data)