import os
import socket
import time
from multiprocessing import Process
import threading
import queue

# URL of the server from which unsorted files will be downloaded
SERVER_URL = '127.0.0.1:12345'

# Buffer size for receiving data from the server
CLIENT_BUFFER = 1024

# Number of unsorted files to be downloaded
UNSORTED_FILES_COUNT = 100

# Queue for managing file numbers to be downloaded
file_queue = queue.Queue()

# List to store threads for file download
threads = []


def create_directories():
    """
    Create directories 'unsorted_files' and 'sorted_files' if they do not exist.
    """
    if not os.path.exists('unsorted_files'):
        os.mkdir('unsorted_files')

    if not os.path.exists('sorted_files'):
        os.mkdir('sorted_files')


def manage_threads():
    """
    Function to manage the threads for downloading unsorted files.
    """
    while True:
        try:
            file_number = file_queue.get_nowait()
        except queue.Empty:
            break
        download_unsorted_files(file_number)


def download_unsorted_files(file_number):
    """
    Function to download unsorted files from the server.

    Parameters:
        file_number (int): The number of the file to be downloaded.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip, port = SERVER_URL.split(':')
        s.connect((ip, int(port)))
        file = b''
        while True:
            packet = s.recv(CLIENT_BUFFER)
            if not packet:
                break
            file += packet
        with open(f'unsorted_files/{file_number}.txt', 'wb') as f:
            f.write(file)


def run_threads():
    """
    Function to run multiple threads for downloading unsorted files.
    """
    for index in range(UNSORTED_FILES_COUNT):
        file_queue.put(index)

    for _ in range(10):
        threads.append(threading.Thread(target=manage_threads))
    [t.start() for t in threads]
    [t.join() for t in threads]


def create_sorted_file(start, end):
    """
    Function to create sorted files from unsorted files.

    Parameters:
        start (int): Starting index of the range of unsorted files.
        end (int): Ending index of the range of unsorted files.
    """
    for unsorted_id in range(start, end):
        with open(f"unsorted_files/{unsorted_id}.txt", "r") as unsorted_file:
            # Split long expression into multiple lines
            unsorted_list = [
                int(number)
                for number in unsorted_file.read().split(',')
            ]

            sorted_list = sorted(unsorted_list)

            with open(f"sorted_files/{unsorted_id}.txt", "w") as sorted_file:
                sorted_file.write(','.join(map(str, sorted_list)))


def sorting_process():
    """
    Function to perform sorting of unsorted files using multiprocessing.
    """
    ranges_list = []
    processes = []
    cores = os.cpu_count()
    chunck = UNSORTED_FILES_COUNT // cores
    remaining_chunck = UNSORTED_FILES_COUNT % cores
    for index in range(remaining_chunck + 1):
        ranges_list.append((index * chunck) + index)

    for index in range(remaining_chunck + 1, cores + 1):
        ranges_list.append((index * chunck) + remaining_chunck)

    for index in range(cores + 1):
        if index == cores:
            break

        processes.append(Process(target=create_sorted_file, args=(
            ranges_list[index], ranges_list[index + 1],)))
    [p.start() for p in processes]
    [p.join() for p in processes]


if __name__ == '__main__':
    create_directories()

    # Time the download process
    tdownload0 = time.monotonic()
    run_threads()
    tdownload = time.monotonic() - tdownload0
    print(f"Files download time: {tdownload}")

    # Time the sorting process
    tsort0 = time.monotonic()
    sorting_process()
    tsort = time.monotonic() - tsort0
    print(f"Sorting time: {tsort}")
