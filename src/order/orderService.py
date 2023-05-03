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

class OrderService(pb2_grpc.OrderServicer):

    def __init__(self, file_path, id=1, leaderId=None):
        self.transaction_number = transaction_number
        self.file_path = file_path
        self.id = id
        self.synchronize_database()
        # create lock instance
        self.lock = rwlock.RWLockRead()
        try:
            # create channel for communicating with catalog service
            catalog_hostname = os.getenv('CATALOG_HOST', 'catalog')
            catalog_port = int(os.getenv('CATALOG_PORT', 6000))
            self.channel = grpc.insecure_channel(f"{catalog_hostname}:{catalog_port}")
            print(f"Order service with id {self.id} conneced to catalog service !")
        except:
            print("Error establishing a channel with catalog service")
        
        

    def trade(self, request, context):
        # get stockname, quantity and order type (buy/sell)  
        stockname = request.stockname
        quantity= request.quantity
        order_type = request.type
        # print("Inside order S - ", self.id)

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

                # make grpc call to catalog service to cary out trade operation 
                status = catalogService.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stockname, quantity=quantity, type=order_type, serviceId=int(self.id)))
                # print(status.error)
                # If no error proceed with generating transaction number and logging the transaction
                if status.error == pb2.NO_ERROR:
                    with self.lock.gen_wlock() as wlock:
                        self.transaction_number  += 1
                        for id, port, host in  zip(self.replica_Ids, self.replica_Ports, self.replica_Hosts):
                            if self.id == id:
                                continue
                            try:
                                order_channel = grpc.insecure_channel(f"{host}:{port}")
                                stub = pb2_grpc.OrderStub(order_channel)
                                
                                result = stub.update_db(pb2.syncRequestMessage(transaction_number=self.transaction_number, stockname=stockname, quantity=quantity, type=order_type))
                                if result.error == pb2.NO_ERROR:
                                    order_channel.close()
                                else:
                                    print("Error syncing transactions")
                                    order_channel.close()
                            except:
                                continue
                        # open log file and append the latest transaction to it
                        with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "a") as transaction_logs:
                            transaction_str = str(f"{self.transaction_number} - Stockname: {stockname}  Quantity: {quantity} Order: {order_type}\n")
                            transaction_logs.write(transaction_str)
                        # send appropriate error code (for no error) and transaction number back to front end server
                    return pb2.tradeResponseMessage(error=pb2.NO_ERROR, transaction_number=self.transaction_number)
                # else forward the error to front end server to send appropriate response to client
                else:
                    return pb2.tradeResponseMessage(error=status.error) 
            return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)
        except:
            return pb2.tradeResponseMessage(error=pb2.INTERNAL_ERROR)
        
    # method to update follower services' database
    def update_db(self, request, context):
        stockname = request.stockname
        quantity= request.quantity
        order_type = request.type
        self.transaction_number = request.transaction_number
        try:
            # open log file and append the latest transaction to it
            print("Update follower")
            with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "a") as transaction_logs:
                with self.lock.gen_wlock() as wlock:
                    transaction_str = str(f"{self.transaction_number} - Stockname: {stockname}  Quantity: {quantity} Order: {order_type}\n")
                    transaction_logs.write(transaction_str)
            return pb2.syncResponseMessage(error=pb2.NO_ERROR)
        except:
            return pb2.syncResponseMessage(error=pb2.DB_UPDATE_ERROR)   
        
    # method to lookup order details provided its transaction number
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
                            #order_type = order_type[:-1]
                            #print("order_type" + order_type)
                            order_quantity = int(contents[6])
                            # send appropriate error code (for no error) and transaction details back to front end server
                            return pb2.lookupOrderResponseMessage(error=pb2.NO_ERROR, number=transaction_number, name=stockname, type=order_type, quantity=order_quantity)
                 transaction_logs.close()
            # return an appropriate error to indicate invalid order number
            return pb2.lookupOrderResponseMessage(error=pb2.INVALID_ORDERNUMBER)
        except:
            return pb2.lookupOrderResponseMessage(error=pb2.INTERNAL_ERROR)   

    # method to check if service is responding
    def healthCheck(self, request, context):
        try:
            if request.ping == "health check":
                return pb2.checkResponse(response=True, error="None")
        except:
            return pb2.checkResponse(response=False, error="Error")

    # method to notify order services of elected leader by frontend
    def setLeader(self, request:pb2.leaderMessage, context):
        try:
            leaderId = request.leaderId
            self.replica_Ids = request.replica_Ids
            self.replica_Ports = request.replica_Ports
            self.replica_Hosts = request.replica_Hosts
            print("Leader Id set to : ", leaderId)
            return pb2.leaderResponse(result=True)
        except:
            return pb2.leaderResponse(result=False)

    # Method to synchronize database from other replicas after service instances recovers/restarts
    def synchronize_database(self):
        print("Sync database")
        self.replica_Ids = [int(x) for x in os.getenv("ORDER_ID").split(",")]
        self.replica_Ports = [int(x) for x in os.getenv("ORDER_PORTS").split(",")]
        self.replica_Hosts = list(os.getenv("ORDER_HOSTS", "0.0.0.0,0.0.0.0,0.0.0.0").split(","))
        
        with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "r+") as transaction_logs:
            try:
                # get the last transaction number curently in own database
                last_order_number = 0
                if transaction_logs.read(1):
                    # transaction_logs.seek(0)
                    last_line = transaction_logs.readlines()[-1]
                    if last_line:
                        last_order_number = int(last_line.split(" ")[0])
                
                transaction_number = last_order_number
                for id, port, host in zip(self.replica_Ids, self.replica_Ports, self.replica_Hosts):
                    # contact other replicas to search for any updates  
                    if self.id == id:
                        continue
                    try:
                        channel = grpc.insecure_channel(f"{host}:{port}")
                        order_stub = pb2_grpc.OrderStub(channel)
                        result = order_stub.lookupOrder(pb2.lookupOrderRequestMessage(order_number=transaction_number))
                    except:
                        # print("Error channel conn")
                        continue
                    if result.error == pb2.NO_ERROR:
                        # if any updates to transaction logs, get the updates 
                        update_result = order_stub.send_db_data(pb2.dataRequestMessage(transaction_number=transaction_number))
                        if update_result.error == pb2.NO_ERROR:                        
                            transaction_str = update_result.transaction_str
                            for line in transaction_str:
                                # write the updates to own database file
                                transaction_logs.write(line)  
                            return pb2.recoveryResponseMessage(error=pb2.NO_ERROR)                    
                return pb2.recoveryResponseMessage(error=pb2.DB_UPDATE_ERROR)              
            except:
                return (pb2.recoveryResponseMessage(error=pb2.DB_UPDATE_ERROR))
            
    # method to send the updated data to a recovered service 
    def send_db_data(self, request, context):
        transaction_number = request.transaction_number
        db_start = -1
        try:
            with open(self.file_path+f"transaction_log_{str(self.id)}.txt", "r") as transaction_logs:
                with self.lock.gen_rlock() as rlock:
                    logs = transaction_logs.readlines()
                    for i, line in enumerate(logs):
                        if str(transaction_number) in line:
                            db_start = i
                            break
                
                if db_start >= 0:
                    transaction_str = logs[db_start+1:]
                    if transaction_str:
                        return pb2.dataResponseMessage(error=pb2.NO_ERROR, transaction_str=transaction_str)
                    else:
                        return pb2.dataResponseMessage(error=pb2.DB_UPDATE_ERROR)
        except:
            return pb2.dataResponseMessage(error=pb2.DB_UPDATE_ERROR)
            

