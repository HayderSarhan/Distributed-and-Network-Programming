import grpc
import sys
import zlib
from concurrent import futures
import chord_pb2_grpc as pb2_grpc
import chord_pb2 as pb2

node_id = int(sys.argv[1])

CHORD = [2, 16, 24, 25, 26, 31]
CHANNELS = [
    "127.0.0.1:5000",
    "127.0.0.1:5001",
    "127.0.0.1:5002",
    "127.0.0.1:5003",
    "127.0.0.1:5004",
    "127.0.0.1:5005",
]

data = {}
finger_table = []

def init_finger_table():
    for i in range(M):
        finger_table.append(find_successor((CHORD[node_id] + 2**i) % 2**M))

def find_successor(id):
    for node_id in CHORD:
        if node_id >= id:
            return node_id
    return CHORD[0]

def find_predecessor(id):
    for i in range(M-1, -1, -1):
        if CHORD[i] < id:
            return CHORD[i]
    return CHORD[-1]

M = 5
id = CHORD[node_id]
succ = CHORD[(node_id + 1) % len(CHORD)]
pred = CHORD[(node_id - 1) % len(CHORD)]


def get_stub(channel):
    channel = grpc.insecure_channel(channel)
    return pb2_grpc.ChordStub(channel)


def get_target_id(key):
    hash_value = zlib.adler32(key.encode())
    return hash_value % (2**M)



def save(key, text):
        target_id = get_target_id(key)
        if pred < target_id <= id:
            data[target_id] = text
            print(f'Node {id} says: Saved {key}')
            return id, True

        elif id < target_id <= succ:
            print(f'Node {id} says: Save from {id} to {succ}')
            succ_index = CHORD.index(succ)
            stub = get_stub(CHANNELS[succ_index])
            res = stub.SaveData(pb2.SaveDataMessage(key=key, text=text))
            return res.node_id, res.status

        else:
            closest_node = max(filter(lambda x: x < target_id, finger_table))
            print(f'Node {id} says: Save from {id} to {closest_node}')
            closest_node_index = CHORD.index(closest_node)
            stub = get_stub(CHANNELS[closest_node_index])
            res = stub.SaveData(pb2.SaveDataMessage(key=key, text=text))
            return res.node_id, res.status

def remove(key):
    target_id = get_target_id(key)
    if pred < target_id <= id:
        if target_id in data:
            data.pop(target_id)
            print(f'Node {id} says: Removed {key}')
            return id, True
        else:
            print(f'Node {id} says: {key} not found')
            return id, False

    elif id < target_id <= succ:
        print(f'Node {id} says: Remove from {id} to {succ}')
        succ_index = CHORD.index(succ)
        stub = get_stub(CHANNELS[succ_index])
        res = stub.RemoveData(pb2.RemoveDataMessage(key=key))
        return res.node_id, res.status

    else:
        closest_node = max(filter(lambda x: x < target_id, finger_table))
        print(f'Node {id} says: Remove from {id} to {closest_node}')
        closest_node_index = CHORD.index(closest_node)
        stub = get_stub(CHANNELS[closest_node_index])
        res = stub.RemoveData(pb2.RemoveDataMessage(key=key))
        return res.node_id, res.status



def find(key):
    target_id = get_target_id(key)
    if pred < target_id <= id:
        if target_id in data:
            print(f'Node {id} says: Found {key}')
            return id, data[target_id]

        else:
            print(f'Node {id} says: {key} not found')
            return id, ""

    elif id < target_id <= succ:
        print(f'Node {id} says: Find from {id} to {succ}')
        succ_index = CHORD.index(succ)
        stub = get_stub(CHANNELS[succ_index])
        res = stub.FindData(pb2.FindDataMessage(key=key))
        return res.node_id, res.data

    else:
        closest_node = max(filter(lambda x: x < target_id, finger_table))
        print(f'Node {id} says: Find from {id} to {closest_node}')
        closest_node_index = CHORD.index(closest_node)
        stub = get_stub(CHANNELS[closest_node_index])
        res = stub.FindData(pb2.FindDataMessage(key=key))
        return res.node_id, res.data


class NodeHandler(pb2_grpc.ChordServicer):
    def SaveData(self, request, context):
            try:
                key = request.key
                text = request.text
                node_id, status = save(key, text)
                reply = {"node_id": node_id, "status": status}
                return pb2.SaveDataResponse(**reply)

            except grpc.RpcError:
                return pb2.SaveDataResponse(node_id=-1, status=False)

    def RemoveData(self, request, context):
        try:
            key = request.key
            node_id, status = remove(key)
            reply = {"node_id": node_id, "status": status}
            return pb2.RemoveDataResponse(**reply)

        except grpc.RpcError:
            return pb2.RemoveDataResponse(node_id=-1, status=False)

    def FindData(self, request, context):
        try:
            key = request.key
            node_id, data = find(key)
            reply = {"node_id": node_id, "data": data}
            return pb2.FindDataResponse(**reply)

        except grpc.RpcError:
            return pb2.FindDataResponse(node_id=-1, data="")

    def GetFingerTable(self, request, context):
        try:
            reply = {"finger_table": finger_table}
            return pb2.GetFingerTableResponse(**reply)

        except grpc.RpcError:
            return pb2.GetFingerTableResponse(finger_table=[])

if __name__ == "__main__":
    node_port = str(5000 + int(node_id))
    node = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ChordServicer_to_server(NodeHandler(), node)
    node.add_insecure_port("127.0.0.1:" + node_port)
    node.start()

    try:
        init_finger_table()
        print(f'Node {id} finger table {finger_table}')
        node.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")
