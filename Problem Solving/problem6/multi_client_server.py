import socket
import threading

# Define the server address and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
ADDRESS = (SERVER_HOST, SERVER_PORT)

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDRESS)

# List to keep track of connected clients
clients = []

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    clients.append(client_socket)
    
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{client_address}] {message}")
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            break

    client_socket.close()
    print(f"[DISCONNECTED] {client_address} disconnected.")

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

def start_server():
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER_PORT}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()
