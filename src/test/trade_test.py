import sys
import json
from sys import argv
import random
import time
import requests

def decode_response(response):
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

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]

    tot_time = 0

    with requests.Session() as session:
        for i in range(200):
            # Test for  Trade request
            name = stock_names[random.randint(0, len(stock_names)-1)]
            type = trade_types[random.randint(0, 1)]
            # print ("Sending Trade request for stockname: " + name + " , type: " + type)
            body_json = {"name": name, "quantity": 1, "type": type}
            json_str = json.dumps(body_json)
            body = json_str.encode('utf-8')
            headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
            url = "http://127.0.0.1:8000/orders/"
            start = time.time()
            response = session.post(url, data=body, headers=headers)
            response_time = time.time() - start
            # print("Response received: " )
            # print(response)
            tot_time += response_time

    # calculate average trade time
    avg_time = tot_time/200

    print(f"Average trade time: {avg_time*1000}ms")
