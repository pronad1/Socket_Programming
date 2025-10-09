import socket
import os
import random
import time
import sys

def udp_server(filename, port):
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        return

    # Get the file size
    file_size = os.path.getsize(filename)
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', port)
    sock.bind(server_address)

    print(f"Server started at {server_address}. Waiting for client requests...")

    # Wait for client request
    data, client_address = sock.recvfrom(1024)
    print(f"Request from {client_address} to stream file: {filename}")

    try:
        # Send the file size first
        sock.sendto(str(file_size).encode(), client_address)
        print(f"Sent file size: {file_size} bytes")

        # Open the file in binary read mode
        with open(filename, 'rb') as f:
            while True:
                # Randomly determine chunk size between 1000 and 2000 bytes
                chunk_size = random.randint(1000, 2000)
                chunk = f.read(chunk_size)
                
                if not chunk:
                    # No more data to send, end of file reached
                    print("End of file reached. Sending EOF message.")
                    sock.sendto(b"EOF", client_address)  # Send an EOF message
                    break
                
                # Send the chunk to the client
                sock.sendto(chunk, client_address)
                print(f"Sent {len(chunk)} bytes to {client_address}")
                
                # Add a slight delay to simulate streaming
                time.sleep(0.1)
    finally:
        sock.close()
        print("Server socket closed. Exiting server.")
        sys.exit()  # Terminate the server program after sending

# Usage
filename = 'D:/Github/socket_programming_computer_network/problem4/file.mp4'  # Replace with the correct path to your multimedia file
port = 10000  # Port number
udp_server(filename, port)
