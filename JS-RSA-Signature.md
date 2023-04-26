const crypto = require('crypto');
const readline = require('readline');

const privateKey = `-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----`

const data = JSON.stringify({
	"mobileNumber" : "9642429378",
  "mobileCountryCode" : "+91",
	"merchantId" : "PAY_TM",
  "timestamp" : "2023-04-13T07:28:40+00:00"
});
const sign = crypto.createSign('RSA-SHA256');
sign.update(data);
const signature = sign.sign(privateKey, 'base64');

const signatureAuthData = {
	authData : data,
	signature : signature
}
