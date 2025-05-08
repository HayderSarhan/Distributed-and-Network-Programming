import socket
import random
import threading

HOST = '127.0.0.1'
PORT = 12345

def server():
    """
    Function to start the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {(HOST, PORT)}")
        try:
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_connection, args=(conn, addr, )).start()

        except KeyboardInterrupt:
            print(f"Shutting down...")

def handle_connection(conn, addr):
    """
    Function to handle client connections.

    Parameters:
        conn (socket): Client socket connection.
    """
    with conn:
        numbers_list = generate_random_numbers_list()
        conn.sendall(numbers_list.encode())
        print(f"Sent a file to {addr}")
        conn.close()

def generate_random_numbers_list():
    """
    Function to generate a list of random numbers.

    Returns:
        str: Comma-separated string of random numbers.
    """
    numbers_list = []
    for _ in range(250000):
        numbers_list.append(str(random.randint(-999999999, 999999999)))
    return ','.join(numbers_list)

if __name__ == '__main__':
    server()
