import socket
import argparse
import os

HOST = "0.0.0.0"

sessions = {}


class Session:

    def __init__(self, client_addr, filename, filesize):
        self.client_addr = client_addr
        self.chunk_num = 0
        self.filename = filename
        self.filesize = filesize
        self.received = 0
        self.expected_seqno = 1
        self.seqno = 0


def send_nack(addr, seqno):
    nack_message = f'n|{seqno}'.encode()
    s.sendto(nack_message, addr)


def send_ack(addr, seqno):
    ack_message = f'a|{seqno}'.encode()
    s.sendto(ack_message, addr)


def handle_start_message(data, addr, sessions):
    _, seqno, filename, filesize = data.decode().split('|')
    if (os.path.exists(filename)):
        print("Overwriting the filname....")
        os.remove(filename)
    print(f"{addr}: s|{seqno}|{filename}|{filesize}")
    if addr not in sessions:
        sessions[addr] = Session(addr, filename, int(filesize))
    send_ack(addr, sessions[addr].expected_seqno)


def handle_data_message(data, addr, sessions):
    if addr not in sessions:
        print(f"No session found for {addr}, ignoring data.")
        return

    session = sessions[addr]
    seqno = data[2:3].decode()
    seqno = int(seqno)
    session.chunk_num += 1
    print(f"{addr}: d|{seqno}|chunk{session.chunk_num}")

    if seqno != session.expected_seqno:
        print(f"Unexpected sequence number from {addr}. Expected "
              " {session.expected_seqno}, got {seqno}")
        send_ack(addr, session.expected_seqno)
        return

    with open(session.filename, 'ab') as file:
        file.write(data[4:])
    session.received += len(data[4:])

    # Update expected sequence number for next chunk
    session.expected_seqno = (seqno + 1) % 2

    # Send ack with the next expected sequence number
    send_ack(addr, session.expected_seqno)
    if session.received == session.filesize:
        print(f"({HOST}, {args.PORT}):    Received {session.filename}.")
        del sessions[addr]


# Create the parser object
parser = argparse.ArgumentParser(description='Parse two integer arguments from'
                                 ' the command line.')

# Add a positional argument
parser.add_argument('PORT', type=int, help='The port number to listen on.')

# Add an optional argument
parser.add_argument('MX_NUMBER_OF_CONNECTION', type=int, help='The maximum '
                    'number of simultaneously connected clients.')

# Parse the command line arguments
args = parser.parse_args()

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, args.PORT))
        print(f"({HOST}, {args.PORT}):    Listening...")
        while True:
            data, addr = s.recvfrom(20480)
            message_type = data[:1].decode()
            if message_type == 's':
                if len(sessions) >= args.MX_NUMBER_OF_CONNECTION:
                    send_nack(addr, 1)
                    continue
                handle_start_message(data, addr, sessions)
            elif message_type == 'd':
                handle_data_message(data, addr, sessions)
            else:
                print(f"Error: Unknown message type from {addr}: {data}. "
                      "Terminating server.")
                break  # Exit the while loop
except KeyboardInterrupt:
    print(f"({HOST}, {args.PORT}):  Shutting down...")
except Exception as e:
    print(f"An error occurred: {e}. Shutting down the server.")
finally:
    del sessions
    print(f"({HOST}, {args.PORT}):  Server has been shut down.")
