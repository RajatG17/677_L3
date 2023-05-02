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

def test_cache_invalidation():
    conn = http.client.HTTPConnection(host, port)

    # Send Lookup request
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    trade_types = ["buy", "sell"]

    name = stock_names[random.randint(0, 3)]
    print ("Sending Lookup request for stockname: " + str(name))
    url = "/stocks/" + name
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()

    assert response.status == 200

    # Lookup cache to check if the stockname is present in cache
 
    print ("Sending Cache Lookup request for stockname: " + str(name))
    url = "/stocksCacheLookup/" + name
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()

    assert response.status == 200

    # Send POST request to invalidate cache
    print ("Sending Trade request for stockname: " + name)
    url = "/orders"
    type = trade_types[random.randint(0, 1)]
    body_json = {"name": name, "quantity": 1, "type": type}
    json_str = json.dumps(body_json)
    body = json_str.encode('utf-8')
    headers = {"Content-type": "application/json", "Content-Length": str(len(body))}
    conn.request("POST", url, body, headers)
    response = conn.getresponse()
    data = response.read()
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)

    assert response.status == 200
 
    # Lookup cache to check if the stockname is present in cache

    print ("Sending Cache Lookup request for stockname after invalidation: " + str(name))
    url = "/stocksCacheLookup/" + name
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)

    assert response.status == 404
    
    conn.close()

def test_valid_cache_lookup():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]

    # Send Lookup request
    name = stock_names[random.randint(0, 3)]
    print ("Sending Lookup request for stockname: " + str(name))
    url = "/stocks/" + name
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)

    assert response.status == 200

    # Lookup cache to check if the stockname is present in cache

    print ("Sending Cache Lookup request for stockname: " + str(name))
    url = "/stocksCacheLookup/" + name
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    print("response.status, response.reason, response.version : ")
    print(response.status, response.reason, response.version)
    data_json_obj = decode_response(data)
    print ("data: ")
    print(data_json_obj)
   
    assert response.status == 200
 
    conn.close()

def test_invalid_cache_lookup():
    conn = http.client.HTTPConnection(host, port)

    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo", "Wheely", "ConStock"]

    # Send 6 Lookup requests to fill the cache of default size 5
    for i in range(6):
        name = stock_names[i]
        print ("Sending Lookup request for stockname: " + str(name))
        url = "/stocks/" + name
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        #print("response.status, response.reason, response.version : ")
        #print(response.status, response.reason, response.version)
        #data_json_obj = decode_response(data)
        #print ("data: ")
        #print(data_json_obj)

        assert response.status == 200
       
        # Lookup cache to check if the stockname is present in cache

        #print ("Sending Cache Lookup request for stockname: " + str(name))
        url = "/stocksCacheLookup/" + name
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
 
        assert response.status == 200

    # Lookup cache to check if the first stockname is present in cache

    for i in range(6):
        name = stock_names[i]
        print ("Sending Cache Lookup request for stockname: " + str(name))
        url = "/stocksCacheLookup/" + name
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        #print("response.status, response.reason, response.version : ")
        #print(response.status, response.reason, response.version)
        #data_json_obj = decode_response(data)
        #print ("data: ")
        #print(data_json_obj)

        if (i==0):
            # Assert first stockname is evicted in the LRU cache 
             assert response.status == 404
        else:
             assert response.status == 200

    conn.close()

if __name__ == "__main__":
    if (len(argv) >= 2 and len(argv) < 4):
        if (len(argv) == 2):
            host = '0.0.0.0'
            port = float(argv[1])
        elif (len(argv) == 3):
            host = argv[1]
            port = int(argv[2])

    test_valid_cache_lookup()
    test_invalid_cache_lookup()
    test_cache_invalidation()
