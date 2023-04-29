import sys
sys.path.append("..")
from sys import argv
import random
from proto import service_rpc_pb2 as pb2
from proto import service_rpc_pb2_grpc as pb2_grpc
import grpc

def order_valid_request(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    quantity = random.randint(1, 50)
    type = random.choice(["buy","sell"])

    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        orderStub = pb2_grpc.OrderStub(channel)
        # test trade method by sending correct methods
        result = orderStub.trade(pb2.tradeRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type))

        print("Test sending correct order: ", result)

        assert result.error == pb2.NO_ERROR, "There should be no Error"

def order_invalid_request(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    quantity = int(1e+9)
    type = random.choice(["buy"])
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        orderStub = pb2_grpc.OrderStub(channel)
        # test by sending a quantity greater than available amount
        result = orderStub.trade(pb2.tradeRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type))

        print("Test sending excessive quantity: ", result)

        assert result.error == pb2.INSUFFICIENT_QUANTITY, "There should be no Error"

def order_invalid_name_request(host, port):
    stock_names = ["GameSetart", "FishCow", "MesnhirCo", "BoardCo"]
    quantity = random.randint(1, 50)
    type = random.choice(["buy","sell"])

    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        orderStub = pb2_grpc.OrderStub(channel)
        # test trade method by sending incorrect names
        result = orderStub.trade(pb2.tradeRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type))

        print("Test sending invalid stockname: ", result)

        assert result.error == pb2.INVALID_STOCKNAME, "There should be invalid stockname Error"

def order_invalid_type_request(host, port):
    stock_names = ["GameSetart", "FishCow", "MesnhirCo", "BoardCo"]
    quantity = random.randint(1, 50)
    type = random.choice(["bury","sael"])

    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        orderStub = pb2_grpc.OrderStub(channel)
        # test trade method by sending correct methods
        result = orderStub.trade(pb2.tradeRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type))

        print("Test sending invalid order type: ", result)

        assert result.error == pb2.INVALID_REQUEST, "There should be invalid request Error"


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
    
    order_valid_request(host, port)
    order_invalid_request(host, port)
    order_invalid_name_request(host, port)
    order_invalid_type_request(host, port)
