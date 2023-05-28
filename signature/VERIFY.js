const crypto = require('crypto');
const fs = require("fs");

const signaturePayload1 = "\"{\\\"userId\\\":\\\"1700612387\\\",\\\"mobileNumber\\\":\\\"9760014894\\\",\\\"mobileCountryCode\\\":\\\"+91\\\",\\\"merchantId\\\":\\\"MOBILITY_PAYTM\\\",\\\"timestamp\\\":\\\"2023-05-14T09:07:45.759Z\\\"}\"" //"\"{\\\"userId\\\":\\\"2141312\\\",\\\"mobileNumber\\\":\\\"9819xxxx90\\\",\\\"mobileCountryCode\\\":\\\"+91\\\",\\\"merchantId\\\":\\\"MOBILITY_PAYTM\\\",\\\"timestamp\\\":\\\"2023-05-14T08:56:42.302Z\\\"}\"";
const signaturePayload2 = "{\"userId\":\"1700612387\",\"mobileNumber\":\"9760014894\",\"mobileCountryCode\":\"+91\",\"merchantId\":\"MOBILITY_PAYTM\",\"timestamp\":\"2023-05-14T08:10:24.253Z\"}";
console.log(signaturePayload1)
console.log(signaturePayload2)
let signature = "uAnRuPJ5mbdL458siNQYMvxAdJ/yM0TRsGiqYIlPMbolZKKjOlLzsiq1c7+5OlwFZoGikDRn9M9Ci5XCJzeywsgnbKs/Obq41RSGLNOII7K9cKXzbtFQqtmRIAlF4+jRCjrAiokJO9wEDk6HQ3g9hhisjOyLnRUTmr803IT4wiGHt5TtL6jBweMfx1AImGfTRGDsGn8Z3i8egdYGR6L46Vm5wGonRX3Y3icCxmu3vKROMS5b4s77gUNr9pSAc40IcqFL9LNMKVZM1jx73gpzz7MB4LrvtJ+R4ZkvyNhXjpImyEYzB223uVxnECn0TwGOp3pyIQXI9WKWb9L/mbZEmQ=="
console.log(signature)
const publicKey = fs.readFileSync(__dirname + "/public-key.pem", "utf8");

const hashBase64 = Buffer.from(publicKey).toString('base64')

console.log("Base64 Encoded Public Key :", hashBase64)

const verify = crypto.createVerify('RSA-SHA256');
verify.update(signaturePayload1);
const isVerified = verify.verify(publicKey, signature, 'base64');

console.log(isVerified)

