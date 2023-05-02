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

if __name__ == "__main__":
    if (len(argv) == 3):
        host = argv[1]
        port = int(argv[2])
    elif (len(argv) == 2):
        host = "0.0.0.0"
        port = int(argv[1])
    else:
        host = "0.0.0.0"
        port = 8000

    conn = http.client.HTTPConnection(host, port)

    tot_time = 0

    for i in range(0, 200):
        # Send Lookup Order request
        transaction_number = random.randint(1, 6)
        # print ("Sending Lookup Order request for order number: " + str(transaction_number))
        url = "/orders/" + str(transaction_number)
        start = time.time()
        conn.request("GET", url)						
        response = conn.getresponse()
        request_time = time.time() - start
        data = response.read()
        print(response.status, response.reason, response.version)
        data_json_obj = decode_response(data)
        print ("data: ")
        tot_time += request_time

        assert response.status == 200
        tot_time += request_time

    avg_time = tot_time/200

    print(f"Average lookup time : {avg_time*1000}ms")
