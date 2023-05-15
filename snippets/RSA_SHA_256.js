const crypto = require('crypto');

const data = JSON.stringify({
    "mobileNumber": "9642429378",
    "mobileCountryCode": "+91",
    "merchantId": "<MERCHANT_ID>",
    "timestamp": "2023-04-13T07:28:40+00:00"
});

// block:start:read-private-key
const privateKey = fs.readFileSync(__dirname + "/private-key.pem", "utf8");
// block:end:read-private-key

// block:start:create-signature
const sign = crypto.createSign('RSA-SHA256');
sign.update(data);
// block:end:create-signature

// block:start:base64
const signature = sign.sign(privateKey, 'base64');
// block:end:base64

const signatureAuthData = {
    authData: data,
    signature: signature
}