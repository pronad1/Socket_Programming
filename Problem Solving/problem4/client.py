import socket
import sys

def udp_client(server_address, port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Send request to the server to start streaming
    message = b'Start streaming'
    sock.sendto(message, (server_address, port))
    
    # File to save received data
    output_file = 'received_file.mp4'  # File to save the received data

    print(f"Receiving data from server {server_address}:{port}...")
    
    # Receive the file size first
    data, _ = sock.recvfrom(1024)
    expected_file_size = int(data.decode())
    print(f"Expected file size: {expected_file_size} bytes")
    
    # Track total bytes received
    total_bytes_received = 0
    playback_started = False

    # Open file to write received data
    with open(output_file, 'wb') as f:
        while True:
            data, _ = sock.recvfrom(2048)  # Receive data from the server
            
            if data == b"EOF":
                print("Received EOF message. Transmission complete.")
                break

            # Write the received chunk to file and update the counter
            f.write(data)
            total_bytes_received += len(data)
            print(f"Received {len(data)} bytes, total received: {total_bytes_received} bytes")

            # Start playback once 50 KB is received (optional)
            if total_bytes_received >= 50000 and not playback_started:
                playback_started = True
                print("Enough data received to start playback.")
                # Here, you would typically launch a media player, e.g.:
                # os.system(f"vlc {output_file} &")

            # Check if we have received the full file
            if total_bytes_received >= expected_file_size:
                print("Full file received successfully.")
                break

    sock.close()
    print("Client socket closed. Exiting client.")
    sys.exit()  # Terminate the client program after receiving

# Usage
server_address = 'localhost'
port = 10000
udp_client(server_address, port)
