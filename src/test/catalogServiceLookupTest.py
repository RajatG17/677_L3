import sys
sys.path.append("..")
from sys import argv
import random
from proto import service_rpc_pb2 as pb2
from proto import service_rpc_pb2_grpc as pb2_grpc
import grpc

def test_valid_stockname(host, port):
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        for i in range(0, len(stock_names)):
            catalogStub = pb2_grpc.CatalogStub(channel)
    
            result = catalogStub.lookup(pb2.lookupRequestMessage(stockname=stock_names[i]))
            print("For stockname: " + stock_names[i] + " , valid stock test result : ", result)

            assert result.error == pb2.NO_ERROR, "There should be no Error"


def test_invalid_stockname(host, port):
    stock_names = ["FisrhCo", "MenhihrCo", "GameSdtart", "BoardCo"]
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        for i in range(0, len(stock_names)):
            catalogStub = pb2_grpc.CatalogStub(channel)
            # test by sending a stockname not availabele in stock catalog
            result = catalogStub.lookup(pb2.lookupRequestMessage(stockname=stock_names[i]))

            print("For stockname: " + stock_names[i] + " , Invalid stock test result : ", result)

            assert result.error == pb2.INVALID_STOCKNAME, "Should return Invalid Stockname Error"

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
    
    test_valid_stockname(host, port)

    test_invalid_stockname(host, port)
