// block:start:create-signature-payload
const crypto = require('crypto');

const privateKey = `-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----`

const createSignature = (payload) => {
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(payload);
    const signature = sign.sign(privateKey, 'base64');
    
    return {
        authData: data,
        signature: signature
    }
}

const data = JSON.stringify({
    "mobileNumber": "9642429378",
    "mobileCountryCode": "+91",
    "merchantId": "PAY_TM",
    "timestamp": "2023-04-13T07:28:40+00:00"
});

createSignature(data);
// block:end:create-signature-payload