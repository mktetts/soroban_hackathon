from pythonSDK.utils.success import Success
from pythonSDK.utils.error import Error
from pythonSDK.sdk.sdkUtils import SorobonSDK
from web3.middleware import geth_poa_middleware
from flask import jsonify, request
import sys, json, subprocess
import os
from pinatapy import PinataPy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import svm

from dotenv import load_dotenv

load_dotenv()


sys.dont_write_bytecode = True

sdk = SorobonSDK()


def check():
    print(request.json)
    return jsonify({"name": "muthu"})


def deploy():
    params = (request.json)["params"]
    res = sdk.deployContract(params["secretkey"], params["contract_path"])
    return res


def initialize():
    params = (request.json)["params"]
    res = sdk.initialize(
        params["tokenOwner"],
        params["contractId"],
        params["initialAmount"],
        params["tokenName"],
        params["tokenSymbol"],
        params['toAddress']
    )
    return jsonify({"result": res})


def get_balance():
    params = (request.json)["params"]
    res = sdk.get_balance(params["secretkey"], params["contractId"])
    return jsonify({"result": res})


def chat():
    params = (request.json)
    print(params)
    with open("chat/chat.json", "w") as json_file:
        json.dump(params, json_file)
    openssl_cmd1 = [
        "openssl",
        "enc",
        "-aes-256-cbc",
        "-in",
        "chat/chat.json",
        "-out",
        "chat/chat_enc.dat",
        "-pass",
        "pass:12345",
    ]

    try:
        subprocess.run(openssl_cmd1, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    openssl_cmd2 = [
        "openssl",
        "enc",
        "-d",  # Decryption mode
        "-aes-256-cbc",
        "-in",
        "chat/chat_enc.dat",
        "-out",
        "chat/chat_dec.json",
        "-pass",
        "pass:12345",
    ]

    try:
        subprocess.run(openssl_cmd2, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    jwt = os.getenv('JWT')

    pinata_api_key=str(api_key)
    pinata_secret_api_key=str(api_secret)
    pinata = PinataPy(pinata_api_key,pinata_secret_api_key)

    # Upload the file
    result = pinata.pin_file_to_ipfs("chat/chat_enc.dat")
    print(result)
    print(params)
    sdk.storeChat(params['secretkey'], params['contractId'], result['IpfsHash'])
    # Should return the CID (unique identifier) of the file
    return jsonify({"status": "success"})

def borrow():
    params = (request.json)["params"]
    res = sdk.checkBorrow(params['amount'])
    if(res[0] == "Y"):
        res = "Approved"
    else:
        res = "Not Approved"
    return jsonify({
        "result" : res
    })

def lend():
    params = (request.json)['params']
    res = sdk.lendToken(params['secretkey'], params['contractId'], params['toAddress'], params['amount'])
    return jsonify({
        "result" : res.stdout
    })