def serve(id, file_path, port, host="0.0.0.0", max_workers=MAX_WORKER_THRESHOLD):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb2_grpc.add_OrderServicer_to_server(OrderService(file_path, id), server)
    server.add_insecure_port(f'{host}:{port}')
    print ("Order service running on:")
    print(host, port)
    server.start()
    server.wait_for_termination()             
    
if __name__=="__main__":

    MAX_WORKER_THRESHOLD = int(os.getenv("MAX_WORKER_THRESHOLD_ORDER", 5))
    order_host = os.getenv("ORDER_HOST", "0.0.0.0")
    order_port = int(os.getenv("ORDER_PORT", 6001))
    id = int((os.getenv("SERVICE_ID", 1)))
    file_path = os.getenv("FILE_PATH", "../data/")
    print ("Running order service on host: " + order_host + " , port: " + str(order_port) + " with id "+ str(id))

    # get last transaction number from log file if it exists
    try:
        file = open(file_path+f"transaction_log_{str(id)}.txt", "r") 
        last_line = file.readlines()[-1]
        if last_line:
            last_line_word = int(last_line.split(" ")[0]) if last_line else 0
            transaction_number = last_line_word
        file.close()
    except:  
        #unique transaction for every order      
        transaction_number = 0

    serve(id, file_path, order_port, order_host, MAX_WORKER_THRESHOLD)
        
