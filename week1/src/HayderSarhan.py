import argparse
import socket
import os

HOST = "0.0.0.0"  # Listening on all available interfaces.
queue = []  # Queue for managing sessions.
chunks_num = 1  # Counter for tracking received chunks.

class Session:
    """Represents a session with a client for file transfer.

    Attributes:
        ip (str): Client's IP address.
        port (int): Client's port number.
        file_name (str): Name of the file being transferred.
        file_size (int): Size of the file in bytes.
    """

    def __init__(self, addr, file_info):
        """Initializes the session with the client's address and file information."""
        self.ip, self.port = addr
        self.file_name, self.file_size = file_info.split("|", 1)
        self.file_size = int(self.file_size)

    def __eq__(self, other):
        return (self.ip, self.port) == (other.ip, other.port)

    def get_addr(self):
        """Returns the client's address as a string."""
        return (self.ip, self.port)


    def get_file_name(self):
        """Returns the file name."""
        return self.file_name

    def get_file_size(self):
        """Returns the file size."""
        return self.file_size

    def left_data(self, chunk_size):
        """Updates the file size after receiving a chunk and returns the remaining size."""
        self.file_size -= chunk_size
        return self.file_size


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port_number", type=int, help="Port number to listen on.")
    parser.add_argument("max_number_of_connections", type=int, help="Maximum number of concurrent connections.")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, args.port_number))
        print(f"({HOST}, {args.port_number}): Listening...")

        try:
            while True:
                frame, addr = s.recvfrom(20480)
                message_type = frame[:1].decode()
                seqno = int(frame[2:3].decode())

                if message_type == "s":
                    if len(queue) < int(args.max_number_of_connections) and Session(addr, frame[4:].decode()) not in queue:
                        queue.append(Session(addr, frame[4:].decode()))
                        print(f"{queue[0].get_addr()}: {frame.decode()}")
                        seqno = (seqno + 1) % 2
                        ack = f"a|{seqno}".encode()
                        s.sendto(ack, addr)
                    else:
                        seqno = (seqno + 1) % 2
                        ack = f"n|{seqno}".encode()
                        s.sendto(ack, addr)

                elif message_type == "d":
                    print(f"{queue[0].get_addr()}: {frame[:4].decode(errors='ignore')}|chunk{chunks_num}")

                    if os.path.exists(queue[0].get_file_name()):
                        print(f"{s.getsockname()}: Overwriting {queue[0].get_file_name()}...")
                        os.remove(queue[0].get_file_name())

                    with open(queue[0].get_file_name(), "ab") as file:
                        file.write(frame[4:])

                    chunks_num += 1

                    if queue[0].left_data(len(frame[4:])) == 0:
                        print(f"{queue[0].get_addr()}: Received {queue[0].get_file_name()}")
                        queue.pop(0)
                        chunks_num = 1

                    seqno = (seqno + 1) % 2
                    ack = f"a|{seqno}".encode()
                    s.sendto(ack, addr)

                else:
                    print(f"{queue[0].get_addr()}: Unknown message type, exiting...")
                    exit()

        except KeyboardInterrupt:
            print(f"({HOST}, {args.port_number}): Shutting down...")