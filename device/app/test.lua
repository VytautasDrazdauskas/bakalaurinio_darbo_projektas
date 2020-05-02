local function isempty(s)
    return s == nil or s == ''
end

function IsDublicate(response_id)
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

function ResetDublicateFile()
    local command = "> temp_ids"
    local handle = io.popen(command)
    handle:close()
end

print(IsDublicate("c5a2b9da-8c6c-11ea-bc55-02aa42asfasfac13444a4"))
--ResetDublicateFile()