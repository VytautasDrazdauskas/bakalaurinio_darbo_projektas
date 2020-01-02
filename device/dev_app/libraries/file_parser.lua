local file_parser = {}

local function ReadLine(line,type)
        local result = nil
    
        if type == "temp" and string.match(line,"t=")
        then
                local temperature = string.match(line, "t=(.*)")
                result = temperature / 1000
                return result
        end
    
        if type == "ip" and string.match(line,"ip=")
        then
                result = string.match(line, "ip=(.*)")
                return result
        end
        return nil
    end
    
function file_parser.ReadFileData(pathToFile, type)
        local file, err = io.open(pathToFile,"r")
        if err then print("File is empty"); return; end

        local data = ""

        while true do
                local line = file:read()    
                if line == nil then break end

                data = ReadLine(line,type)            
                if (data ~= nil) then break end  
        end        
        file:close()

        return data
end

return file_parser