const crypto = require("crypto");
const readline = require('readline');

const { privateKey, publicKey } = crypto.generateKeyPairSync('ed25519', {
    publicKeyEncoding: {
        type: 'spki',
        format: 'pem'
    },
    privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem'
    }
});

// const privateKey = crypto.createPrivateKey("wI22pSXNxsXvItM3K3FKyCLjU1qRadiVZrVcM6mY45w=");
// const publicKey = crypto.createPublicKey("SDDatsOSXC2BSasE2MDpFm2B4+2WwkMK+CBNsiJBiuc=");

console.log(privateKey, publicKey);

let data = JSON.stringify({"mobileNumber":"9642429378","mobileCountryCode":"+91","merchantId":"<MERCHNAT_ID>"});
let hasheddata = crypto.createHash("blake2b512").update(Buffer.from(data)).digest("base64");
console.log(hasheddata);

let signedData = `(created): 1681371205\n(expires): 1681371805\ndigest: BLAKE-512=${hasheddata}`;
let signature = crypto.sign(null, signedData, privateKey);

const authHeader = `Signature keyId="NAMMA_YATRI|juspay-mobility-bpp-1-key|ed25519",algorithm="ed25519",created=1681371205,expires=1681371805,headers="(created) (expires) digest",signature="${signature.toString("base64")}"`;

let isVerified = crypto.verify(null, signedData, publicKey, signature);
console.log(`Is signature verified: ${isVerified}`);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

new Promise(resolve => rl.question("Click enter to proceed ahead.", ans => {
    rl.close();
    resolve(ans);
})).then(() => {
    fetch('http://127.0.0.1:8013/v2/auth/v1', {
        method: 'POST',
        body: data,
        headers: {
			'Authorization': authHeader,
		}
    })
    .then((response) => response.json())
    .then((json) => console.log(json));
})
  