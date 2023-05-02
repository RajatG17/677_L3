import sys
sys.path.append("..")
from sys import argv
import random
from proto import service_rpc_pb2 as pb2
from proto import service_rpc_pb2_grpc as pb2_grpc
import grpc

host = "0.0.0.0"
port = "6001"

def test_valid_ordernumber(host, port):
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        for transaction_number in range(1, 6):
            orderStub = pb2_grpc.OrderStub(channel)
            # test by sending a ordernumber available in transactions log        
            result = orderStub.lookupOrder(pb2.lookupOrderRequestMessage(order_number=transaction_number))
            print("For order number: " + str(transaction_number) + " , valid lookup test result : ", result)

            assert result.error == pb2.NO_ERROR


def test_invalid_ordernumber(host, port):
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        for transaction_number in range(int(1e+9), int(1e+9)+5):
            orderStub = pb2_grpc.OrderStub(channel)
            # test by sending a ordernumber not available in transactions log
            result = orderStub.lookupOrder(pb2.lookupOrderRequestMessage(order_number=transaction_number))
            print("For order number: " + str(transaction_number) + " , invalid lookup test result : ", result)

            assert result.error == pb2.INVALID_ORDERNUMBER

if __name__ == "__main__":
    if (len(argv) == 3):
        host = argv[1]
        port = int(argv[2])
    elif (len(argv) == 2):
        host = "0.0.0.0"
        port = int(argv[1])
    else:
        host = "0.0.0.0"
        port = 6001
    
    test_valid_ordernumber(host, port)

    test_invalid_ordernumber(host, port)
