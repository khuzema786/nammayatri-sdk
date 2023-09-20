-- Define the HTTP request
request = function()
    local headers = {
        ["token"] = "00d45543-417b-4a92-af65-94f18e459ebe",
        ["vt"] = "SUV",
        ["mId"] = "7f7896dd-787e-4a0b-8675-e9e6fe93bb8f",
        ["Content-Type"] = "application/json"
    }
    local body = '[{"pt": {"lat": 13.21105683994044,"lon": 77.86952343480942},"ts": "2023-09-07T20:46:27+00:00","acc": 0}]'

    return wrk.format("POST", nil, headers, body)
end

local response_codes = {}

response = function(status, headers, body)
    if status >= 200 and status < 300 then
        return
    end

    if not response_codes[status] then
        response_codes[status] = 1
    else
        response_codes[status] = response_codes[status] + 1
    end
end

done = function(summary, latency, requests)
    for code, count in pairs(response_codes) do
        print(code, count)
    end
end
