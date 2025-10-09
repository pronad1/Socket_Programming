import socket
import threading

# Define the server address and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
ADDRESS = (SERVER_HOST, SERVER_PORT)

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Error receiving message. Connection may be closed.")
            client_socket.close()
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDRESS)
    
    # Start a thread to listen for incoming messages
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()
    
    while True:
        message = input()
        if message.lower() == 'exit':
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    main()
