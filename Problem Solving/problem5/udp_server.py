import socket

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 9999))
    print("UDP server listening on port 9999...")
    
    while True:
        message, client_address = server.recvfrom(1024)
        message = message.decode('utf-8')
        print(f"Client: {message}")
        reply = input("You: ")
        server.sendto(reply.encode('utf-8'), client_address)

if __name__ == "__main__":
    main()
