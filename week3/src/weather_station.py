import sys
import zmq
import time
import json
import random
from datetime import datetime

IP_ADD = '127.0.0.1'
DATA_PROCESSES_INPUT_PORT = 5555

def generate_humidity_temperature():
    humidity = round(random.uniform(40, 100), 1)
    temperature = round(random.uniform(5, 40), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps({"time": timestamp, "temperature": temperature, "humidity": humidity})

def generate_CO2():
    co2 = round(random.uniform(300, 500), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps({"time": timestamp, "co2": co2})

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{IP_ADD}:{DATA_PROCESSES_INPUT_PORT}")

    while True:
        try:
            weather = generate_humidity_temperature()
            print(f"Weather is sent from WS1 {weather}")
            socket.send_string(f"weather {weather}")
            time.sleep(2)
            co2 = generate_CO2()
            print(f"CO2 is sent from WS1 {co2}")
            socket.send_string(f"co2 {co2}")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Terminating weather station")
            break

if __name__ == '__main__':
    main()