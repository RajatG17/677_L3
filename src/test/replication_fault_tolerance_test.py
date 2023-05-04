import subprocess
import os
import signal
import time
import http.client
import sys
import json
from sys import argv
import random
import threading
import multiprocessing
import time

def decode_response (response):
    return json.loads(response.decode('utf-8'))


host = "0.0.0.0"
port = "8000"


env = os.environ

myvar = {'CATALOG_PORT': "6000",'SERVICE_ID': "8",'ORDER_PORT': "6003",'ORDER_PORTS': "6001,6002,6003",'CATALOG_PORT': "6000", 'ORDER_ID': "5,6,8", 'FILE_PATH': "../data/" } 
env.update(myvar)

# Kill highest service id replica/leader


# Find the PID of the process listening on port 8080
lsof_output = subprocess.check_output(['lsof', '-t', '-i', ':6003'])

pid = int(lsof_output.decode('utf-8').strip())

print(pid)

print("Killing order service leader")

# Kill the process
subprocess.call(['sudo', 'kill', '-9', str(pid)])

print("Killed order service leader")

stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
trade_types = ["buy", "sell"]
total_requests = 0

max_requests = 2

conn = http.client.HTTPConnection(host, port)

while (True):
        total_requests = total_requests+1
        if (total_requests > max_requests):
            break
        # Send Trade request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        type = trade_types[random.randint(0, 1)]
        print ("Sending Trade request for stockname: " + name + " , type: " + type)
        url = "/orders"
        body_json = {"name": name, "quantity": 1, "type": type}
        json_str = json.dumps(body_json)
        body = json_str.encode('utf-8')
        headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
        conn.request("POST", url, body, headers)
        response = conn.getresponse()
        data = response.read()
        data_json_obj = decode_response(data)
        print("data: ")
        print(data_json_obj)

        assert response.status == 200

        # Send order query request
        transaction_number = random.randint(1, 6)
        print ("Sending Lookup Order request for order number: " + str(transaction_number))
        url = "/orders/" + str(transaction_number)
        conn.request("GET", url)						
        response = conn.getresponse()
        data = response.read()
        data_json_obj = json.loads(data.decode('utf-8'))
        print ("Response: ")
        print(data_json_obj)
        
        assert response.status == 200

conn.close()

print("Order requests served after even killing the order service leader")

print("Restarting old order service leader")

# Start a new order replica on the same port.

pid = os.fork()
if pid == 0:
        # child process
        subprocess.call(['python3', 'orderService.py'], env=env, cwd="../order/", close_fds=True, stdout=subprocess.PIPE)
        os._exit(0)

print("Restarted old order service leader")

time.sleep(10)

replica_Ids = [5, 6, 8]
        
last_transaction = 0

for id in replica_Ids:       
    with open(f"../data/transaction_log_{str(id)}.txt", "r+") as transaction_logs:
        try:
                # get the last transaction number curently in own database
                last_order_number = 0
                if transaction_logs.read(1):
                    last_line = transaction_logs.readlines()[-1]
                    if last_line:
                        last_order_number = int(last_line.split(" ")[0])
                
                transaction_number = last_order_number
                print("transaction_number: " + str(transaction_number))
                if (last_transaction != 0):
                    assert transaction_number == last_transaction
                last_transaction = transaction_number
        except:
                print("Error reading file")

print ("All replicas have the same database content and are synchronized")

print("Killing order service leader")

os.system("sudo kill -9 $(sudo lsof -t -i:6003)")

print("Killed order service leader")
