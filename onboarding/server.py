import json
import time
import os
import base64
import datetime
import json
import nacl.encoding
import nacl.hash
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey, VerifyKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey,X25519PublicKey
from cryptography.hazmat.primitives import serialization
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad,unpad
from flask import Flask
import requests
import uuid
import threading

registry_url = "https://preprod.registry.ondc.org/ondc/subscribe"

# bapBaseUrl = "api.sandbox.beckn.juspay.in/dev"
# bppBaseUrl = "api.sandbox.beckn.juspay.in/dev/dobpp"

bapBaseUrl = "api.sandbox.beckn.juspay.in/loadtest/bap"
bppBaseUrl = "api.sandbox.beckn.juspay.in/loadtest/bpp"

bapSubscribeBody = {
  "context": {
    "operation": {
      "ops_no": 1
    },
    "request_id": "",
    "timestamp": "2023-06-19T13:44:54.101Z",
    "entity": {
      "gst": {
        "legal_entity_name": "JUSPAY TECHNOLOGIES PRIVATE LIMITED",
        "business_address": "STALLION BUSINESS CENTRE, NO 444, 18TH MAIN, 6TH BLOCK, KORAMANGALA, BENGALLURU, Bengaluru Urban, Karnataka, 560095",
        "city_code": [
          "std:080"
        ],
        "gst_no": "29AACCJ9163G1Z9"
      },
      "pan": {
        "name_as_per_pan": "JUSPAY TECHNOLOGIES PRIVATE LIMITED",
        "pan_no": "AACCJ9163G",
        "date_of_incorporation": "01/07/2017"
      },
      "name_of_authorised_signatory": "JUSPAY",
      "address_of_authorised Signatory": "STALLION BUSINESS CENTRE, NO 444, 18TH MAIN, 6TH BLOCK, KORAMANGALA, BENGALLURU, Bengaluru Urban, Karnataka, 560095",
      "email_id": "mags@juspay.in",
      "mobile_no": 9620902139,
      "country": "IND",
      "subscriber_id": "",
      "unique_key_id": "",
      "callback_url": "",
      "key_pair": {
        "signing_public_key": "",
        "encryption_public_key": "",
        "valid_from": "2021-01-01T00:00:00Z",
        "valid_until": "2030-06-19T11:57:54.101Z"
      }
    },
    "network_participant": [
      {
        "subscriber_url": "",
        "domain": "ONDC:TRV10",
        "type": "buyerApp",
        "msn": False,
        "city_code": []
      }
    ]
  }
}

bppSubscribeBody = {
  "context": {
    "operation": {
      "ops_no": 2
    }
  },
  "message": {
    "request_id": "",
    "timestamp": "2023-06-19T13:44:54.101Z",
    "entity": {
      "gst": {
        "legal_entity_name": "JUSPAY TECHNOLOGIES PRIVATE LIMITED",
        "business_address": "STALLION BUSINESS CENTRE, NO 444, 18TH MAIN, 6TH BLOCK, KORAMANGALA, BENGALLURU, Bengaluru Urban, Karnataka, 560095",
        "city_code": [
          "std:080"
        ],
        "gst_no": "29AACCJ9163G1Z9"
      },
      "pan": {
        "name_as_per_pan": "JUSPAY TECHNOLOGIES PRIVATE LIMITED",
        "pan_no": "AACCJ9163G",
        "date_of_incorporation": "01/07/2017"
      },
      "name_of_authorised_signatory": "JUSPAY",
      "address_of_authorised Signatory": "STALLION BUSINESS CENTRE, NO 444, 18TH MAIN, 6TH BLOCK, KORAMANGALA, BENGALLURU, Bengaluru Urban, Karnataka, 560095",
      "email_id": "mags@juspay.in",
      "mobile_no": 9620902139,
      "country": "IND",
      "subscriber_id": "",
      "unique_key_id": "",
      "callback_url": "",
      "key_pair": {
        "signing_public_key": "",
        "encryption_public_key": "",
        "valid_from": "2021-01-01T00:00:00Z",
        "valid_until": "2030-06-19T11:57:54.101Z"
      }
    },
    "network_participant": [
      {
        "subscriber_url": "",
        "domain": "ONDC:TRV10",
        "type": "sellerApp",
        "msn": False,
        "city_code": [
          ""
        ]
      }
    ]
  }
}

