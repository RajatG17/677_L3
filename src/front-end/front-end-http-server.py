import os
import sys
sys.path.append("..")

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
			catalog_host = os.getenv("CATALOG_HOST", "catalog")
			catalog_port = int(os.getenv("CATALOG_PORT", 6000))
			print ("Connecting to catalog service at host:" + catalog_host + " ,port: " + str(catalog_port))
			self.catalog_channel = grpc.insecure_channel(f"{catalog_host}:{catalog_port}")
		except:
			print("Error establishing a channel with catalog service")

		# elect leader of order servies and notify to all services
		try:
			runing_order_id_addrs = list(os.getenv("ORDER_IDS").split("."))
			runing_order_id_addrs = [item.split(":") for item in runing_order_id_addrs]
			self.runing_order_ids = {int(key):int(val) for [val, key] in runing_order_id_addrs}
			self.leaderId = self.leader_election(self.runing_order_ids)
			self.catalogService = pb2_grpc.CatalogStub(self.catalog_channel)
			self.catalogService.setLeader(pb2.leaderMessage(leaderId=self.leaderId))
			print(self.runing_order_ids)
			if self.leaderId < 0:
				print("Erorr connecting to all order srvice instances")
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
			orderService = pb2_grpc.OrderStub(self.order_channel)
			response = orderService.healthCheck(pb2.checkMessage(ping="health check"))
			print(response)
			if response.error == "Error":
				# elect new leader
				self.leader_election(self.runing_order_ids)
		except:
			self.leader_election(self.runing_order_ids)
			self.catalogService.setLeader(pb2.leaderMessage(leaderId=self.leaderId))


		result = orderService.trade(pb2.tradeRequestMessage(stockname=stockname, quantity=quantity, type=order_type))
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

	def leader_election(self, running_id_addrs:dict):
		if not len(running_id_addrs)>0:
			print("All replicas down!!")
			return -999

		try:
			ports = running_id_addrs.values()
			print("Ports: ", ports)
			max_id = max(running_id_addrs)
			order_host = os.getenv("ORDER_HOST", "0.0.0.0")
			order_port = running_id_addrs.pop(max_id)
			follower_ids, follower_ports = running_id_addrs.keys(), running_id_addrs.values()
			print(follower_ids, follower_ports)
			print ("Connecting to order service at host:" + order_host + " ,port: " + str(order_port) + " with id " + str(max_id))
			self.order_channel = grpc.insecure_channel(f"{order_host}:{order_port}")
			o_stb = pb2_grpc.OrderStub(self.order_channel)
			result = o_stb.healthCheck(pb2.checkMessage(ping="health check"))
			result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, followerIds=follower_ids, followerPorts=follower_ports))
			print(result)
			print("Ports: ", ports)

			for port in ports:
				print("Connecting to : ", order_host, port)
				channel = grpc.insecure_channel(f"{order_host}:{port}")
				o_stb = pb2_grpc.OrderStub(channel)
				# result = o_stb.healthCheck(pb2.checkMessage(ping="health check"))
				result = o_stb.setLeader(pb2.leaderOrderMessage(leaderId=max_id, followerIds=follower_ids, followerPorts=follower_ports))
				channel.close()
			return max_id
		except:
			self.leader_election(running_id_addrs)

if __name__ == "__main__":

	frontend_host = os.getenv("FRONTEND_HOST", "0.0.0.0")
	frontend_port = int(os.getenv("FRONTEND_PORT", 4000))
	print("Running Front-End Service on host: " + frontend_host + " , port:" + str(frontend_port))
	http_server = ThreadingHTTPServer((frontend_host, frontend_port), MyHTTPHandlerClass)
	http_server.serve_forever()
