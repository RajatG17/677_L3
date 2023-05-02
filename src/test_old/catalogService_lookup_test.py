import sys
sys.path.append("..")
from sys import argv
import random
from proto import service_rpc_pb2 as pb2
from proto import service_rpc_pb2_grpc as pb2_grpc
import grpc

host = "0.0.0.0"
port = "6000"

def test_valid_stockname():
    stock_names = ["GameStart", "FishCo", "MenhirCo", "BoarCo"]
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        catalogStub = pb2_grpc.CatalogStub(channel)
    
        result = catalogStub.lookup(pb2.lookupRequestMessage(stockname=stock_names[random.randint(0, 3)]))
        print("valid stock test : ", result)

        assert result.error == pb2.NO_ERROR, "There should be no Error"


def test_invalid_stockname():
    stock_names = ["FisrhCo", "MenhihrCo", "GameSdtart", "BoardCo"]
    # create a channel
    channel = grpc.insecure_channel(f"{host}:{port}")

    with channel:
        catalogStub = pb2_grpc.CatalogStub(channel)
        # test by sending a stockname not availabele in stock catalog
        result = catalogStub.lookup(pb2.lookupRequestMessage(stockname=stock_names[random.randint(0, 3)]))

        print("Invalid stock test: ", result)

    assert result.error == pb2.INVALID_STOCKNAME, "Should return Invalid Stockname Error"

if __name__ == "__main__":
    if (len(argv) == 2):
        host = '127.0.0.1'
        port = int(argv[1]) 
    elif (len(argv) == 3):
        host = argv[1]
        port = int(argv[2])

    test_valid_stockname()

    test_invalid_stockname()



