import time

import requests
from getpass import getpass
import sys
import json
from sys import argv
import random

if __name__ == "__main__":
    if (len(argv) >= 2 and len(argv) <= 4):
        if (len(argv) == 2):
            host = '127.0.0.1'
            port = 4000
            p = float(argv[1])
        elif (len(argv) == 3):
            host = '127.0.0.1'
            port = int(argv[1])
            p = float(argv[2])
        else:
            host = argv[1]
            port = int(argv[2])
            p = float(argv[3])

client_orders = []
max_requests = 20
# By using a context manager, you can ensure the resources used by
# the session will be released after use
with requests.Session() as session:
    # session.auth = ('username', getpass())

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo", "InvalidStockName"]
    trade_types = ["buy", "sell"]
    requests = 0
    while (True):
        requests = requests+1
        if (requests > max_requests):
            break
        # Send Lookup request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        print ("Sending Lookup request for stockname: " + name)
        #url = "/stockss/" + name
        url = "http://127.0.0.1:8000/stocks/" + name
        response = session.get(url)

        # print(response.headers)
        print(response.json())
        data_json_obj = response.json()
        if data_json_obj.get("data", 0):
            # If the lookup was succesful and client received JSON reply with top-level data object
            stock_quantity = int(data_json_obj['data']['quantity'])
            print ("Stock Quantity: " + str(stock_quantity))
        else:
            # If the lookup failed, set the "stock_quantity" as 0, so that trade request is not sent for this failed lookup
            stock_quantity = 0
        prob = random.random()
        if (stock_quantity > 0 and prob <= p):
            # Send Trade request
            name = stock_names[random.randint(0, len(stock_names)-2)]
            type = trade_types[random.randint(0, 1)]
            print ("Sending Trade request for stockname: " + name + " , type: " + type)
            body_json = {"name": name, "quantity": 1, "type": type}
            json_str = json.dumps(body_json)
            body = json_str.encode('utf-8')
            headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
            url = "http://127.0.0.1:8000/orders/"
            response = session.post(url, data=body, headers=headers)
            print(response.json())
            response = response.json()
            if response.get("data", 0):
                transaction_num = response['data']['transaction_number']
                client_orders.append({"transaction_number": transaction_num, "name": name, "quantity": 1, "type": type})

        time.sleep(5)

print("len(client_orders): " + str(len(client_orders)))
for client_order in client_orders:
    transaction_number = client_order['transaction_number']
    name = client_order['name']
    quantity = client_order['quantity']
    type = client_order['type']
    # print(f"transaction_number: {transaction_number}, name: {name}, quantity: {quantity}, type: {type}")
    # Send Lookup Order request
    print ("Sending Lookup Order request for ordernumber: " + str(transaction_number))
    url = "http://127.0.0.1:8000/orders/" + str(transaction_number)
    response = session.get(url)
    print(response.json()) 
    response = response.json()
    is_valid = False
    if (response.get("data", 0)):
        if (transaction_number == response['data']['number'] and name == response['data']['name'] and quantity == response['data']['quantity'] and type == response['data']['type']):
            is_valid = True
    if (not is_valid):
        print ("Incorrect Lookup Order response received for transaction_number: " + str(transaction_number))
    else:
        print ("Correct Lookup Order response received for transaction_number: " + str(transaction_number))    
