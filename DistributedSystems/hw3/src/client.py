import logging
import grpc
from pubsub_pb2 import mes2server
from pubsub_pb2_grpc import pubsubStub

def run():
    # 创建通信信道
    with grpc.insecure_channel('localhost:50074') as channel:
        # 客户端通过stub来实现rpc通信
        stub = pubsubStub(channel)
        while 1:
            try:	    
                mes = stub.pubsubServe(mes2server(mes1='client'), timeout=500)
                print(mes)
            except KeyboardInterrupt:
                exit(0)

logging.basicConfig()
run()