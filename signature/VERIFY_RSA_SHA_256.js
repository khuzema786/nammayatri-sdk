const signaturePayload = "\"{\\\"mobileNumber\\\":\\\"9642429378\\\",\\\"mobileCountryCode\\\":\\\"+91\\\",\\\"merchantId\\\":\\\"NAMMA_YATRI\\\",\\\"timestamp\\\":\\\"2023-04-13T07:28:40+00:00\\\"}\"";
let signature = "Tz8ew9MYewcXBKIkjT7U+Tu3bPN06RZHBIKKbaJjMQ+e5uTaI4Hz0Ktu2KAXITR+7xBhBaLkMZ4Fb6HyaEOUjZES/qid/cVghyi1rJn3A0mI4VmMGt50IOep0b+5Ae2N1yCz58SwWvIRunv345amE0URHD6uca71rk2Rijva5XGjwgNrqOWXpzrHT0y0FRrvEr4u3du8QS2q0Wu4fZ2Ps9RSh04iPVNNuuMcUgkGSktxFP5vJLVYllYJDUzrOxi7nq3R11utNlSQMu18+ATSO5HyMTLxpndjhFlUJqn4QGxYovpp7amztJYjvoEnG9itPp2WdYamVeRAEcJnqRon2w=="

fetch('http://127.0.0.1:8013/v2/auth', {
    method: 'POST',
    body: signaturePayload,
    headers: {
        'x-sdk-authorization': signature,
        'Content-Type': 'application/json;charset=utf-8'
    }
})
.then((response) => response.json())
.then((json) => console.log(json));