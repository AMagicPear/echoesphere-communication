import json
import socket
import threading
import time

from led_control.ws2812b_test import pixels

HOST = '0.0.0.0'
PORT = 65432

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            conn.sendall(b"Hello, client!")
            data = conn.recv(1024)
            if data:
                print(f"Received data from {addr}:")
                data_key_value = json.loads(data.decode())
                print(data_key_value)
                if "HitBlockColor" in data_key_value:
                    hit_block_color = data_key_value["HitBlockColor"]
                    match hit_block_color:
                        case "Red":
                            pixels.fill((255, 0, 0))
                        case "Green":
                            pixels.fill((0, 255, 0))
                        case "Blue":
                            pixels.fill((0, 0, 255))
                        case "Orange":
                            pixels.fill((255, 80, 0))
                        case _:
                            pixels.fill((0, 0, 0))
                    pixels.show()
            time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Connection closed with {addr}")

if __name__ == "__main__":
    start_server()