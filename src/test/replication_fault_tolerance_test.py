import subprocess
import os
import signal
import time
import http.client
import sys
import json
from sys import argv
import random


def decode_response (response):
    return json.loads(response.decode('utf-8'))


host = "0.0.0.0"
port = "8000"


env = os.environ

myvar = {'CATALOG_PORT': "6000",'SERVICE_ID': "8",'ORDER_PORT': "6003",'ORDER_PORTS': "6001,6002,6003",'CATALOG_PORT': "6000", 'ORDER_ID': "5,6,8", 'FILE_PATH': "../data/" } 
env.update(myvar)

# Kill highest service id replica/leader
#os.system("sudo kill -9 $(sudo lsof -t -i:6003)")

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

conn.close()

print("Order requests served after even killing the order service leader")

# Start a new order replica on the same port.

subprocess.Popen(["python3", "orderService.py"], env=env, close_fds=True, cwd="../order/",stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

time.sleep(5)

os.system("sudo kill -9 $(sudo lsof -t -i:6003)")
