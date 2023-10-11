import time
import threading
from stellar_sdk import Keypair, Network, SorobanServer, StrKey, TransactionBuilder, scval
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

import subprocess

class SorobonSDK:
    def __init__(self) -> None:
        self.rpc_server_url = "https://rpc-futurenet.stellar.org:443/"
        self.network_passphrase =  Network.FUTURENET_NETWORK_PASSPHRASE

        df = pd.read_csv('sdk/borrow.csv')
        df = df.drop('Loan_ID', axis=1)
        X = df.drop('Loan_Status', axis=1)
        y = df['Loan_Status']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LogisticRegression(solver='lbfgs', max_iter=3000)
        model.fit(X_train, y_train)

        model.score(X_test, y_test)

        self.model = model
    
    def deployContract(self, secret, contract_file_path):


        kp = Keypair.from_secret(secret)
        soroban_server = SorobanServer(self.rpc_server_url)

        print("uploading contract...")
        source = soroban_server.load_account(kp.public_key)
        print(source)

        # with open(contract_file_path, "rb") as f:
        #     contract_bin = f.read()

        tx = (
            TransactionBuilder(source, self.network_passphrase)
            .set_timeout(300)
            .append_upload_contract_wasm_op(
                contract=contract_file_path,  # the path to the contract, or binary data
            )
            .build()
        )

        try:
            tx = soroban_server.prepare_transaction(tx)
        except PrepareTransactionException as e:
            print(f"Got exception: {e.simulate_transaction_response}")
            raise e

        tx.sign(kp)
        send_transaction_data = soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")
        if send_transaction_data.status != SendTransactionStatus.PENDING:
            raise Exception("send transaction failed")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_data = soroban_server.get_transaction(send_transaction_data.hash)
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(3)

        print(f"transaction: {get_transaction_data}")

        wasm_id = None
        if get_transaction_data.status == GetTransactionStatus.SUCCESS:
            assert get_transaction_data.result_meta_xdr is not None
            transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
                get_transaction_data.result_meta_xdr
            )
            wasm_id = transaction_meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()  # type: ignore
            print(f"wasm id: {wasm_id}")
        else:
            print(f"Transaction failed: {get_transaction_data.result_xdr}")

        assert wasm_id, "wasm id should not be empty"

        print("creating contract...")

        source = soroban_server.load_account(
            kp.public_key
        )  # refresh source account, because the current SDK will increment the sequence number by one after building a transaction

        tx = (
            TransactionBuilder(source, self.network_passphrase)
            .set_timeout(300)
            .append_create_contract_op(wasm_id=wasm_id, address=kp.public_key)
            .build()
        )

        try:
            tx = soroban_server.prepare_transaction(tx)
        except PrepareTransactionException as e:
            print(f"Got exception: {e.simulate_transaction_response}")
            raise e

        tx.sign(kp)

        send_transaction_data = soroban_server.send_transaction(tx)
        if send_transaction_data.status != SendTransactionStatus.PENDING:
            raise Exception("send transaction failed")
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_data = soroban_server.get_transaction(send_transaction_data.hash)
            if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                break
            time.sleep(3)

        print(f"transaction: {get_transaction_data}")

        if get_transaction_data.status == GetTransactionStatus.SUCCESS:
            assert get_transaction_data.result_meta_xdr is not None
            transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
                get_transaction_data.result_meta_xdr
            )
            result = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hash  # type: ignore
            contract_id = StrKey.encode_contract(result)
            print(f"contract id: {contract_id}")
            return {
                "status" : "success",
                "contractId" : contract_id
            }
        else:
            print(f"Transaction failed: {get_transaction_data.result_xdr}")
            return {
                "status" : "failure",
                "reason" : get_transaction_data.result_xdr
            } 


    # def initialize(self, secret, contract_id, amount, name, symbol):
    #     print(secret)
    #     kp = Keypair.from_secret(secret)
    #     soroban_server = SorobanServer(self.rpc_server_url)
    #     source = soroban_server.load_account(kp.public_key)
    #     print(kp.public_key)
    #     # Let's build a transaction that invokes the `hello` function.
    #     tx = (
    #         TransactionBuilder(source, self.network_passphrase, base_fee=100)
    #         .set_timeout(300)
    #         .append_invoke_contract_function_op(
    #             contract_id=contract_id,
    #             function_name="initialize",
    #             # parameters=[scval.to_address(kp.public_key)]
    #             parameters=[scval.to_address(kp.public_key), scval.to_uint32(amount), scval.to_string(name), scval.to_string(symbol)],
    #             # parameters=[]
    #         )
    #         .build()
    #     )
    #     print(f"XDR: {tx.to_xdr()}")

    #     try:
    #         tx = soroban_server.prepare_transaction(tx)
    #     except PrepareTransactionException as e:
    #         print(e)
    #         print(f"Got exception: {e.simulate_transaction_response}")
    #         return ({
    #                 "status" : "failed"
    #             })
    #         raise e

    #     tx.sign(kp)
    #     print(f"Signed XDR: {tx.to_xdr()}")

    #     send_transaction_data = soroban_server.send_transaction(tx)
    #     print(f"sent transaction: {send_transaction_data}")
    #     if send_transaction_data.status != SendTransactionStatus.PENDING:
    #         raise Exception("send transaction failed")
    #         return ({
    #             "status" : "failed"
    #         })
    #     while True:
    #         print("waiting for transaction to be confirmed...")
    #         get_transaction_data = soroban_server.get_transaction(send_transaction_data.hash)
    #         if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
    #             break
    #         time.sleep(3)

    #     print(f"transaction: {get_transaction_data}")

    #     if get_transaction_data.status == GetTransactionStatus.SUCCESS:
    #         assert get_transaction_data.result_meta_xdr is not None
    #         transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
    #             get_transaction_data.result_meta_xdr
    #         )
    #         result = transaction_meta.v3.soroban_meta.return_value  # type: ignore[union-attr]
    #         # output = [x.sym.sc_symbol.decode() for x in result.vec.sc_vec]  # type: ignore
    #         print(f"transaction result: {result}")
    #         return ({
    #             "status" : "success",
    #         })
    #     else:
    #         print(f"Transaction failed: {get_transaction_data.result_xdr}")
    #         return ({
    #             "status" : "failed"
    #         })
    def initialize(self, secret, contract_id, amount, name, symbol, toAddress):
        kp = Keypair.from_secret(secret)
        initialize = "soroban contract invoke --id " + contract_id + " " + \
          "--source-account " + secret + " " + \
          "--rpc-url " + self.rpc_server_url + " " + \
          '--network-passphrase "' + self.network_passphrase + '" ' + \
          "-- initialize --admin " + kp.public_key + " " + \
          "--decimal " + amount + " --name " + name + " --symbol " + symbol

        result = subprocess.run(initialize, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        if(symbol == "sb"):
            my_thread = threading.Thread(target=self.mintSB, args=(secret, contract_id, amount, toAddress))

            # Start the thread
            my_thread.start()
            # self.mintSB(secret, contract_id, amount, toAddress)

        else:
            mint = "soroban contract invoke --id " + contract_id + " " + \
            "--source-account " + secret + " " + \
            "--rpc-url " + self.rpc_server_url + " " + \
            '--network-passphrase "' + self.network_passphrase + '" ' + \
            "-- mint --to " + kp.public_key + " " + \
            "--amount " + amount
            result = subprocess.run(mint, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result)
            return str(result)

    def get_balance(self, secret, contract_id):
        kp = Keypair.from_secret(secret)
        mint = "soroban contract invoke --id " + contract_id + " " + \
          "--source-account " + secret + " " + \
          "--rpc-url " + self.rpc_server_url + " " + \
          '--network-passphrase "' + self.network_passphrase + '" ' + \
          "-- balance --id " + kp.public_key
        result = subprocess.run(mint, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        return (result.stdout)
    

    def checkBorrow(self, amount) :
        new_data = pd.DataFrame({
            'LoanAmount': [amount],       
            'Loan_Amount_Term': [120],    
        })
        predictions = self.model.predict(new_data)
        return predictions
    

    def lendToken(self, secret, contract_id, to, amount):
        kp = Keypair.from_secret(secret)
        transfer = "soroban contract invoke --id " + contract_id + " " + \
          "--source-account " + secret + " " + \
          "--rpc-url " + self.rpc_server_url + " " + \
          '--network-passphrase "' + self.network_passphrase + '" ' + \
          "-- transfer  --from "  + kp.public_key + " " + \
          "--to " + to + " " + \
          "--amount " + amount 
        result = subprocess.run(transfer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        return result

    def mintSB(self, secret, contract_id, amount, toAddress):
        while True:
            mint = "soroban contract invoke --id " + contract_id + " " + \
                "--source-account " + secret + " " + \
                "--rpc-url " + self.rpc_server_url + " " + \
                '--network-passphrase "' + self.network_passphrase + '" ' + \
                "-- mint --to " + toAddress + " " + \
                "--amount " + amount
            result = subprocess.run(mint, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result)
            time.sleep(10)

    def storeChat(self, secret, contract_id, cid):
        kp = Keypair.from_secret(secret)
        storeCID = "soroban contract invoke --id " + contract_id + " " + \
          "--source-account " + secret + " " + \
          "--rpc-url " + self.rpc_server_url + " " + \
          '--network-passphrase "' + self.network_passphrase + '" ' + \
          "-- store_cid --cid " + cid
        result = subprocess.run(storeCID, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        # return (result.stdout)