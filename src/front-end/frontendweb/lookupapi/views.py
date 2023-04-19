from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
import grpc
import sys
sys.path.append("../..")

from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2

# Create your views here.

# Get client IP Address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# create channel for communicating with catalog service
try:
    catalog_host = os.getenv("CATALOG_HOST", "catalog")
    catalog_port = int(os.getenv("CATALOG_PORT", 6000))
    print ("Connecting to catalog service at host:" + catalog_host + " ,port: " + str(catalog_port))
    catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
except:
    print("Error establishing a channel with catalog service")

# create channel for communicating with order service
try:
    order_host = os.getenv("ORDER_HOST", "order")
    order_port = int(os.getenv("ORDER_PORT", 6001))
    print ("Connecting to order service at host:" + order_host + " ,port: " + str(order_port))
    order_channel = grpc.insecure_channel(f"{order_host}:{order_port}")
except:
    print("Error establishing a channel with order service")

# Method to encode a JSON string into bytes
def convert_json_string(json_str):
    response = json_str.encode('utf-8')
    return response

# Method to write and send response and HTTP headers
def create_and_send_response(code, content_type, content_length, response):
    response = HttpResponse(status=code, content=response, headers={"Content-Type": content_type, "Content-Length": content_length}) 
    return response

# Method for GET request: GET /stocks/<stock_name>
def getstocks(request, stockname):
    get_path = str(request.path)
    parsed_path = get_path.split("/")

    
    print ("Client IP: " + get_client_ip(request))

    if request.method != "GET" or (len(parsed_path) != 3 or parsed_path[0] != "" or parsed_path[1] != "stocks"):
        json_str = json.dumps({"error": {"code": 400, "message": "Invalid GET request/URL"}})
        response = convert_json_string(json_str)
        return create_and_send_response(400, "application/json", str(len(response)), response)

    # Obtain the stockname from the parsed URL/path
    stock_name = parsed_path[2]    

    # make lookup call to catalog service
    catalogService = pb2_grpc.CatalogStub(catalog_channel)
    result = catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
    print("Response received from the back-end Catalog service:")
    print(result)

    if result.error == pb2.NO_ERROR:
        # Return JSON reply with a top-level data object
        stockname = result.stockname
        price = result.price
        quantity = result.quantity
        json_str = json.dumps({"data": {"name": stockname, "price": price, "quantity": quantity}})
        response = convert_json_string(json_str)
        return create_and_send_response(200, "application/json", str(len(response)), response)
    elif result.error == pb2.INVALID_STOCKNAME:
        # If the GET request was not successful due to invalid stockname, return JSON reply with a top-level error object
        json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
        response = convert_json_string(json_str)
        return create_and_send_response(404, "application/json", str(len(response)), response)
    else:
        # If the GET request was not successful due to any other error, return JSON reply with a top-level error object
        json_str = json.dumps({"error": {"code": 500, "message": "Lookup Failed due to internal error"}})
        response = convert_json_string(json_str)
        return create_and_send_response(500, "application/json", str(len(response)), response)

# Method for GET request: GET/orders/<order_number>
def getorders(request, ordernumber):
    get_path = str(request.path)
    parsed_path = get_path.split("/")

    print("parsed_path: " + str(parsed_path))
    
    print ("Client IP: " + get_client_ip(request))

    if request.method == "GET":
        if (len(parsed_path) != 3 or parsed_path[0] != "" or parsed_path[1] != "orders"):
            json_str = json.dumps({"error": {"code": 400, "message": "Invalid GET request/URL"}})
            response = convert_json_string(json_str)
            return create_and_send_response(400, "application/json", str(len(response)), response)

        ordernumber = int(parsed_path[2])
        
        # make lookup call to order service
        orderService = pb2_grpc.OrderStub(order_channel)
        result = orderService.lookupOrder(pb2.lookupOrderRequestMessage(order_number=ordernumber))
        print("Response received from the back-end Order service:")
        print(result)   

        if result.error == pb2.NO_ERROR:
            # Return JSON reply with a top-level data object
            number = result.number
            name = result.name
            type = result.type
            quantity = result.quantity
            json_str = json.dumps({"data": {"number": number, "name": name, "type": type, "quantity": quantity}})
            response = convert_json_string(json_str)
            return create_and_send_response(200, "application/json", str(len(response)), response)
        elif result.error == pb2.INVALID_ORDERNUMBER:
            # If the GET request was not successful due to invalid ordernumber, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 404, "message": "order number not found"}})
            response = convert_json_string(json_str)
            return create_and_send_response(404, "application/json", str(len(response)), response)
        else:
            # If the GET request was not successful due to any other error, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 500, "message": "Lookup Failed due to internal error"}})
            response = convert_json_string(json_str)
            return create_and_send_response(500, "application/json", str(len(response)), response) 

# Method for POST request: POST /orders
@csrf_exempt
def postorders(request):
    get_path = str(request.path)
    parsed_path = get_path.split("/")

    print ("Client IP: " + get_client_ip(request))

    if request.method == "POST":
        if (len(parsed_path) != 3 or parsed_path[0] != "" or parsed_path[1] != "orders" or parsed_path[2] != ""):
            json_str = json.dumps({"error": {"code": 400, "message": "Invalid POST request/URL"}})
            response = convert_json_string(json_str)
            return create_and_send_response(400, "application/json", str(len(response)), response)

        # Obtain the stockname from the parsed URL/path
        request_body = json.loads(request.body)
        stockname = request_body["name"]
        quantity = request_body["quantity"]
        type = request_body["type"]

        # make trade call to order service
        orderService = pb2_grpc.OrderStub(order_channel)
        result = orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=type))
        print("Response received from the back-end Order service:")
        print(result)

        # If the trade request was succesful from the order service, send the JSON object containing the Transaction number
        if result.error == pb2.NO_ERROR:
            # Return JSON reply with a top-level data object
            transaction_number = result.transaction_number
            json_str = json.dumps({"data": {"transaction_number": transaction_number}})
            response = convert_json_string(json_str)
            return create_and_send_response(200, "application/json", str(len(response)), response)
        elif result.error == pb2.INVALID_REQUEST:
            # If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 400, "message": "Order type is invalid, only buy/sell are accepted"}})
            response = convert_json_string(json_str)
            return create_and_send_response(400, "application/json", str(len(response)), response)
        elif result.error == pb2.INVALID_STOCKNAME:
            # If the POST request was not successful due to invalid stockname, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
            response = convert_json_string(json_str)
            return create_and_send_response(404, "application/json", str(len(response)), response)
        elif result.error == pb2.INSUFFICIENT_QUANTITY:
            json_str = json.dumps({"error": {"code": 400, "message": "Available quantity to buy is less than requested quantity"}})
            response = convert_json_string(json_str)
            return create_and_send_response(400, "application/json", str(len(response)), response)
        else:
            # If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 500, "message": "Stock could not be traded due to internal error"}})
            response = convert_json_string(json_str)
            return create_and_send_response(500, "application/json", str(len(response)), response)
 
    else:   
        json_str = json.dumps({"error": {"code": 400, "message": "Invalid request/URL"}})
        response = convert_json_string(json_str)
        return create_and_send_response(400, "application/json", str(len(response)), response)
