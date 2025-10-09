import socket

HOST = 'localhost'
PORT = 6000
FILENAME = 'D:\Github\socket_programming_computer_network\file.txt'


# UDP Server Code
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print("UDP Server listening...")

        while True:
            data, addr = server_socket.recvfrom(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")


# UDP Client Code
def udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        with open(FILENAME, 'r') as file:
            for line in file:
                client_socket.sendto(line.encode(), (HOST, PORT))
                print(f"Sent: {line.strip()}")


# Main function to start UDP Client or Server
if __name__ == "__main__":
    choice = input("Start as (s)erver or (c)lient? ")
    if choice.lower() == 's':
        udp_server()
    elif choice.lower() == 'c':
        udp_client()
    else:
        print("Invalid choice!")
