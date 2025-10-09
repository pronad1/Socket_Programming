import socket


HOST = 'localhost'
PORT = 5000
FILENAME = 'D:/Github/socket_programming_computer_network/file.txt'


# TCP Server Code
def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("TCP Server listening for connections...")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received data:", data.decode())
                conn.sendall(b'ACK')  # Send acknowledgment


# TCP Client Code
def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        with open(FILENAME, 'rb') as file:
            while True:
                chunk = file.read(100)
                if not chunk:
                    break

                while True:
                    client_socket.sendall(chunk)
                    try:
                        client_socket.settimeout(2)  # Set timeout for acknowledgment
                        ack = client_socket.recv(1024)
                        if ack == b'ACK':
                            print("Received ACK, sending next chunk.")
                            break
                    except socket.timeout:
                        print("Timeout, retransmitting chunk.")


# Main function to start TCP Client or Server
if __name__ == "__main__":
    choice = input("Start as (s)erver or (c)lient? ")
    if choice.lower() == 's':
        tcp_server()
    elif choice.lower() == 'c':
        tcp_client()
    else:
        print("Invalid choice!")
