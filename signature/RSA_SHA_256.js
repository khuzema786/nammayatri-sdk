const crypto = require('crypto');
const readline = require('readline');

let { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
    },
    privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem'
    }
});

console.log(privateKey, publicKey);

const hash = crypto.createHash('sha256').update(publicKey).digest()
const hashBase64 = Buffer.from(publicKey).toString('base64')

console.log("Base64 Encoded Public Key :", hashBase64)

let data = "\"{\\\"mobileNumber\\\":\\\"9642429378\\\",\\\"mobileCountryCode\\\":\\\"+91\\\",\\\"merchantId\\\":\\\"NAMMA_YATRI\\\",\\\"timestamp\\\":\\\"2023-04-13T07:28:40+00:00\\\"}\"";
const sign = crypto.createSign('RSA-SHA256');
sign.update(data);
const signature = sign.sign(privateKey, 'base64');

console.log("Signature :", signature)

const verify = crypto.createVerify('RSA-SHA256');
verify.update(data);
const isVerified = verify.verify(publicKey, signature, 'base64');

console.log(`Is signature verified: ${isVerified}`);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

new Promise(resolve => rl.question("Click enter to proceed ahead.", ans => {
    rl.close();
    resolve(ans);
})).then(() => {
    fetch('http://127.0.0.1:8013/v2/auth', {
        method: 'POST',
        body: data,
        headers: {
			'x-sdk-authorization': signature,
            'Content-Type': 'application/json;charset=utf-8'
		}
    })
    .then((response) => response.json())
    .then((json) => console.log(json));
})
  