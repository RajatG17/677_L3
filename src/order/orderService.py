import sys
import os
sys.path.append("..")
import csv
import grpc
import os
from concurrent import futures
from proto import service_rpc_pb2_grpc as pb2_grpc
from proto import service_rpc_pb2 as pb2 
from readerwriterlock import rwlock

# Maximum worker threshold for threadpool (default value is 3)
MAX_WORKER_THRESHOLD = 3
#unique transaction for every order
transaction_number = 0

class OrderService(pb2_grpc.OrderServicer):

    def __init__(self, file_path, id=1, isLeader=False, leaderId=None):
        global transaction_number
        self.file_path = file_path
        self.id = id
        self.leaderId = leaderId
        self.isLeader = isLeader
        # create lock instance
        self.lock = rwlock.RWLockRead()
        try:
            # create channel for communicating with catalog service
            catalog_hostname = os.getenv('CATALOG_HOST', 'catalog')
            catalog_port = int(os.getenv('CATALOG_PORT', 6000))
            self.channel = grpc.insecure_channel(f"{catalog_hostname}:{catalog_port}")
            print(f"Orderservice with id {self.id} conneced to catalog service !")
        except:
            print("Error establishing a channel with catalog service")

        
        # # get last transaction number from log file if it exists
        # with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "r") as file:
        #     try:
        #         last_line = file.readlines()[-1]
        #         if last_line:
        #             last_line_word = int(last_line.split(" ")[0]) if last_line else 0
        #             transaction_number = last_line_word
        #     except:        
        #         pass


    def trade(self, request, context):
        global transaction_number
        # get stockname, quantity and order type (buy/sell)  
        stockname = request.stockname
        quantity= request.quantity
        order_type = request.type
        print("Inside order S - ", self.id)

        # return error order type is invalid (other than buy/sell)
        if order_type.lower() not in ["buy", "sell"] or quantity <= 0:
            return pb2.tradeResponseMessage(error=pb2.INVALID_REQUEST)

        catalogService = pb2_grpc.CatalogStub(self.channel)
        
        # make lookup call to catalog service
        result = catalogService.lookup(pb2.lookupRequestMessage(stockname=stockname))
        print(result)

        # return error if stockname is not in stocks catalog
        if result.error == pb2.INVALID_STOCKNAME:
            return pb2.tradeResponseMessage(error=pb2.INVALID_STOCKNAME)
        # return error if available quantity to buy is less than requested quantity
        if (order_type.lower() == "buy" and result.quantity < quantity):
            return pb2.tradeResponseMessage(error=pb2.INSUFFICIENT_QUANTITY)
        
        try:
            # check if stockname provided is valid & if request type is buy, there is enough stock available to buy
            if result.error == pb2.NO_ERROR and ((order_type.lower() == "buy" and int(result.quantity) >= quantity) or (order_type.lower() == "sell")):
                print("About to make call to catalog....")
                # make grpc call to catalog service to cary out trade operation 
                if self.isLeader:
                    status = catalogService.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stockname, quantity=quantity, type=order_type, serviceId=int(self.id)))
                    # print(status.error)
                    # If no error proceed with generating transaction number and logging the transaction
                    if status.error == pb2.NO_ERROR:
                        with self.lock.gen_wlock() as wlock:
                            transaction_number  += 1
                            for port, host in  zip(self.followers, self.followerHosts):
                                order_channel = grpc.insecure_channel(f"{host}:{port}")
                                stub = pb2_grpc.OrderStub(order_channel)
                                result = stub.trade(pb2.tradeRequestMessage(transaction_number=transaction_number, stockname=stockname, quantity=quantity, type=order_type))
                                print("rsut:", result)
                                if result.error == pb2.NO_ERROR:
                                    order_channel.close()
                                else:
                                    print("Error syncing transactions")
                                    order_channel.close()

                            # open log file and append the latest transaction to it
                            with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "a") as transaction_logs:
                                transaction_str = str(f"{transaction_number} - Stockname: {stockname}  Quantity: {quantity} Order: {order_type}, service id: {self.leaderId}, \n")
                                transaction_logs.write(transaction_str)
                            # send appropriate error code (for no error) and transaction number back to front end server
                        return pb2.tradeResponseMessage(error=pb2.NO_ERROR, transaction_number=transaction_number)
                    # else forward the error to front end server to send appropriate response to client
                    else:
                        return pb2.tradeResponseMessage(error=status.error) 
                else:
                    # open log file and append the latest transaction to it
                    print("Sync follower")
                    with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "a") as transaction_logs:
                        transaction_str = str(f"{request.transaction_number} - Stockname: {stockname}  Quantity: {quantity} Order: {order_type}, service id: {self.leaderId}, \n")
                        transaction_logs.write(transaction_str)
                    return pb2.tradeResponseMessage(error=pb2.NO_ERROR, transaction_number=transaction_number)
            else:   
                return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)
        except:
            return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)
        
    def lookupOrder(self, request, context):
        try:
            order_number = int(request.order_number)
            with self.lock.gen_rlock() as rlock:
                 with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "r") as transaction_logs:
                     for line in transaction_logs:
                         contents = line.strip().split(" ")
                         transaction_number = int(contents[0])
                         if (transaction_number == order_number):
                             stockname = contents[3]
                             order_type = contents[8]
                             order_type = order_type[:-1]
                             order_quantity = int(contents[6])
                             # send appropriate error code (for no error) and transaction details back to front end server
                             return pb2.lookupOrderResponseMessage(error=pb2.NO_ERROR, number=transaction_number, name=stockname, type=order_type, quantity=order_quantity)
                 transaction_logs.close()
            # return an appropriate error to indicate invalid order number
            return pb2.lookupOrderResponseMessage(error=pb2.INVALID_ORDERNUMBER)
        except:
            return pb2.lookupOrderResponseMessage(error=pb2.INTERNAL_ERROR)   

    def healthCheck(self, request, context):
        try:
            if request.ping == "health check":
                return pb2.checkResponse(response="Service up", error="None")
        except:
            return pb2.checkResponse(response="Service down", error="Error")

    def setLeader(self, request, context):
        try:
            leaderId = request.leaderId
            print("Leader Id set to : ", leaderId)
            self.leaderId = leaderId
            self.isLeader = (self.leaderId == self.id)
            if self.isLeader:
                self.followerHosts = request.followerHosts
                self.followers = request.followerPorts
                self.followerIds = request.followerIds
                print("Followers: ", self.followers)
                print("Ids : ", self.followerIds)
                print("Hosts: ", self.followerHosts)
            return pb2.leaderResponse(result=True)
        except:
            return pb2.leaderResponse(result=False)


def serve(id, file_path, port, host="0.0.0.0", max_workers=MAX_WORKER_THRESHOLD):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_OrderServicer_to_server(OrderService(file_path, id), server)
    server.add_insecure_port(f'{host}:{port}')
    print ("Order service running on:")
    print(host, port)
    server.start()
    server.wait_for_termination()             
    
if __name__=="__main__":

    if len(sys.argv) > 3:
        file_path = str(sys.argv[2])
        id = int(sys.argv[1])
        order_port = sys.argv[3]
        order_host = str(sys.argv[4])
    else:
        order_host = str(sys.argv[3])
        order_port = sys.argv[2]
        file_path = str(sys.argv[1])
        id = 1
    MAX_WORKER_THRESHOLD = int(os.getenv("MAX_WORKER_THRESHOLD_ORDER", 5))
    print ("Running order service on host: " + order_host + " , port: " + str(order_port) + " with id "+ str(id))
    
    serve(id, file_path, order_port, order_host, MAX_WORKER_THRESHOLD)
        
