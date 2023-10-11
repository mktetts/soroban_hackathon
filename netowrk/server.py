import sys
sys.path.append('../consensus')
sys.path.append('../model')
import consensus as Con
import pandas as pd, pickle, time
from io import StringIO
from peer_federated_training import overall_accuracy
from sklearn.metrics import accuracy_score


con = Con.Consensus()

import numpy as np, json
from sklearn.model_selection import train_test_split
from sklearn import datasets

import threading, random, socket
import multiprocessing


host = '127.0.0.1'
port = random.randint(1000, 9999)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
with open("port_number.txt", "w") as file:
    file.write(str(port))

peers = []
users = []
process = []
stop_process = False

X_train, X_test, y_train, y_test = [], [], [], []
def broadcast_all(message):
    print(peers)
    for i in range(len(peers)):
        time.sleep(1)
        peers[i]['socket'].send(message.encode())

def broadcast(self):
    pass

def handle_messages(client):
    while not stop_process:
        try:
            message = client.recv(1024).decode()
            print(message)
                
        except:
            pass

def accept_client():
    while not stop_process:
        client, address = server.accept()
        print(f'Connection is established with {str(address)}')
        client.send('peerid'.encode())
        peerid = client.recv(1024)
        print(peerid)
        client_data = {
            'socket' : client,
            'peerid' : peerid.decode()
        }
        peers.append(client_data)
        client_process = threading.Thread(target=handle_messages, args=(client, ))
        client_process.start()
        process.append(client_process)

def start_server():
    print(f'Server is running and listening on {port}...')
    accept_client_process = threading.Thread(target=accept_client)
    accept_client_process.start()
    process.append(accept_client_process)

def list_peers():
    pass

def stop_server():
    server.close()
    stop_process = True
    for pro in process:
        pro.terminate()
    return

def start_training():
    global X_train, X_test, y_train, y_test
    # dataset = datasets.load_breast_cancer()
    # X, y = dataset.data, dataset.target
    # x_column = X[:, 3]
    # new_values = 2 + 53 * x_column
    # X[:, 3] = new_values
    titanic_data = pd.read_csv('./train.csv')
    # titanic_data['Age'] = 53 * titanic_data['Age'] + 2
    titanic_data
    # titanic_data['Age'].plot.hist()
    titanic_data.info()
    titanic_data.isnull().sum()
    titanic_data.drop('Cabin', axis=1, inplace=True)
    titanic_data.dropna(inplace=True)
    sex = pd.get_dummies(titanic_data['Sex'], drop_first=True)
    embarked = pd.get_dummies(titanic_data['Embarked'], drop_first=True)
    pcl = pd.get_dummies(titanic_data['Pclass'], drop_first=True)
    titanic_data = pd.concat([titanic_data, sex, embarked, pcl], axis=1)
    titanic_data.head(5)
    titanic_data.drop(['Sex', 'Embarked', 'PassengerId', 'Name', 'Ticket'], axis=1, inplace=True)
    titanic_data.drop('Pclass', axis=1, inplace=True)

    # print(bc.data[:5])

    # X, y = bc.data, bc.target
    X = titanic_data.drop('Survived', axis=1)
    y = titanic_data['Survived']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)
    chunks = con.split_chunks(X, y, peers=5)
    for i in range(5):
        with open("./peerfiles/" + peers[i]['peerid'] + ".pkl", 'wb') as file:
            pickle.dump(chunks[i], file)
        # chunks[i] = (json.dumps(chunks[i]))

    broadcast_all("train")

def build_proof():
    infile, outfile = [], []
    weights, bias = [], []
    for i in range(len(peers)):
        with open("./peerfiles/" + peers[i]['peerid'] + ".pkl", 'rb') as file:
                infile.append(pickle.load(file))
        with open("./modelparameters/" + peers[i]['peerid'] + ".pkl", 'rb') as file:
                outfile.append(pickle.load(file))
                weights.append(outfile[i]['weights'])
                bias.append(outfile[i]['bias'])

    finalizedModels = {}
    finalizedModels['weights'] = weights
    finalizedModels['bias'] = bias
    with open("./finalisedmodels/" + "cancer_prediction" + ".pkl", 'wb') as file:
        pickle.dump(finalizedModels, file)
    decrypted_weights, decrypted_bias = [], []
    for i in range(len(peers)):
        decrypted_weights.append(con.decrypt(weights[i]))
        decrypted_bias.append(con.decrypt(bias[i]))
    weights = np.mean(decrypted_weights, axis=0)
    bias = np.mean(decrypted_bias)
    pred = overall_accuracy(X_test, weights, bias)
    # print("Overall Accuracy : ", accuracy_score(y_test, pred))
    print("Overall Accuracy : ", np.sum(pred==y_test)/len(y_test) )
    con.build_web(infile, outfile, peers=5)

if __name__ == '__main__':

    while True:
        print("\n\n\t\t*****************Welcome to AI DAO*****************\n")
        print("\t\t1.Start server")
        print("\t\t2.Start Training")
        print("\t\t3.Build Proof")
        print("\t\t4.Exit\n\n")

        choice = int(input("Enter your choice : "))
        if choice == 1:
            start_server()
        
        elif choice == 2:
            start_training()

        elif choice == 3:
            build_proof()

        else:
            stop_server()
            break
