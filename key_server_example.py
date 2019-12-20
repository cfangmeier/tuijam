#!/usr/bin/env python
import rsa
import base64
from flask import Flask, request, jsonify

KEYS = dict(
    LASTFM_API_KEY="REDACTED",
    LASTFM_API_SECRET="READACTED",
    GOOGLE_DEVELOPER_KEY="READACTED",
)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def query():
    req_data = request.json
    pub_key = rsa.PublicKey.load_pkcs1(req_data["public_key"])
    keys = {}
    for id_ in req_data["ids"]:
        crypt_bytes = rsa.encrypt(KEYS[id_].encode(), pub_key)
        b64_utf = base64.encodebytes(crypt_bytes).decode()
        keys[id_] = b64_utf
    return jsonify(keys)
