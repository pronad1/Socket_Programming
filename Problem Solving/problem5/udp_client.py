import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 9999)
    
    while True:
        message = input("You: ")
        client.sendto(message.encode('utf-8'), server_address)
        reply, _ = client.recvfrom(1024)
        reply = reply.decode('utf-8')
        print(f"Server: {reply}")

if __name__ == "__main__":
    main()
