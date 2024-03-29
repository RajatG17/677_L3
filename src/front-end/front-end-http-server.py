import os
import sys
sys.path.append("..")
import time
import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import grpc
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2 
from urllib.parse import urlparse
import json
from sys import argv
import threading
import os
from numpy import * 

order_Ports = list(int(x) for x in list(os.getenv("ORDER_PORTS").split(",")))
order_Hosts = list(os.getenv("ORDER_HOSTS").split(","))
order_Ids = list(int(x) for x in list(os.getenv("ORDER_ID").split(",")))
down_services = []
order_channel = None
leader_Id = -1
orderService = None

# Assign a leader when the front-end service starts
if len(order_Ids)>0:
        
        order_Hosts_copy = order_Hosts.copy()
        order_Ports_copy = order_Ports.copy()
        order_Ids_copy = order_Ids.copy()
        while len(order_Ids_copy)>0:
            max_id = max(order_Ids_copy)
            order_host, order_port = order_Hosts_copy.pop(order_Ids_copy.index(max_id)), order_Ports_copy.pop(order_Ids_copy.index(max_id))
            order_Ids_copy.remove(max_id)
            #self.order_host, self.order_port = self.order_Hosts.pop(self.order_Ids.index(max_id)), self.order_Ports.pop(self.order_Ids.index(max_id))
            # print(f"Order service leader with id {max_id} selected, proceeding to connect and notify other replicas...")
            # print ("Connecting to order service at host:" + self.order_host + " ,port: " + str(self.order_port) + " with id " + str(max_id))
            order_channel = grpc.insecure_channel(f"{order_host}:{order_port}")
            o_stb = pb2_grpc.OrderStub(order_channel)
            # check if service responsive
            try:
                result = o_stb.healthCheck(pb2.checkMessage(ping="health check"))
                if result.response:
                    result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, replica_Ids=order_Ids, replica_Ports=order_Ports, replica_Hosts=order_Hosts))
                    for id, port, host in zip(order_Ids, order_Ports, order_Hosts):
                        if id == max_id:
                            continue
                        print("Connecting to : ",id, host, port)
                        try:
                            channel = grpc.insecure_channel(f"{host}:{port}")
                            o_stb = pb2_grpc.OrderStub(channel)
                            # notify order services of elected leader
                            result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, replica_Ids=order_Ids, replica_Ports=order_Ports, replica_Hosts=order_Hosts))
                            channel.close()
                        except:
                            # if unable to establish connection, continue
                            continue
                    leader_Id = max_id
                    break
                else:
                    print("Error setting leader, retrying..")
            except:
                print("Error setting leader, retrying..")   
else:
        print("All replicas down!!")

# If no order service replicasa are up, print appropriate message
if (leader_Id == -1):
    print("All replicas down!!")

# print(f"Order service leader with id {max_id} selected, proceeding to connect and notify other replicas...")
# print ("Connecting to order service at host:" + self.order_host + " ,port: " + str(self.order_port) + " with id " + str(max_id))
       

# LRU Cache Class to store stockname lookups
class MyLRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.keys = []
        self.lock = threading.Lock()

    # Method of cache lookup	
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            self.keys.remove(key)
            self.keys.append(key)
            return self.cache[key]

    # Method for cache update		
    def put(self, key, value):
        with self.lock:
            if self.capacity == 0:
                return	
            if key in self.cache:
                self.keys.remove(key)
            elif len(self.keys) == self.capacity:
                evicted = self.keys.pop(0)
                del self.cache[evicted]
            self.cache[key] = value
            self.keys.append(key)

    # Methods for cache invalidate
    def invalidate(self, key):
        with self.lock:
            if key in self.cache:
                print("Invalidating stockname: " + key + " from cache")
                self.keys.remove(key)
                del self.cache[key]

