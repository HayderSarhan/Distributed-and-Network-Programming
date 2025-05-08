import zmq
import json
import sys

IP_ADD = '127.0.0.1'
WEATHER_INPUT_PORT= 5555


def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "co2")

    while True:
        try:
            data = socket.recv_string()
            json_data = data.split("co2 ")[1]
            co2 = json.loads(json_data)
            with open('co2_data.log', 'a') as file:
                print(f"Received weather data: {data}")
                file.write(f"{data}\n")
                if co2['co2'] > 400:
                    print("Danger Zone! Please do not leave home")

        except KeyboardInterrupt:
            print("Terminating data_processor")
            file.close()
            socket.close()
            context.term()
            break


if __name__ == "__main__":
    main()

