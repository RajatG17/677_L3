import sys
import json
from sys import argv
import random
import requests

def decode_response (response):
	return json.loads(response.decode('utf-8'))


def test_valid_lookup_front_end(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]

    with requests.Session() as session:    
        # Send Lookup request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        print ("Sending Lookup request for stockname: " + name)
        url = "http://127.0.0.1:8000/stocks/" + name
        response = session.get(url)
        
        data_json_obj = response.json()
        print("Response received: " )
        print(response.json())
       
        if data_json_obj.get("data", 0):
            # If the lookup was succesful and client received JSON reply with top-level data object
            stock_quantity = int(data_json_obj['data']['quantity'])
            print ("Lookup successful as expected")
        else:
            # If the lookup failed, set the "stock_quantity" as 0, so that trade request is not sent for this failed lookup
            stock_quantity = 0
            print ("Lookup failed")

        assert response.status_code == 200

def test_invalid_trade_front_end(host, port):

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buye", "seld"]

    with requests.Session() as session:
        # Send Trade request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        type = trade_types[random.randint(0, 1)]
        print ("Sending Invalid Trade request for stockname: " + name + " , type: " + type)
        body_json = {"name": name, "quantity": 1, "type": type}
        json_str = json.dumps(body_json)
        body = json_str.encode('utf-8')
        headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
        url = "http://127.0.0.1:8000/orders/"
        response = session.post(url, data=body, headers=headers)
        print("Response received: " )
        print(response)
        data_json_obj = response.json()
        if data_json_obj.get("data", 0):
            print ("Trade successful")
        else:
            print ("Trade failed as expected")

        assert response.status_code == 400

def test_valid_trade_front_end(host, port):

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]

    with requests.Session() as session:
        # Send Trade request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        type = trade_types[random.randint(0, 1)]
        print ("Sending Trade request for stockname: " + name + " , type: " + type)
        body_json = {"name": name, "quantity": 1, "type": type}
        json_str = json.dumps(body_json)
        body = json_str.encode('utf-8')
        headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
        url = "http://127.0.0.1:8000/orders/"
        response = session.post(url, data=body, headers=headers)
        print("Response received: " )
        print(response)
        data_json_obj = response.json()
        if data_json_obj.get("data", 0):
            print ("Trade successful as expected")
        else:
            print ("Trade failed")

        assert response.status_code == 200

def test_invalid_lookup_front_end(host, port):

    stock_names = ["Game", "Fish", "Menhir", "Boar"]

    with requests.Session() as session:
        # Send Lookup request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        print ("Sending Invalid Lookup request for stockname: " + name)
        url = "http://127.0.0.1:8000/stocks/" + name
        response = session.get(url)

        data_json_obj = response.json()
        print("Response received: " )
        print(response.json())

        if data_json_obj.get("data", 0):
            # If the lookup was succesful and client received JSON reply with top-level data object
            stock_quantity = int(data_json_obj['data']['quantity'])
            print ("Lookup successful")
        else:
            # If the lookup failed, set the "stock_quantity" as 0, so that trade request is not sent for this failed lookup
            stock_quantity = 0
            print ("Lookup failed as expected")

        assert response.status_code == 404

def test_invalid_url_front_end(host, port):

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]

    with requests.Session() as session:
        # Send Trade request
        name = stock_names[random.randint(0, len(stock_names)-1)]
        type = trade_types[random.randint(0, 1)]
        print ("Sending Trade request for stockname: " + name + " , type: " + type)
        body_json = {"name": name, "quantity": 1, "type": type}
        json_str = json.dumps(body_json)
        body = json_str.encode('utf-8')
        headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
        url = "http://127.0.0.1:8000/order/"
        response = session.post(url, data=body, headers=headers)
        print("Response received from invalid URL: " )
        print(response)

        assert response.status_code == 404
        print ("Trade failed as expected")

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

    test_valid_lookup_front_end(host, port)

    test_valid_trade_front_end(host, port)

    test_invalid_trade_front_end(host, port)

    test_invalid_lookup_front_end(host, port)

    test_invalid_url_front_end(host, port)

