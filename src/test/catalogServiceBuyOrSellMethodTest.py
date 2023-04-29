import sys
sys.path.append("..")
from sys import argv
import random
from proto import service_rpc_pb2 as pb2
from proto import service_rpc_pb2_grpc as pb2_grpc
import grpc

def test_valid_trade_request(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    quantity = random.randint(1, 50)
    type = random.choice(["buy", "sell"])

    channel = grpc.insecure_channel(f"{host}:{port}")

    catalogStub = pb2_grpc.CatalogStub(channel)

    result = catalogStub.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type, serviceId=8))

    print("Valid trade request: ", result)

    assert result.error == pb2.NO_ERROR, "There should be no Error"


def test_invalid_buy_trade_request_invalid_quantity(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    quantity = int(1e+9)
    type = "buy"

    channel = grpc.insecure_channel(f"{host}:{port}")

    catalogStub = pb2_grpc.CatalogStub(channel)

    result = catalogStub.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type, serviceId=8))

    print("Test by sending excessive quantity: ", result)

    assert result.error == pb2.INSUFFICIENT_QUANTITY, "Should return INSUFFICIENT_QUANTITY error"

def test_invalid_sell_trade_request_invalid_stockname(host, port):
    stock_names = ["GameeStart", "FishyCo", "MenthirCo", "BoarCO"]
    quantity = random.randint(1, 50)
    type = random.choice(["buy", "sell"])

    channel = grpc.insecure_channel(f"{host}:{port}")


    catalogStub = pb2_grpc.CatalogStub(channel)

    result = catalogStub.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type, serviceId=8))

    print("Test sending incorrect stock trade request: ", result)

    assert result.error == pb2.INTERNAL_ERROR, "Should return INTERNAL_ERROR"

def test_invalid_sell_trade_request_invalid_type(host, port):
    stock_names = ["GameStart", "FishCo", "MentirCo", "BoarCo"]
    quantity = int(1e+9)
    type = random.choice(["purchase", "trade"])

    channel = grpc.insecure_channel(f"{host}:{port}")

    catalogStub = pb2_grpc.CatalogStub(channel)

    result = catalogStub.buy_or_sell_stock(pb2.orderRequestMessage(stockname=stock_names[random.randint(0, 3)], quantity=quantity, type=type, serviceId=8))

    print("Test sending invalid trade type: ", result)

    assert result.error == pb2.INTERNAL_ERROR, "Should return INTERNAL_ERROR"




if __name__ == "__main__":
    if (len(argv) == 3):
        host = argv[1]
        port = int(argv[2])
    elif (len(argv) == 2):
        host = "0.0.0.0"
        port = int(argv[1])     
    else:
        host = "0.0.0.0"
        port = 6000  
    
    test_valid_trade_request(host, port)

    test_invalid_buy_trade_request_invalid_quantity(host, port)

    test_invalid_sell_trade_request_invalid_stockname(host, port)

    test_invalid_sell_trade_request_invalid_type(host, port)

