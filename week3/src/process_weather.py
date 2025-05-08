import zmq
import json
import sys
import threading
from datetime import datetime, timedelta

WEATHER_INPUT_PORT= 5555
FASHION_SOCKET_PORT = 5556

IP_ADD = '127.0.0.1'

latest_data = {}
temp_hum = {}


def average_temperature_humidity():
    global latest_data, temp_hum
    threshold_time = datetime.now() - timedelta(seconds=30)
    parsed_data = {time: values for time, values in temp_hum.items() if time >= threshold_time}
    temperatures = [values[0] for values in parsed_data.values()]
    humidities = [values[1] for values in parsed_data.values()]

    average_temp = round(sum(temperatures) / len(temperatures), 2)
    average_hum = round(sum(humidities) / len(humidities), 2)

    latest_data['average-temp'] = average_temp
    latest_data['average-hum'] = average_hum


def recommendation():
    result = ""
    average_temperature_humidity()
    if latest_data['average-temp'] <10:
        result = "Today weather is cold. Its better to wear warm clothes"
    elif latest_data['average-temp'] >10 and latest_data['average-temp'] <25:
        result = "Feel free to wear spring/autumn clothes"
    else:
        result = "Go for light clothes"
    print(result)
    return result

def report():
    average_temperature_humidity()
    result = f"The last 30 sec average Temperature is {latest_data['average-temp']} and Humidity {latest_data['average-hum']}"
    print(result)
    return result

def data_from_station():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "weather")
    while True:
        try:
            data = socket.recv_string()
            json_data = data.split("weather ")[1]
            weather = json.loads(json_data)
            weather_time = datetime.strptime(weather['time'], "%Y-%m-%d %H:%M:%S")
            temp_hum[weather_time] = (weather['temperature'], weather['humidity'])
            with open('weather_data.log', 'a') as file:
                print(f"Received weather data: {data}")
                file.write(f"{data}\n")

        except KeyboardInterrupt:
            print("Terminating data_processor")
            file.close()
            socket.close()
            context.term()
            break

def handle_requests():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{IP_ADD}:{FASHION_SOCKET_PORT}")
    while True:
        try:
            query = socket.recv_string()

            if query == "Fashion":
                response = recommendation()
                socket.send_string(response)

            elif query == "Weather":
                response = report()
                socket.send_string(response)

            else:
                socket.send_string("Invalid query. Please enter 'Fashion' or 'Weather'.")

        except KeyboardInterrupt:
            print("Terminating data_processor")
            socket.close()
            context.term()
            break


def main():

    try:
        handle_requests_thread = threading.Thread(target=handle_requests, daemon=True)
        data_from_station_thread = threading.Thread(target=data_from_station, daemon=True)

        data_from_station_thread.start()
        handle_requests_thread.start()

        # keep the main running, otherwise it ends and kills the daemon threads
        # I used this since join() blocks main while the thread is running and
        # would not allow the KeyboardInterrupt to be caught
        while True:
            continue

    except KeyboardInterrupt:
        print("Terminating data_processor")

if __name__ == "__main__":
    main()

