import socket
import threading
import time
import os

HOST = 'localhost'
PORT = 5000
BUFFER_SIZE = 1000  # Transfer size (max 1000 bytes)

# Function to handle client request in a separate thread
def handle_client(conn, addr):
    try:
        print(f"Connection from {addr}")
        # Receive the file name requested by the client
        file_name = conn.recv(1024).decode()
        if not os.path.exists(file_name):
            conn.sendall(b"Error: File not found")
            return

        # Open the requested file and send its contents
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                conn.sendall(data)
                print(f"Sent {len(data)} bytes to {addr}")
                time.sleep(0.2)  # Sleep for 200 milliseconds

        print(f"File transfer complete for {addr}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# Main server function
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Server is listening...")

        while True:
            conn, addr = server_socket.accept()
            # Start a new thread for each client connection
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
