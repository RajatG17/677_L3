import sys
import json
from sys import argv
import random
import http.client
import time

host = "0.0.0.0"
port = "8000"

def decode_response (response):
	return json.loads(response.decode('utf-8'))


def test_time_lookup():
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]

    tot_time = 0
    
    for i in range(0, 200):
        # Send Lookup request
        name = stock_names[random.randint(0, 3)]
        print ("Sending Lookup request..")
        url = "/stocks/" + name
        start = time.time()
        conn.request("GET", url)						
        response = conn.getresponse()
        request_time = time.time() - start
        data = response.read()
        print(response.status, response.reason, response.version)
        data_json_obj = decode_response(data)
        print ("data: ")
        tot_time += request_time
    
    avg_time = tot_time/200

    print(f"Average lookup time : {avg_time*1000}ms")     
    assert response.status == 200

    conn.close()

if __name__ == "__main__":
    if (len(argv) >= 2 and len(argv) <= 4):
        if (len(argv) == 2):
            host = '127.0.0.1'
            port = float(argv[1])
        elif (len(argv) == 3):
            host = argv[1]
            port = int(argv[2])
        else:
            host = argv[1]
            port = int(argv[2])

    conn = http.client.HTTPConnection(host, port)	
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]

    tot_time = 0
    
    for i in range(0, 200):
        # Send Lookup request
        name = stock_names[random.randint(0, 3)]
        print ("Sending Lookup request..")
        url = "/stocks/" + name
        start = time.time()
        conn.request("GET", url)						
        response = conn.getresponse()
        request_time = time.time() - start
        data = response.read()
        print(response.status, response.reason, response.version)
        data_json_obj = decode_response(data)
        print ("data: ")
        tot_time += request_time
    
    avg_time = tot_time/200

    print(f"Average lookup time : {avg_time*1000}ms")   
  
    conn.close()	