class MyHTTPHandlerClass(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    
    def __init__(self, request, client_address, server):
        # create channel for communicating with catalog service
        try:
            catalog_host = os.getenv("CATALOG_HOST", "0.0.0.0")
            catalog_port = int(os.getenv("CATALOG_PORT", 6000))
            print ("Connecting to catalog service at host:" + catalog_host + " ,port: " + str(catalog_port))
            self.catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
            self.catalogService = pb2_grpc.CatalogStub(self.catalog_channel)
        except:
            print("Error establishing a channel with catalog service")

        # elect leader of order servies and notify to all services
        
        self.order_channel = order_channel
        self.order_Ports = order_Ports
        self.order_Hosts = order_Hosts
        self.order_Ids = order_Ids
        self.down_services = []
        self.leaderId = leader_Id
        self.order_host = order_host
        self.order_port = order_port
        
        self.orderService = pb2_grpc.OrderStub(self.order_channel)
        if self.leaderId < 0:
            print("Error connecting to all order service instances")
        # except:
        #     print("Error establishing a channel with order service")


        # create channel for communicating with order service
        super().__init__(request, client_address, server)

    def handle_one_request(self):
        super(MyHTTPHandlerClass, self).handle_one_request()
        print ("cur_thread: " + threading.current_thread().name)
        print ("client address_string: " + str(self.client_address))

    # Method to encode a JSON string into bytes 
    def convert_json_string(self, json_str):
        response = json_str.encode('utf-8')
        return response

    # Method to write and send response and HTTP headers
    def create_and_send_response(self, status_code, content_type, content_length, response):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", content_length)
        self.end_headers()
        self.wfile.write(response)

    # Method for GET request: GET /stocks/<stock_name> , GET/orders/<order_number>, GET /stocksCache/<stock_name> and GET /stocksCacheLookup/<stock_name>
    def do_GET(self):
        get_path = str(self.path)
        parsed_path = get_path.split("/")

        # Check if the URL for the GET method  is of the form: "/stocksCacheLookup/<stock_name>"
        if (len(parsed_path) == 3 and parsed_path[0] == "" and parsed_path[1] == "stocksCacheLookup"):
                    # Return JSON reply with a top-level data object if stockname is in cache, otherwise return JSON reply with a top-level error object 
                    # Obtain the stockname from the parsed URL/path "/stocks/<stock_name>"
                    stockname = str(parsed_path[2])

                    result = stocksLRUCache.get(stockname)
                    if result:
                        # Return JSON reply with a top-level data object
                        print("Stockname: " + stockname + " in cache")
                        response = self.convert_json_string(result)
                        return self.create_and_send_response(200, "application/json", str(len(response)), response) 
                    else:
                        # If the GET request was not successful as stockname is not in cache, return JSON reply with a top-level error object
                        print("Stockname: " + stockname + " not in cache")
                        json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
                        response = self.convert_json_string(json_str)
                        self.create_and_send_response(404, "application/json", str(len(response)), response)
          

        # Check if the URL for the GET method is invalid - It should be of the format : "/stocks/<stock_name>" , "/orders/<order_number>" or /stocksCache/<stock_name>
        if (len(parsed_path) != 3 or parsed_path[0] != "" or (parsed_path[1] != "stocks" and parsed_path[1] != "orders" and parsed_path[1] != "stocksCache")):
            print ("URL for HTTP GET request is invalid - It should be of the format : ") 
            print("\"/stocks/<stock_name>\" OR \"/orders/<order_number>\"")
            # If the GET request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 400, "message": "Invalid GET request/URL"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(400, "application/json", str(len(response)), response)
            return

        if (parsed_path[1] == "stocks"):
            print("Inside stocks lookup")		
            # Obtain the stockname from the parsed URL/path "/stocks/<stock_name>" 
            stockname = parsed_path[2]

            result = stocksLRUCache.get(stockname)
            if result:
                print("Stockname: " + stockname + " in cache")
                response = self.convert_json_string(result)
                return self.create_and_send_response(200, "application/json", str(len(response)), response)
    
            # make lookup call to catalog service
            print("Stockname : " + stockname + " not in cache, making lookup call to Catalog service")    
            result = self.catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
            print("Response received from the back-end Catalog service:")
            print(result)
        
            if result.error == pb2.NO_ERROR:
                # Return JSON reply with a top-level data object 
                stockname = result.stockname
                price = result.price
                quantity = result.quantity
                json_str = json.dumps({"data": {"name": stockname, "price": price, "quantity": quantity}})
                stocksLRUCache.put(stockname, json_str)
                response = self.convert_json_string(json_str)
                self.create_and_send_response(200, "application/json", str(len(response)), response)
            elif result.error == pb2.INVALID_STOCKNAME:
                # If the GET request was not successful due to invalid stockname, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
                response = self.convert_json_string(json_str)
                self.create_and_send_response(404, "application/json", str(len(response)), response)
            else:			
                # If the GET request was not successful due to any other error, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 500, "message": "Lookup Failed due to internal error"}})
                response = self.convert_json_string(json_str)
                self.create_and_send_response(500, "application/json", str(len(response)), response) 
        elif (parsed_path[1] == "orders"):
            # Obtain the order number from the parsed URL/path "/orders/<order_number>"
            order_number = int(parsed_path[2])
            
            try:
                # make lookup call to order service
                try:
                    print("Making lookup call to Order service for order number: " + str(order_number))
                    result = self.orderService.lookupOrder(pb2.lookupOrderRequestMessage(order_number=order_number))
                except:
                    # if not able to communicate with current leader, elect a new leader, and continue order lookup
                    self.leaderId = self.leader_election()
                    self.orderService = pb2_grpc.OrderStub(self.order_channel)
                    result = self.orderService.lookupOrder(pb2.lookupOrderRequestMessage(order_number=order_number))
            except:
                print("All replicas down")
                #If the GET request was not successful as all replicas are down, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 500, "message": "Order query failed as all replicas are down"}})
                response = self.convert_json_string(json_str)
                self.create_and_send_response(500, "application/json", str(len(response)), response)
                return
            
            print("Response received from the back-end Order service:")
            print(result)

            if result.error == pb2.NO_ERROR:
                # Return JSON reply with a top-level data object
                number = result.number
                name = result.name
                type = result.type
                quantity = result.quantity
                json_str = json.dumps({"data": {"number": number, "name": name, "type": type, "quantity": quantity}})
                response = self.convert_json_string(json_str)
                return self.create_and_send_response(200, "application/json", str(len(response)), response)
            elif result.error == pb2.INVALID_ORDERNUMBER:
                # If the GET request was not successful due to invalid ordernumber, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 404, "message": "order number not found"}})
                response = self.convert_json_string(json_str)
                return self.create_and_send_response(404, "application/json", str(len(response)), response)
            else:
                # If the GET request was not successful due to any other error, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 500, "message": "Lookup Failed due to internal error"}})
                response = self.convert_json_string(json_str)
                return self.create_and_send_response(500, "application/json", str(len(response)), response) 
        elif (parsed_path[1] == "stocksCache"):
            # Method for GET request: GET /stocksCache/<stock_name>
            # Obtain the stockname from the parsed URL/path
            stockname = str(parsed_path[2])
            #print("Invalidating stockname: " + stockname + " from cache")
            try:
                # Invalidate cache entry for stockname
                stocksLRUCache.invalidate(stockname)
                json_str = json.dumps({"data": {"code": 200, "message": "Cache Invalidation done"}})
                response = self.convert_json_string(json_str)
                #print("Cache invalidation done")  
                return self.create_and_send_response(200, "application/json", str(len(response)), response)
            except:
                # If cache invalidation failed, return JSON reply with a top-level error object
                json_str = json.dumps({"error": {"code": 500, "message": "Cache Invalidation Failed due to internal error"}})
                response = self.convert_json_string(json_str)
                return self.create_and_send_response(500, "application/json", str(len(response)), response)

    def do_POST(self):
        
        # Read the JSON object attached by the client to the POST request
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length).decode('utf-8'))
                
        # Check if the URL for the POST method is invalid - It should be of the format : "/orders"
        if self.path != "/orders":
            print ("URL for HTTP POST request is invalid - It should be of the format : ")
            print("\"/orders\"")
            #If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 400, "message": "Invalid POST request/URL"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(400, "application/json", str(len(response)), response)
            return

        if (self.headers["Content-type"] != "application/json" or "name" not in request or "quantity" not in request or "type" not in request):
            print ("Invalid POST request - JSON object should contain the keys \"name\", \"quantity\" and \"type\"")
            #If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 400, "message": "Invalid request- JSON object should contain name, quantity and type"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(400, "application/json", str(len(response)), response)
            return

        # Populate the order information from the recived JSON object
        stockname = request["name"]
        quantity = request["quantity"]
        order_type = request["type"]
        
        # make trade call to order service
        try:
            try:	
                result = self.orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
            except:
                # if not able to communicate with current leader, elect a new leader, and continue trade
                self.leaderId = self.leader_election()
                self.orderService = pb2_grpc.OrderStub(self.order_channel)
                result = self.orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
        except:
               print("All replicas down")
               #If the POST request was not successful as all replicas are down, return JSON reply with a top-level error object
               json_str = json.dumps({"error": {"code": 500, "message": "Stock could not be traded as all replicas are down"}})
               response = self.convert_json_string(json_str) 
               self.create_and_send_response(500, "application/json", str(len(response)), response)
               return    

        # result = self.orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
        print("Response received from the back-end Order service:")
        print(result)

        # If the trade request was succesful from the order service, send the JSON object containing the Transaction number
        if result.error == pb2.NO_ERROR:
            #Return JSON reply with a top-level data object
            transaction_number = result.transaction_number
            json_str = json.dumps({"data": {"transaction_number": transaction_number}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(200, "application/json", str(len(response)), response)
        elif result.error == pb2.INVALID_REQUEST:
            #If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 400, "message": "Order type is invalid, only buy/sell are accepted"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(400, "application/json", str(len(response)), response)
        elif result.error == pb2.INVALID_STOCKNAME:
            #If the POST request was not successful due to invalid stockname, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(404, "application/json", str(len(response)), response)
        elif result.error == pb2.INSUFFICIENT_QUANTITY:
            json_str = json.dumps({"error": {"code": 400, "message": "Available quantity to buy is less than requested quantity"}})
            response = self.convert_json_string(json_str)
            self.create_and_send_response(400, "application/json", str(len(response)), response)
        else:
            #If the POST request was not successful, return JSON reply with a top-level error object
            json_str = json.dumps({"error": {"code": 500, "message": "Stock could not be traded due to internal error"}})
            response = self.convert_json_string(json_str) 
            self.create_and_send_response(500, "application/json", str(len(response)), response)

    # method to pick a leader from currently running order services based on their id
    def leader_election(self):
        print("Leader election")
        if not len(self.order_Ids)>0:
            print("All replicas down!!")
            return -999
        
        order_Hosts_copy = self.order_Hosts.copy()
        order_Ports_copy = self.order_Ports.copy()
        order_Ids_copy = self.order_Ids.copy()
        while len(order_Ids_copy)>0:
            if not len(order_Ids_copy)>0:
                print("All replicas down!!")
                return -999
            max_id = max(order_Ids_copy)
            self.order_host, self.order_port = order_Hosts_copy.pop(order_Ids_copy.index(max_id)), order_Ports_copy.pop(order_Ids_copy.index(max_id))
            order_Ids_copy.remove(max_id)
            # print(f"Order service leader with id {max_id} selected, proceeding to connect and notify other replicas...")
            # print ("Connecting to order service at host:" + self.order_host + " ,port: " + str(self.order_port) + " with id " + str(max_id))
            self.order_channel = grpc.insecure_channel(f"{self.order_host}:{self.order_port}")
            o_stb = pb2_grpc.OrderStub(self.order_channel)
            try:
                # check if service responsive
                result = o_stb.healthCheck(pb2.checkMessage(ping="health check"))
                if result.response:
                    result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, replica_Ids=self.order_Ids, replica_Ports=self.order_Ports, replica_Hosts=self.order_Hosts))
                    for id, port, host in zip(self.order_Ids, self.order_Ports, self.order_Hosts):
                        if id == max_id:
                            continue
                        print("Connecting to : ",id, host, port)
                        try:
                            channel = grpc.insecure_channel(f"{host}:{port}")
                            o_stb = pb2_grpc.OrderStub(channel)
                            # notify order services of elected leader
                            result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, replica_Ids=self.order_Ids, replica_Ports=self.order_Ports, replica_Hosts=self.order_Hosts))
                            channel.close()
                        except:
                            # if unable to establish connection, continue
                            continue
                    return max_id
                else:
                    print("Error setting leader, retrying..")
            except:
                print("Error setting leader, retrying..")

if __name__ == "__main__":

	CACHE_SIZE = int(os.getenv("CACHE_SIZE", 5))
	stocksLRUCache = MyLRUCache(CACHE_SIZE)
	frontend_host = os.getenv("FRONTEND_HOST", "0.0.0.0")
	frontend_port = int(os.getenv("FRONTEND_PORT", 8000))
	print("Running Front-End Service on host: " + frontend_host + " , port:" + str(frontend_port))
	http_server = ThreadingHTTPServer((frontend_host, frontend_port), MyHTTPHandlerClass)
	http_server.serve_forever()
