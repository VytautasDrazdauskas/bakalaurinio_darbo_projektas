local file_parser = {}

local function ReadLine(line,type)
        local result = nil          
        
        result = string.match(line, type.."=(.*)")

        return result
end

local function isempty(s)
        return s == nil or s == ''
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
        if err then print("File is empty"); return nil, true; end

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

function file_parser.OverwriteFileData(pathToFile, inputData)
        local file = io.open(pathToFile, "w+") 
        file:write(inputData)
        file:close()

        return 0
end

function file_parser.UpdateFileData(pathToFile, type, inputData)
        local res, err = file_parser.ReadFileData(pathToFile, type)
        if err then return -1; end

        if res == inputData then return 1
        else
                local file = io.open( pathToFile, "r" )
                local newContent = ""

                while true do --iteruojam per failo eilutes
                        local line = file:read()    
                        if line == nil then break end
                  
                        if (ReadLine(line,type) ~= nil) then 
                                newContent = newContent .. type .. "=" .. inputData .. "\n" --jei randame reikalinga eilute, sukuriam nauja reiksme
                        else
                                newContent =  newContent .. line .. '\n'  -- jei nerandam, paliekam taip, kaip yra
                        end  
                end   
                file:close()

                local fileToWrite = io.open(pathToFile, "w" )

                fileToWrite:write(newContent)
                fileToWrite:close()

                return 0
        end
end

--funkcijos skirtos paketo ID dublikato tikrinimui.
--Paketo ID response_id saugomi tol, kol nepakeiciamas AES raktas
function file_parser.IsDublicate(response_id)
        local command = "cat temp_ids | grep " .. response_id
        local handle = io.popen(command)
        local result = handle:read("*a")
        handle:close()

        if (isempty(result)) then
                local edit_command = "echo '" .. response_id .. "' >> temp_ids"
                local handle = io.popen(edit_command)
                return false
        else
                return true
        end
end

function file_parser.ResetDublicateFile()
        local command = "> temp_ids"
        local handle = io.popen(command)
        handle:close()
end

return file_parser