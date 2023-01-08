import grpc
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from pubsub_pb2_grpc import add_pubsubServicer_to_server, pubsubServicer
from pubsub_pb2 import mes2client

class PubsubServer():
    # 实现pubsub.proto中定义的接口
    def __init__(self):
        self.threadLock = threading.Lock()
        self.n = 0
        self.mes = "default"

    def pubsubServe(self, request, context):
        if self.n == 0:
            self.threadLock.acquire()  # 线程锁
            self.n += 1
            self.mes = input('mes:')
            self.threadLock.release()  # 释放锁
        self.threadLock.acquire()  # 线程锁
        self.n = 0
        self.threadLock.release()  # 释放锁
        return mes2client(mes2=self.mes)

def serve():
    # 通过thread pool来并发处理server的任务
    server = grpc.server(ThreadPoolExecutor(max_workers=2))
    # 将对应的任务处理函数添加到rpc server中
    add_pubsubServicer_to_server(PubsubServer(), server)
    # 设置IP地址和端口
    server.add_insecure_port('[::]:50074')
    print("Server is running...")
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)

logging.basicConfig()
serve()