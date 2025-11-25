import socket
import threading
import time

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
            if not data:
                break
            print(f"Received data from {addr}: {data.decode()}")
            time.sleep(0.01)
    except ConnectionResetError:
        print(f"Connection reset by {addr}")
    finally:
        conn.close()
        print(f"Connection closed with {addr}")

if __name__ == "__main__":
    start_server()