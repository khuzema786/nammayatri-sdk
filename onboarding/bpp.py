import time
import re
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
from functools import wraps
from flask import Flask, request, jsonify
import requests
import uuid
import threading
from prometheus_client import Histogram, generate_latest, CONTENT_TYPE_LATEST

outgoing_request_histogram = Histogram(
    "outgoing_request_duration",
    "Outgoing Request Duration",
    ["host","endpoint","method","status"]
)

incoming_request_histogram = Histogram(
    "incoming_request_duration",
    "Incoming Request Duration",
    ["endpoint","method"]
)

def track_requests(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        response = func(*args, **kwargs)
        duration = time.time() - start_time
        incoming_request_histogram.labels(endpoint=request.path, method=request.method).observe(duration)
        return response
    return decorated_function

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

gateway_url = os.getenv("GATEWAY_URL")
registry_url = os.getenv("REGISTRY_URL")

signing_private_key = os.getenv("SIGNING_PRIVATE_KEY")
subscriber_id = os.getenv("SUBSCRIBER_ID")
unique_key_id = os.getenv("UNIQUE_KEY_ID")
signature_type = os.getenv("SIGNATURE_TYPE")

def sign_response(signing_key):
    signing_private_key64 = base64.b64decode(signing_private_key)
    signer = SigningKey(signing_private_key64, encoder=nacl.encoding.RawEncoder)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature

def hash_message(msg:str):
    HASHER = nacl.hash.blake2b
    digest = HASHER(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str

def create_signing_string(digest_base64, created, expires):
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string

def create_authorisation_header(request_body):
    created = int(datetime.datetime.now().timestamp())
    expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    signing_key = create_signing_string(hash_message(request_body), created, expires)
    signature = sign_response(signing_key)
    if signature_type == "BECKN":
        return f'Signature keyId=\"{subscriber_id}|{unique_key_id}|ed25519\",algorithm=\"ed25519\",created=' \
               f'\"{created}\",expires=\"{expires}\",headers=\"(created) (expires) digest\",signature=\"{signature}\"'
    else:
        return f'Signature keyId=\"{subscriber_id}|{unique_key_id}|ed25519\",algorithm=\"ed25519\",created=' \
               f'{created},expires={expires},headers=\"(created) (expires) digest\",signature=\"{signature}\"'

def get_filter_dictionary_or_operation(filter_string):
    filter_string_list = re.split(',', filter_string)
    filter_string_list = [x.strip(' ') for x in filter_string_list]  # to remove white spaces from list
    filter_dictionary_or_operation = dict()
    for fs in filter_string_list:
        splits = fs.split('=', maxsplit=1)
        key = splits[0].strip()
        value = splits[1].strip()
        filter_dictionary_or_operation[key] = value.replace("\"", "")
    return filter_dictionary_or_operation

def verify_response(signature, signing_key, public_key):
    try:
        public_key64 = base64.b64decode(public_key)
        VerifyKey(public_key64).verify(bytes(signing_key, encoding='utf8'), base64.b64decode(signature))
        return True
    except Exception:
        return False

def verify_authorisation_header(auth_header, request_body_str):
    req = json.loads(request_body_str)
    header_parts = get_filter_dictionary_or_operation(auth_header.replace("Signature ", ""))
    created = int(header_parts['created'])
    expires = int(header_parts['expires'])
    current_timestamp = int(datetime.datetime.now().timestamp())
    if created <= current_timestamp <= expires:
        try:
            signing_key = create_signing_string(hash_message(request_body_str), created=created, expires=expires)
            lookup_req = {
                "subscriber_id" : header_parts['keyId'].split("|")[0],
                "ukId" : header_parts['keyId'].split("|")[1],
            }
            response = requests.post(f"{registry_url}/lookup", json=lookup_req)
            if response.status_code != 200:
                print({ "pod" : os.getenv("POD_NAME"), "action" : "registry_lookup_failed", "transactionId" : req['context']['transaction_id'], "messageId" : req['context']['message_id'], "request_body" : request_body_str })
            if len(response.json()) >= 1:
                return verify_response(header_parts['signature'], signing_key, public_key=response.json()[0]['signing_public_key'])
            else:
                print({ "pod" : os.getenv("POD_NAME"), "action" : "registry_lookup_empty", "transactionId" : req['context']['transaction_id'], "messageId" : req['context']['message_id'], "request_body" : request_body_str })
                return False
        except:
            print({ "pod" : os.getenv("POD_NAME"), "action" : "signature_verification_exception", "transactionId" : req['context']['transaction_id'], "messageId" : req['context']['message_id'], "request_body" : request_body_str })
            return False
    else:
        return False

def signature_authenticate(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        signature = request.headers.get('Authorization')
        if not verify_authorisation_header(signature, request.data.decode('utf-8')):
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return decorated

@app.route('/search', methods=['POST'])
@track_requests
@signature_authenticate
def search():
    search_req = request.get_json()
    current_datetime = datetime.datetime.now()
    current_datetime_iso8601 = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    on_search_req = {
        "context": {
            "country": search_req['context']['country'],
            "bpp_uri": f"https://{subscriber_id}",
            "domain": search_req['context']['domain'],
            "timestamp": current_datetime_iso8601,
            "bap_id": search_req['context']['bap_id'],
            "transaction_id": search_req['context']['transaction_id'],
            "bpp_id": subscriber_id,
            "message_id": search_req['context']['message_id'],
            "city": search_req['context']['city'],
            "core_version": search_req['context']['core_version'],
            "action": "on_search",
            "bap_uri": search_req['context']['bap_uri']
        },
        "message": {
            "catalog": {
                "bpp/descriptor": {},
                "bpp/providers": []
            }
        }
    }
    on_search_req_str = json.dumps(on_search_req)
    headers = {
        "Content-Type": "application/json",
        "Authorization": create_authorisation_header(on_search_req_str)
    }
    start_time = time.time()
    response = requests.post(f"{gateway_url}/on_search", data=on_search_req_str, headers=headers)
    duration = time.time() - start_time
    outgoing_request_histogram.labels(host=f"{gateway_url}", endpoint="/on_search", method="POST", status=response.status_code).observe(duration)
    print({ "pod" : os.getenv("POD_NAME"), "action" : "search", "transactionId" : search_req['context']['transaction_id'], "messageId" : search_req['context']['message_id'], "status" : response.status_code })
    if response.status_code == 200:
        return { "message" : f"/on_search passed for transaction_id : {search_req['context']['transaction_id']}" }
    else:
        return { "message" : f"/on_search failed for transaction_id : {search_req['context']['transaction_id']} | {response.text}" }

if __name__ == '__main__':
    app.run(port=5001, host="0.0.0.0")
