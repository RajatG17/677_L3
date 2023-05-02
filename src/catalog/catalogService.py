import sys
sys.path.append("..")

import json
import http.client
import grpc
import os
import pandas as pd
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2
from readerwriterlock import rwlock
import requests
# from dirsync import sync

# Maximum worker threshold for threadpool (default value is 3)
MAX_WORKER_THRESHOLD = 3

# Catalog service server class to carry out lookup and trade operations with backend(file)
class CatalogService(pb2_grpc.CatalogServicer):

    def __init__(self, leaderId = None) -> None:
        self.lock = rwlock.RWLockRead()
        self.leaderId = leaderId
        # load data
        try:
            self.data_file = pd.read_csv("../data/stock_data.csv")
        except:
            print("Failed to load files")

    def lookup(self, request, context):
        try:
            # print("Inside lookup method")
            stockname = request.stockname
            # acquire read lock
            read_lock = self.lock.gen_rlock()

            if stockname in self.data_file.keys():
                # get stock details from data
                with read_lock:
                    name = stockname
                    price =  self.data_file[stockname][0]
                    quantity = self.data_file[stockname][1]
                # print(name, price, quantity)
                return pb2.lookupResponseMessage(error=pb2.NO_ERROR, stockname=name, price=price, quantity=int(quantity))
            else:
                # return stockname with approperiate error to indicate invalid stockname 
                return pb2.lookupResponseMessage(error=pb2.INVALID_STOCKNAME)
        except :
            return pb2.lookupResponseMessage(error=pb2.INTERNAL_ERROR)
        
    def buy_or_sell_stock(self, request:pb2.orderRequestMessage, context):
            stockname = request.stockname
            quantity = int(request.quantity)
            order_type = request.type
            serviceId = request.serviceId
            # print("Inside catalog service's buy or sell method")

            # acquire write lock
            write_lock = self.lock.gen_wlock()
            # proceed to trade stock
            if order_type.lower() == "buy":
                try:
                    # reduce quantity of stock volume (in server's data)   
                    with write_lock: 
                        if self.data_file[stockname][1] >= quantity:
                            # decrement quantity available to trade
                            self.data_file[stockname][1] -= quantity
                            # update volume of traded stock
                            self.data_file[stockname][2] += quantity
                        else:
                            # return insufficient quantity error
                            return pb2.orderResponseMessage(error=pb2.INSUFFICIENT_QUANTITY)
                        # presist data
                        try:
                            self.data_file.to_csv('../data/stock_data.csv', sep=",", index=False)
                        except:
                            print("Error writing data to file")
                    # print(f"Buy request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 
                    
                    try:
                        # Send cache invalidation request to front-end service after successful Buy request
                        print("Send cache invalidation request to front-end service")
                        conn = http.client.HTTPConnection("0.0.0.0", 8000)
                        # Send GET request for invalidation
                        name = stockname
                        url = "/stocksCache/" + name
                        conn.request("GET", url)
                        response = conn.getresponse()
                        data = response.read()
                        # print(data)
                        data_json_obj = json.loads(data.decode('utf-8'))    
                        # print(data_json_obj)
                        #if data_json_obj.get("data", 0):
                            # Cache invalidation was successful and client received JSON reply with top-level data object
                            #print ("Cache Invalidation done")
                        #else:
                            # Cache invalidation failed
                            #print ("Cache Invalidation failed")
                        conn.close()
                    except:
                        return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
                    return pb2.orderResponseMessage(error=pb2.NO_ERROR)
                except:
                    # print(f"Error occured processing request for buying {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
            elif order_type.lower() == "sell":
                try:
                    # reduce quantity of stock volume (in server's data)   
                    with write_lock:
                        # increment quantity available to trade
                        self.data_file[stockname][1] += quantity
                        # update total volume of traded stock
                        self.data_file[stockname][2] += quantity
                        # persist data
                        try:
                            self.data_file.to_csv('../data/stock_data.csv', sep=",", index=False)    
                        except:
                            print("Error persisting data")
                    # print(f"Sell request successful for {quantity} stocks of {stockname} for $ {(quantity*self.data_file[stockname][0])}.") 

                    try:
                        # Send cache invalidation request to front-end service after successful Sell request
                        print("Send cache invalidation request to front-end service")
                        conn = http.client.HTTPConnection("0.0.0.0", 8000)
                        # Send GET request for invalidation
                        name = stockname
                        url = "/stocksCache/" + name
                        conn.request("GET", url)
                        response = conn.getresponse()
                        data = response.read()
                        # print(data)
                        data_json_obj = json.loads(data.decode('utf-8'))
                        # print(data_json_obj)
                        #if data_json_obj.get("data", 0):
                            # Cache invalidation was successful and client received JSON reply with top-level data object
                            #print ("Cache Invalidation done")
                        #else:
                            # Cache invalidation failed
                            #print ("Cache Invalidation failed")
                        conn.close()
                    except:
                        return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
                    return pb2.orderResponseMessage(error=pb2.NO_ERROR)
                except:
                    # print(f"Error occured processing request for selling {quantity} {stockname} stocks")
                    return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
            return pb2.orderResponseMessage(error=pb2.INTERNAL_ERROR)
                
                
def serve(hostname="0.0.0.0", port=6000, max_workers=MAX_WORKER_THRESHOLD):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_CatalogServicer_to_server(CatalogService(), server)
    server.add_insecure_port(f'{hostname}:{port}')
    print ("Catalog service running on:")
    print (f'{hostname}:{port}')
    server.start()
    server.wait_for_termination()



if __name__=="__main__":

    # Maximum worker threshold for threadpool (default value is 3)
    MAX_WORKER_THRESHOLD = int(os.getenv("MAX_WORKER_THRESHOLD_CATALOG", 5))
    host = os.getenv("CATALOG_HOST", "0.0.0.0")
    port = int(os.getenv("CATALOG_PORT", 6000))
    
    serve(host, port, MAX_WORKER_THRESHOLD)

