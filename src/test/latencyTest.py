import time

import requests
from getpass import getpass
import sys
import json
from sys import argv
import random


def runLatencyTest(host, port, p):
   
    print("Probability p: " + str(p))
    client_orders = []
    max_requests = 20
    # By using a context manager, you can ensure the resources used by
    # the session will be released after use
    with requests.Session() as session:
        # session.auth = ('username', getpass())

        stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo", "InvalidStockName"]
        trade_types = ["buy", "sell"]
        total_requests = 0

        tot_stocklookup_time = 0
        tot_orderlookup_time = 0
        tot_trade_time = 0

        tot_stocklookup_req = 0
        tot_orderlookup_req = 0
        tot_trade_req = 0
 
        while (True):
            total_requests = total_requests+1
            if (total_requests > max_requests):
                break
            # Send Lookup request
            name = stock_names[random.randint(0, len(stock_names)-1)]
            # print ("Sending Lookup request for stockname: " + name)
            url = f"http://{host}:{port}/stocks/" + name
            # print("url: " + url)

            start_stocklookup = time.time()
            response = session.get(url)
            request_stocklookup_time = time.time() - start_stocklookup
            tot_stocklookup_time+=request_stocklookup_time
            tot_stocklookup_req+=1

            # print(response.headers)
            # print("Response received:")
            # print(response.json())
            data_json_obj = response.json()
            if data_json_obj.get("data", 0):
                # If the lookup was succesful and client received JSON reply with top-level data object
                stock_quantity = int(data_json_obj['data']['quantity'])
                #print ("Stock Quantity: " + str(stock_quantity))
            else:
                # If the lookup failed, set the "stock_quantity" as 0, so that trade request is not sent for this failed lookup
                stock_quantity = 0
            prob = random.random()
            if (stock_quantity > 0 and prob <= p):
                # Send Trade request
                name = stock_names[random.randint(0, len(stock_names)-2)]
                type = trade_types[random.randint(0, 1)]
                # print ("Sending Trade request for stockname: " + name + " , type: " + type)
                body_json = {"name": name, "quantity": 1, "type": type}
                json_str = json.dumps(body_json)
                body = json_str.encode('utf-8')
                headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
                url = f"http://{host}:{port}/orders/"

                start_trade = time.time()
                response = session.post(url, data=body, headers=headers)
                request_trade_time = time.time() - start_trade
                tot_trade_time+=request_trade_time
                tot_trade_req+=1

                # print("Response received:")
                # print(response.json())
                response = response.json()
                if response.get("data", 0):
                    transaction_num = response['data']['transaction_number']
                    client_orders.append({"transaction_number": transaction_num, "name": name, "quantity": 1, "type": type})

            time.sleep(5)

    # print("len(client_orders): " + str(len(client_orders)))
    for client_order in client_orders:
        transaction_number = client_order['transaction_number']
        name = client_order['name']
        quantity = client_order['quantity']
        type = client_order['type']
        # print(f"transaction_number: {transaction_number}, name: {name}, quantity: {quantity}, type: {type}")
        # Send Lookup Order request
        # print ("Sending Lookup Order request for ordernumber: " + str(transaction_number))
        url = f"http://{host}:{port}/orders/" + str(transaction_number)
    
        start_orderlookup = time.time()
        response = session.get(url)
        request_orderlookup_time = time.time() - start_orderlookup
        tot_orderlookup_time+=request_orderlookup_time
        tot_orderlookup_req+=1

        # print("Response received:")
        # print(response.json()) 
        response = response.json()
        is_valid = False
        if (response.get("data", 0)):
            if (transaction_number == response['data']['number'] and name == response['data']['name'] and quantity == response['data']['quantity'] and type == response['data']['type']):
                is_valid = True
        if (not is_valid):
            print ("Incorrect Lookup Order response received for transaction_number: " + str(transaction_number))
        #else:
            #print ("Correct Lookup Order response received for transaction_number: " + str(transaction_number))   

    if (tot_stocklookup_req != 0):
        avg_stocklookup_time = tot_stocklookup_time/tot_stocklookup_req
    else:
        avg_stocklookup_time = 0

    print(f"Total stock lookup requests: {tot_stocklookup_req}")
    print(f"Average stock lookup time : {avg_stocklookup_time*1000}ms")

    if (tot_trade_req != 0):
        avg_trade_time = tot_trade_time/tot_trade_req
    else:
        avg_trade_time = 0

    print(f"Total trade requests: {tot_trade_req}")
    print(f"Average trade time : {avg_trade_time*1000}ms")

    if (tot_orderlookup_req != 0):
        avg_orderlookup_time = tot_orderlookup_time/tot_orderlookup_req
    else:
        avg_orderlookup_time = 0

    print(f"Total order lookup requests: {tot_orderlookup_req}")
    print(f"Average order lookup time: {avg_orderlookup_time*1000}ms")

if __name__ == "__main__":
    if (len(argv) == 4):
        host = argv[1]
        port = int(argv[2])
        p = float(argv[3])
        runLatencyTest(host, port, p)
    elif (len(argv) == 3):
        host = argv[1]
        port = int(argv[2])
        #p_values = [0, 0.2, 0.4, 0.6, 0.8, 1]
        p_values = [1, 0.8, 0.6, 0.4, 0.2, 0]
        for i in range(0, len(p_values)):
            p = p_values[i]
            runLatencyTest(host, port, p)
    elif (len(argv) == 2):
        host = "127.0.0.1"
        port = 8000
        p = float(argv[1])
        runLatencyTest(host, port, p)
    else:
        host = "127.0.0.1"
        port = 8000
        #p_values = [0, 0.2, 0.4, 0.6, 0.8, 1]
        p_values = [1, 0.8, 0.6, 0.4, 0.2, 0]
        for i in range(0, len(p_values)):
            p = p_values[i]
            runLatencyTest(host, port, p) 