subscribers = {
    "api.sandbox.beckn.juspay.in/loadtest/bpp | 80" : {
        "signingPublicKey" : "kCa4OlmRVfCPcvzjPPGik0Ljei5dRYuuj/2K6upaf1E=",
        "signingPrivateKey" : "y+am+uN/7KL9AXbGGSwRZcnw0fO4JRPNEsKZCYKMyTEQtx0d3WlSBpqVZIT3oFym4QqmpyivO3mAsP5ac/toAQ==",
        "encPublicKey" : "MCowBQYDK2VuAyEAGidjRUcKUmkVkEnbPOS/0EN/9iEo6fFiYajfCekRQRE=",
        "encPrivateKey" : "MC4CAQAwBQYDK2VuBCIEIHhGdE0ECPBcW/lA+1X9ynLx32s1fTsBlA5A7XDKO8Zl",
        "type" : "BPP",
        "city" : "std:080"
    },
    "api.sandbox.beckn.juspay.in/loadtest/bap | 81" : {
        "signingPublicKey" : "kCa4OlmRVfCPcvzjPPGik0Ljei5dRYuuj/2K6upaf1E=",
        "signingPrivateKey" : "y+am+uN/7KL9AXbGGSwRZcnw0fO4JRPNEsKZCYKMyTEQtx0d3WlSBpqVZIT3oFym4QqmpyivO3mAsP5ac/toAQ==",
        "encPublicKey" : "MCowBQYDK2VuAyEAGidjRUcKUmkVkEnbPOS/0EN/9iEo6fFiYajfCekRQRE=",
        "encPrivateKey" : "MC4CAQAwBQYDK2VuBCIEIHhGdE0ECPBcW/lA+1X9ynLx32s1fTsBlA5A7XDKO8Zl",
        "type" : "BAP",
        "city" : "std:080"
    }
}

def sign_response(signing_key, signing_private_key):
    signing_private_key64 = base64.b64decode(signing_private_key)
    seed = crypto_sign_ed25519_sk_to_seed(signing_private_key64)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature

