import sys
import json
from sys import argv
import random
import http.client

host = "0.0.0.0"
port = "8000"

def decode_response (response):
	return json.loads(response.decode('utf-8'))


def test_valid_lookup_front_end():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    
    # Send Lookup request
    name = stock_names[random.randint(0, 3)]
    print ("Sending Lookup request..")
    url = "/stocks/" + name
    conn.request("GET", url)						
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)
    if data_json_obj.get("data", 0):
        stock_quantity = int(data_json_obj['data']['quantity'])
        print ("Stock Quantity: " + str(stock_quantity))
    elif data_json_obj.get("error"):
        message = data_json_obj["error"]["message"]
        print(message)

    assert response.status == 200

    conn.close()
    
def test_invalid_trade_front_end():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buye", "seld"]
    # Test for  Trade request
    name = stock_names[random.randint(0, 3)]
    print ("Sending Trade request..")
    url = "/orders"
    type = trade_types[random.randint(0, 1)]
    body_json = {"name": name, "quantity": 1, "type": type}
    json_str = json.dumps(body_json)
    body = json_str.encode('utf-8')	
    headers = {"Content-type": "application/json", "Content-Length": str(len(body))}		
    conn.request("POST", url, body, headers)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    print("data: ")
    data_json_obj = decode_response(data)
    print(data_json_obj)

    assert response.status == 400
    # Close the HTTP connection
    conn.close()

def test_valid_trade_front_end():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]
    # Test for  Trade request
    name = stock_names[random.randint(0, 3)]
    print ("Sending Trade request..")
    url = "/orders"
    type = trade_types[random.randint(0, 1)]
    body_json = {"name": name, "quantity": 1, "type": type}
    json_str = json.dumps(body_json)
    body = json_str.encode('utf-8')	
    headers = {"Content-type": "application/json", "Content-Length": str(len(body))}		
    conn.request("POST", url, body, headers)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    print("data: ")
    data_json_obj = decode_response(data)
    print(data_json_obj)

    assert response.status == 200
    # Close the HTTP connection
    conn.close()

def test_invalid_lookup_front_end():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["Game", "Fish", "Menhir", "Boar"]
    
    # Send Lookup request
    name = stock_names[random.randint(0, 3)]
    print ("Sending Invalid Lookup request..")
    url = "/stocks/" + name
    conn.request("GET", url)						
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)
    if data_json_obj.get("data", 0):
        stock_quantity = int(data_json_obj['data']['quantity'])
        print ("Stock Quantity: " + str(stock_quantity))
    assert response.status == 404, 'Should return 400'

    conn.close()

def test_invalid_url_front_end():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]
    # Test for  Trade request
    name = stock_names[random.randint(0, 3)]
    print ("Sending request via an invalid url ..")
    url = "/order"
    type = trade_types[random.randint(0, 1)]
    body_json = {"name": name, "quantity": -1, "type": type}
    json_str = json.dumps(body_json)
    body = json_str.encode('utf-8')	
    headers = {"Content-type": "application/json", "Content-Length": str(len(body))}		
    conn.request("POST", url, body, headers)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    print("data: ")
    data_json_obj = decode_response(data)
    print(data_json_obj)

    assert response.status == 400, 'Should return 400'
    # Close the HTTP connection
    conn.close()


if __name__ == "__main__":
    if (len(argv) >= 2 and len(argv) < 4):
        if (len(argv) == 2):
            host = '0.0.0.0'
            port = float(argv[1])
        elif (len(argv) == 3):
            host = argv[1]
            port = int(argv[2])

    test_valid_lookup_front_end()

    test_valid_trade_front_end()

    test_invalid_trade_front_end()

    test_invalid_lookup_front_end()

    test_invalid_url_front_end()

