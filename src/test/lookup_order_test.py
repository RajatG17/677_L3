import sys
import json
from sys import argv
import random
import time
import requests

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
        port = 6000

    tot_time = 0

    with requests.Session() as session:
        for i in range(0, 200):
            # Send Lookup Order request
            transaction_number = random.randint(1, 6)
            # print ("Sending Lookup Order request for order number: " + str(transaction_number))
            url = "http://127.0.0.1:8000/orders/" + str(transaction_number)
            start = time.time()
            response = session.get(url)
            request_time = time.time() - start
            data_json_obj = response.json()
            # print("Response received: " )
            # print(response.json())

            assert response.status_code == 200
            tot_time += request_time

    avg_time = tot_time/200

    print(f"Average lookup time : {avg_time*1000}ms")
