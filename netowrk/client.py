import sys
sys.path.append('../model')

import threading, random, socket
import multiprocessing
import secrets, string, pickle
from io import StringIO
import pandas as pd

from peer_federated_training import start_train


host = '127.0.0.1'
peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with open("port_number.txt", "r") as file:
    port = file.read()
stop_process = False
process = []
peerid = ""

def send_message():
    message = input("Enter the message : ")
    peer.send(message.encode())



def handle_messages():
    while not stop_process:
        try:
            message = peer.recv(1024).decode()
            

            if message == "train":
                with open("./peerfiles/" + peerid + ".pkl", 'rb') as file:
                    chunk = pickle.load(file)
                # print(chunk)
                values = start_train(chunk['X'], chunk['y'], chunk['mod'])
                print("mod : ", chunk['mod'])
                print("mask : ", chunk['mask'])
                print("accuracy : ", values['accuracy'])
                with open("./modelparameters/" + peerid  + ".pkl", 'wb') as file:
                    pickle.dump(values, file)

            elif message == "peerid":
                characters = string.ascii_letters + string.digits
                peerid = ''.join(secrets.choice(characters) for _ in range(10))
                print(f'You Peer Id is : {peerid}')
                peer.send(peerid.encode('utf-8'))
            else:
                print(message)
        except:
            pass

    
def start_server():
    print(f'Peer is running and listening on {port}...')
    peer.connect((host, int(port)))
    peer_process = threading.Thread(target=handle_messages)
    peer_process.start()
    process.append(peer_process)


def stop_peer():
    peer.close()
    stop_process = True
    for pro in process:
        pro.terminate()
    return

if __name__ == '__main__':

    while True:
        print("\n\n\t\t*****************Welcome to AI DAO*****************\n")
        print("\t\t1.Start peer")
        print("\t\t2.Send message")
        print("\t\t3.Exit\n\n")

        choice = int(input("Enter your choice : "))
        if choice == 1:
            start_server()
        
        elif choice == 2:
            send_message()

        else:
            stop_peer()
            break
