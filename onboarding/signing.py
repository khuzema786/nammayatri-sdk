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

signing_private_key = "ftjLZNZ6+QG8KAcNqax3NiX6Cg1bKVVdnbygReTwpFw="
signing_public_key = "kCa4OlmRVfCPcvzjPPGik0Ljei5dRYuuj/2K6upaf1E="

message = '{"context": {"country": "IND", "domain": "ONDC:TRV10", "timestamp": "2023-06-25T12:26:34.513273Z", "bap_id": "api.sandbox.beckn.juspay.in/loadtest/bap", "transaction_id": "093b07d3-7d80-469b-9fbe-f668d8bf0419", "message_id": "093b07d3-7d80-469b-9fbe-f668d8bf0419", "city": "std:080", "core_version": "0.9.4", "action": "search", "bap_uri": "https://api.sandbox.beckn.juspay.in/loadtest/bap"}, "message": {"intent": {"fulfillment": {"start": {"location": {"gps": "12.923608703179461, 77.61462964117527"}}, "end": {"location": {"gps": "12.9346302, 77.61533969999999"}}}}}}'

signing_private_key64 = base64.b64decode(signing_private_key)
signer = SigningKey(signing_private_key64, encoder=nacl.encoding.RawEncoder)
signed = signer.sign(bytes(message, encoding='utf8'))
signature = base64.b64encode(signed.signature).decode()

public_key64 = base64.b64decode(signing_public_key)
VerifyKey(public_key64).verify(bytes(message, encoding='utf8'), base64.b64decode(signature))