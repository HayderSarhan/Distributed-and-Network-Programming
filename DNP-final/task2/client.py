import grpc
import argparse
import queue_pb2 as queue 
import queue_pb2_grpc as queue_grpc

def run(args, input):
    channel = grpc.insecure_channel(args)
    stub = queue_grpc.QueueStub(channel)

    add_to_queue = stub.Put(queue.Item(input))
    print(add_to_queue.result)

    peek = stub.Peek(queue.Empty())
    print(peek.result)

    pop = stub.Pop(queue.Empty())
    print(pop.result)

    size = stub.Size(queue.Empty())
    print(size.result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address')
    args = parser.parse_args()
    while True:
        input = input()
        run(args.address, input)

