import argparse
from grpc import server
from queue_pb2 import isFull, item, size
from concurrent import futures
from queue_pb2_grpc import QueueServicer
from queue_pb2_grpc import add_QueueServicer_to_server

Size = 0

class Queue(QueueServicer):
    def __init__(self):
        self.queue = []

    def Put(self, request, context):
        self.queue.append(request)
        if len(self.queue) > Size:
            return isFull(result=False)
        return True

    def Peek(self, request, context):
        if len(self.queue) == 0:
            return item(result=None)
        return item(result=self.queue[0])
    
    def Pop(self, request, context):
        if len(self.queue) == 0:
            return item(result=None)
        return item(result=self.queue.pop(0))


    def Size(self, request, context):
        return size(result=len(self.queue))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('size')
    args = parser.parse_args()
    Size = args.size
    server = server(futures.ThreadPoolExecutor(max_workers=10))
    add_QueueServicer_to_server(Queue(), server)
    server.add_insecure_port(args.port)
    server.start()
