
import sys
import json
from sys import argv
import random
import http.client
import time


host = "0.0.0.0"
port = "8000"

def decode_response(response):
	return json.loads(response.decode('utf-8'))


if __name__ == "__main__":
    if (len(argv) >= 2 and len(argv) <= 4):
        if (len(argv) == 2):
            host = '127.0.0.1'
            port = int(argv[1])
        elif (len(argv) == 3):
            host = argv[1]
            port = int(argv[2])
        else:
            host = argv[1]
            port = int(argv[2])
           

    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]

    tot_time = 0

    for i in range(200):
        # Test for  Trade request
        name = stock_names[random.randint(0, 3)]
        print("Sending Trade request..")
        url = "/orders"
        type = trade_types[random.randint(0, 1)]
        body_json = {"name": name, "quantity": 1, "type": type}
        json_str = json.dumps(body_json)
        body = json_str.encode('utf-8')
        headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
        start = time.time()
        conn.request("POST", url, body, headers)
        response = conn.getresponse()
        data = response.read()
        response_time = time.time() - start
        tot_time += response_time
    # calculate average trade time
    avg_time = tot_time/200

    print(f"Average trade time: {avg_time*1000}ms")

    # Close the HTTP connection
    conn.close()
