import math
import random
import pandas as pd
from functools import reduce
import operator
import numpy as np

class Consensus():
    def __init__(self) -> None:

        self.prime = 53
        self.deci = False
        row = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
                    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@', '#', '$', 
                    '%', '^', '&', '*', '(', ')', '-', '=', '|', '.', ',', '<', '~', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        column = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
                    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@', '#', '$', 
                    '%', '^', '&', '*', '(', ')', '-', '=', '|', '.',  ',','<' ,'~', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

        # row = ['a', 'b', 'c', 'd', 'e']
        # column = ['a', 'b', 'c', 'd', 'e']

        self.row = self.shuffle(row)
        self.column = self.shuffle(column)

        table = []
        for letter1 in self.row:
            row = []
            for letter2 in self.column:
                row.append(letter1 + letter2)
                self.shuffle(row)
            table.append(row)

        fermats_table = []

        for i in range(len(self.row)):
            column = []
            for row in table:
                column.append(row[i])
                self.shuffle(column)
            fermats_table.append(column)

        value = 1
        self.fermats_numbers = {}
        for i in range(len(fermats_table[0])):
            for j in range(len(fermats_table[i])):
                self.fermats_numbers[fermats_table[j][i]] = {"pos" : i, "value" : value}
                value += 1
        
        self.fermats_table = fermats_table
        
        df = pd.DataFrame(self.fermats_numbers).T
        df.to_excel(excel_writer = "test.xlsx")
        # print(self.fermats_table)
        # print(self.fermats_numbers)
        self.value = []

    def encrypt_numbers(self, num, mod):
        temp_d, num = {}, str(num)
        # digits = 4
        encrypted = ""
        for ch in num:
            if ch == '.':
                self.deci = True
                encrypted = encrypted +  ".." 
            elif ch == '-':
                encrypted = encrypted +  "--" 
            else:
                ch = int(ch)
                if ch in temp_d:
                    temp_d[ch] = (temp_d[ch] + 1) % (self.prime // 10)
                    ch = (temp_d[ch] * 10) + ch
                else:
                    temp_d[ch] = 1
                encrypted =  encrypted + self.fermats_table[mod][ch]
            # digits -= 1
            # if(digits == 0):
            #     break
        self.encrypted = encrypted
        return self.encrypted
        # print(self.encrypted)


    def decrypt_numbers(self, encrypted):
        decrypted = ""
        # value = []
        for i in range(0, len(encrypted), 2):
            if encrypted[i:i+2] == "..":
                decrypted += '.'
                self.deci = True
            elif encrypted[i:i+2] == "--":
                decrypted += "-"
            else:
                s = self.fermats_numbers[encrypted[i:i+2]]
                decrypted += str(((s)['pos']) % 10)
                self.value.append(s['value'])

            # print(s)
        print((decrypted))
        # print(value)
        # result = [num % self.prime for num in value]
        # result = reduce(operator.xor, result)
        # print(result)
        # decrypted = decrypted[:4]
        self.decrypted = (float(decrypted)) if self.deci else int(decrypted)
        return self.decrypted
        # print(self.decrypted)


    def shuffle(self, arr):
        n = len(arr) - 1
        while n > 0:
            random_index = random.randint(0, n)
            arr[n], arr[random_index] = arr[random_index], arr[n]
            n -= 1
        return arr
    
    def encrypt(self, li, mod=1):
        if isinstance(li, np.ndarray):
            encrypted = []
            for ele in li:
                encrypted.append(self.encrypt_numbers(ele, mod=mod))
            return encrypted
        elif(isinstance(li, list)):
            encrypted = []
            for ele in li:
                encrypted.append(self.encrypt_numbers(ele, mod=mod))
            return encrypted
        else:
            return self.encrypt_numbers(li, mod=mod)
    
    def decrypt(self, li):
        if isinstance(li, list):
            decrypted = []
            for ele in li:
                decrypted.append(self.decrypt_numbers(ele))
            return decrypted
        else:
            return self.decrypt_numbers(li)

    def evaluate(self, expression, values, cal="as"):
        enc = values['enc']
        exp_values = {}
        for key, value in enc.items():
            exp_values[key] = self.decrypt(value)
        # print(exp_values)
        values['enc'] = exp_values
        flattened_values = {f"{inner_key}": inner_value for outer_key, inner_dict in values.items() for inner_key, inner_value in inner_dict.items()}
        # pred = np.dot(flattened_values['X'], flattened_values['weights']) + flattened_values['bias']
        # print(pred)
        #  print(flattened_values)
        # print(expression)
        # print(flattened_values)
        if cal == 'norm':

            value = flattened_values
        # if expression == "1/(1+np.exp(-x))":
        #     return list(1/(1+np.exp(-flattened_values['x'])))
        # else:
        # print(flattened_values['weights'], flattened_values['dw'])
            result =  eval(expression, {'value' : value})
            # print(result)
            return self.encrypt(result)
        else:
            result =  eval(expression, flattened_values)
            # print(result)
            return self.encrypt(result)
        
    
    def split_chunks(self, X, y, peers=1):
        chunk_size = len(X) // peers
        
        x_chunks = [X[i:i+chunk_size] for i in range(0, len(X), chunk_size)]
        y_chunks = [y[i:i+chunk_size] for i in range(0, len(y), chunk_size)]

        mod = self.shuffle([i for i in range(1, peers + 1)])
        peer_data = []
        for i in range(peers):
            data = {}
            data['mod'] = mod[i]
            data['X'] = x_chunks[i]
            data['y'] = y_chunks[i]
            x_column = data['X'][:, 3]

            

            new_values = 2 + self.prime * x_column

            data['X'][:, 3] = new_values
            # result = (data['X'][:, 3]) & self.prime
            # result = 0
            # for i in range(1, len(result)):
            #     result += result[i]
            data['mask'] = (data['X'][:, 3]).mean()
            peer_data.append(data)
        return peer_data
    
    def build_web(self, infile, outfile, peers=5):
        print(len(infile), len(outfile))
        for i in range(peers):
            print("Peer " + str(i + 1))
            print(infile[i]['mod'], " : ", outfile[i]['accuracy'])
            print(infile[i]['mask'], " : ", outfile[i]['mask'])
            print("Checking mod:")
            mod = outfile[i]['accuracy']
            mod = self.decrypt(mod)
            print("Decrypted mod values : ", self.value)
            result = [num % self.prime for num in self.value]
            self.value = []
            result = reduce(operator.xor, result)
            if(str(infile[i]['mod']) == str(result)):
                print("Checking validity Success")
            else:
                print("Some of the data manipulated. Stop training!. Notified by network")
            
        # print(re)
con = Consensus()

n = -21.1112334324
con.encrypt_numbers(n, mod = 5)
print(con.encrypted)
con.decrypt_numbers(con.encrypted)
print(con.decrypted)
print(n == con.decrypted)

n = 123 * 125
print("Before Encryption : ", n)
print("After Encrytpion : ", con.decrypt(con.encrypt(123)) * con.decrypt(con.encrypt(125)))