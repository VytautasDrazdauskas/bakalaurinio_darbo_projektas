local file_parser = {}

local function ReadLine(line,type)
        local result = nil          
        
        result = string.match(line, type.."=(.*)")

        return result
end

function file_parser.GetData(string,type)
	local result = nil
	
	for i in string.gmatch(string, "[^;]+") do
		result = string.match(i, type .. "=(.*)")
		if result ~= nil then
			return result
		end
	end

	return result
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