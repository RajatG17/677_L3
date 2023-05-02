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

class MyHTTPHandlerClass(http.server.BaseHTTPRequestHandler):
	protocol_version = 'HTTP/1.1'

	def __init__(self, request, client_address, server):
		# create channel for communicating with catalog service
		try:
			catalog_host = os.getenv("CATALOG_HOST", "0.0.0.0")
			catalog_port = int(os.getenv("CATALOG_PORT", 6000))
			print ("Connecting to catalog service at host:" + catalog_host + " ,port: " + str(catalog_port))
			self.catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
		except:
			print("Error establishing a channel with catalog service")

		# elect leader of order servies and notify to all services
		try:
			self.order_Ports = list(int(x) for x in list(os.getenv("ORDER_PORTS").split(",")))
			self.order_Hosts = list(os.getenv("ORDER_HOSTS").split(","))
			self.order_Ids = list(int(x) for x in list(os.getenv("ORDER_ID").split(",")))
			self.down_services = []
			self.leaderId = self.leader_election()
			self.catalogService = pb2_grpc.CatalogStub(self.catalog_channel)
			self.orderService = pb2_grpc.OrderStub(self.order_channel)
			self.order_recover_sync()
			if self.leaderId < 0:
				print("Erorr connecting to all order service instances")
		except:
			print("Error establishing a channel with order service")


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

	def do_GET(self):
		"""
		# create channel for communicating with catalog service
		try:
			catalog_host = os.getenv("CATALOG_HOST", "catalog")
			catalog_port = int(os.getenv("CATALOG_PORT", 6000)) 
			self.catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
		except:
			print("Error establishing a channel with catalog service")
		"""

		get_path = str(self.path)
		parsed_path = get_path.split("/")

		# Check if the URL for the GET method is invalid - It should be of the format : "/stocks/<stock_name>"
		if (len(parsed_path) != 3 or parsed_path[0] != "" or parsed_path[1] != "stocks"):
			print ("URL for HTTP GET request is invalid - It should be of the format : ") 
			print("\"/stocks/<stock_name>\"")
			# If the GET request was not successful, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 400, "message": "Invalid GET request/URL"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(400, "application/json", str(len(response)), response)
			return
		
		# Obtain the stockname from the parsed URL/path
		stockname = parsed_path[2]

		# make lookup call to catalog service
		
		result = self.catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
		print("Response received from the back-end Catalog service:")
		print(result)
		
		if result.error == pb2.NO_ERROR:
			#Return JSON reply with a top-level data object 
			stockname = result.stockname
			price = result.price
			quantity = result.quantity
			json_str = json.dumps({"data": {"name": stockname, "price": price, "quantity": quantity}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(200, "application/json", str(len(response)), response)
		elif result.error == pb2.INVALID_STOCKNAME:
			#If the GET request was not successful due to invalid stockname, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 404, "message": "stock not found"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(404, "application/json", str(len(response)), response)
		else:			
			#If the GET request was not successful due to any other error, return JSON reply with a top-level error object
			json_str = json.dumps({"error": {"code": 500, "message": "Lookup Failed due to internal error"}})
			response = self.convert_json_string(json_str)
			self.create_and_send_response(500, "application/json", str(len(response)), response) 

	def do_POST(self):
		"""
		# create channel for communicating with order service
		try:
			order_host = os.getenv("ORDER_HOST", "order")
			order_port = int(os.getenv("ORDER_PORT", 6001))
			self.order_channel = grpc.insecure_channel(f"{order_host}:{order_port}")
		except:
			print("Error establishing a channel with order service")
		"""
		self.order_recover_sync()
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
		"""
		# Read the JSON object attached by the client to the POST request
		length = int(self.headers["Content-Length"])
		request = json.loads(self.rfile.read(length).decode('utf-8'))
		"""

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
			result = self.orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
			# if not result.error:
			# 	# elect new leader
			# 	self.leaderId = self.leader_election(self.runing_order_ids)
			# 	self.orderService = pb2_grpc.OrderStub(self.order_channel)
			# 	response = self.orderService.healthCheck(pb2.checkMessage(ping="health check"))
		except:
			# if not able to communicate with current leader, elect a new leader, and continue trade
			self.order_Ids
			self.down_services.append([self.leaderId, self.order_host, self.order_port])
			self.leaderId = self.leader_election()
			self.orderService = pb2_grpc.OrderStub(self.order_channel)
			result = self.orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))

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
		if not len(self.order_Ids)>0:
			print("All replicas down!!")
			return -999
		
		
		max_id = max(self.order_Ids)
		self.order_host, self.order_port = self.order_Hosts[self.order_Ids.index(max_id)], self.order_Ports[self.order_Ids.index(max_id)]
		# print(f"Order service leader with id {max_id} selected, proceeding to connect and notify other replicas...")
		# print ("Connecting to order service at host:" + self.order_host + " ,port: " + str(self.order_port) + " with id " + str(max_id))
		self.order_channel = grpc.insecure_channel(f"{self.order_host}:{self.order_port}")
		o_stb = pb2_grpc.OrderStub(self.order_channel)
		# check if service responseive
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
					# notify orer services of elected leader
					result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, replica_Ids=self.order_Ids, replica_Ports=self.order_Ports, replica_Hosts=self.order_Hosts))
					channel.close()
				except:
					# if unable to establish connection, add that service to list of stopped/ crashed services
					self.down_services.append([id, host, port])
					continue
			self.order_Ids.remove(max_id)
			self.order_Hosts.remove(self.order_host)
			self.order_Ports.remove(self.order_port)
			return max_id
		else:
			print("Error setting leader, retrying..")
			self.leader_election()

	def try_sync_recovered_services(self):
		print("Trying to connect downed order services if any...")
		if self.down_services:
			for service in self.down_services:
				with grpc.insecure_channel(f"{service[1]}:{service[2]}") as channel:
					stub = pb2_grpc.OrderStub(channel)
					try:
						result = stub.healthCheck(pb2.checkMessage(ping="health check"))
					except:
						continue
					if result.response:
						# add id, host, and port of recovered service to list of online services
						self.order_Ids.append(int(service[0]))
						self.order_Hosts.append(service[1])
						self.order_Ports.append(int(service[2]))
						# notify recovered service of current leader
						result = stub.setLeader(pb2.leaderOrderMessage(leaderId=self.leaderId, replica_Ids=self.order_Ids, replica_Ports=self.order_Ports, replica_Hosts=self.order_Hosts))
						# notify current leader of id, host and port of recovered service
						self.orderService.setLeader(pb2.leaderOrderMessage(leaderId = self.leaderId, replica_Ids=self.order_Ids, replica_Ports=self.order_Ports, replica_Hosts=self.order_Hosts))
						# remove recovered service from list of crashed/ stopped services
						self.down_services.remove(service)
						
				

	def order_recover_sync(self):
		self.try_sync_recovered_services()



if __name__ == "__main__":

	frontend_host = os.getenv("FRONTEND_HOST", "0.0.0.0")
	frontend_port = int(os.getenv("FRONTEND_PORT", 4000))
	print("Running Front-End Service on host: " + frontend_host + " , port:" + str(frontend_port))
	http_server = ThreadingHTTPServer((frontend_host, frontend_port), MyHTTPHandlerClass)
	http_server.serve_forever()