def hash_message(msg:str):
    HASHER = nacl.hash.blake2b
    digest = HASHER(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str

def create_signing_string(digest_base64):
    created = int(datetime.datetime.now().timestamp())
    expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string

def decrypt(enc_private_key, enc_public_key, cipherstring):
    private_key = serialization.load_der_private_key(
        base64.b64decode(enc_private_key),
        password=None
    )
    public_key = serialization.load_der_public_key(
        base64.b64decode(enc_public_key)
    )
    shared_key = private_key.exchange(public_key)
    cipher = AES.new(shared_key, AES.MODE_ECB)
    ciphertxt = base64.b64decode(cipherstring)
    return cipher.decrypt(ciphertxt).decode('utf-8')

def createHtml(request_id, subscriber, subscriber_id):
    signing_key = create_signing_string(hash_message(request_id))
    print(subscriber)
    signature = sign_response(signing_key, subscriber['signingPrivateKey'])
    htmlFile = f'''
    <html>
        <head>
            <meta name='ondc-site-verification' content='{signature}' />
        </head>
        <body>
            ONDC Site Verification Page
        </body>
    </html>
    '''
    if subscriber['type'] == "BAP":
        if not os.path.exists(f'ondc-verification/{subscriber_id[slice(len(bapBaseUrl) + 1, len(subscriber_id))]}'):
            os.makedirs(f'ondc-verification/{subscriber_id[slice(len(bapBaseUrl) + 1, len(subscriber_id))]}')
        with open(f"ondc-verification/{subscriber_id[slice(len(bapBaseUrl) + 1, len(subscriber_id))]}/ondc-site-verification.html", "w+") as file:
            file.write(htmlFile)
    elif subscriber['type'] == "BPP":
        if not os.path.exists(f'ondc-verification/{subscriber_id[slice(len(bppBaseUrl) + 1, len(subscriber_id))]}'):
            os.makedirs(f'ondc-verification/{subscriber_id[slice(len(bppBaseUrl) + 1, len(subscriber_id))]}')
        with open(f"ondc-verification/{subscriber_id[slice(len(bppBaseUrl) + 1, len(subscriber_id))]}/ondc-site-verification.html", "w+") as file:
            file.write(htmlFile)

app = Flask(__name__)

@app.route('/cab/v1/on_subscribe', methods=['POST'])
def bap_onsubscribe():
    data = request.get_json()
    subscriber = subscribers[data.subscriber_id]
    return { 
        answer : decrypt(subscriber['encPublicKey'], subscriber['encPrivateKey'], data.challenge) 
    }

@app.route('/beckn/<merchantId>/on_subscribe', methods=['POST'])
def bpp_onsubscribe(merchantId):
    data = request.get_json()
    subscriber = subscribers[data.subscriber_id]
    return { 
        answer : decrypt(subscriber['encPublicKey'], subscriber['encPrivateKey'], data.challenge) 
    }

def serve_file():
    os.system('python -m http.server 8000 --directory ondc-verification')

def serve_files():
    for subscriber_uk_id, subscriber in subscribers.items():
        [subscriber_id, unique_key_id] = subscriber_uk_id.split(' | ')
        request_id = str(uuid.uuid4())
        subscribers[subscriber_uk_id]['requestId'] = request_id
        createHtml(request_id, subscriber, subscriber_id)
    threading.Thread(target=serve_file).start()
    time.sleep(5)
    for subscriber_uk_id, subscriber in subscribers.items():
        [subscriber_id, unique_key_id] = subscriber_uk_id.split(' | ')
        request_id = subscriber['requestId']
        current_datetime = datetime.datetime.now()
        current_datetime_iso8601 = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if subscriber['type'] == 'BAP':
            bapSubscribeBody['context']['request_id'] = request_id
            bapSubscribeBody['context']['timestamp'] = current_datetime_iso8601
            bapSubscribeBody['context']['entity']['subscriber_id'] = subscriber_id
            bapSubscribeBody['context']['entity']['unique_key_id'] = unique_key_id
            bapSubscribeBody['context']['entity']['key_pair']['signing_public_key'] = subscriber['signingPublicKey']
            bapSubscribeBody['context']['entity']['key_pair']['encryption_public_key'] = subscriber['encPublicKey']
            bapSubscribeBody['context']['entity']['key_pair']['valid_from'] = current_datetime_iso8601
            bapSubscribeBody['context']['network_participant'][0]['subscriber_url'] = f'https://{subscriber_id}'
            bapSubscribeBody['context']['network_participant'][0]['city_code'] = subscriber['city']

            print(json.dumps(bapSubscribeBody))

            # response = requests.post(registry_url, json=bapSubscribeBody)
            # if response.status_code == 200:
            #     print(f"/subscribe for {subscriber_uk_id} request successful")
            # else:
            #     print(f"/subscribe for {subscriber_uk_id} request failed")
        elif subscriber['type'] == 'BPP':
            bppSubscribeBody['message']['request_id'] = request_id
            bppSubscribeBody['message']['timestamp'] = current_datetime_iso8601
            bppSubscribeBody['message']['entity']['subscriber_id'] = subscriber_id
            bppSubscribeBody['message']['entity']['unique_key_id'] = unique_key_id
            bppSubscribeBody['message']['entity']['key_pair']['signing_public_key'] = subscriber['signingPublicKey']
            bppSubscribeBody['message']['entity']['key_pair']['encryption_public_key'] = subscriber['encPublicKey']
            bppSubscribeBody['message']['entity']['key_pair']['valid_from'] = current_datetime_iso8601
            bppSubscribeBody['message']['network_participant'][0]['subscriber_url'] = f'https://{subscriber_id}'
            bppSubscribeBody['message']['network_participant'][0]['city_code'] = subscriber['city']

            print(json.dumps(bppSubscribeBody))

            # response = requests.post(registry_url, json=bppSubscribeBody)
            # if response.status_code == 200:
            #     print(f"/subscribe for {subscriber_uk_id} request successful")
            # else:
            #     print(f"/subscribe for {subscriber_uk_id} request failed")

def start_flask_app():
    app.run()

if __name__ == '__main__':
    thread1 = threading.Thread(target=start_flask_app)
    thread2 = threading.Thread(target=serve_files)

    thread1.start()
    thread2.start()