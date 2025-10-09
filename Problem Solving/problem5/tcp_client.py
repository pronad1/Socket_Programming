import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))
    
    while True:
        message = input("You: ")
        client.send(message.encode('utf-8'))
        reply = client.recv(1024).decode('utf-8')
        print(f"Server: {reply}")

if __name__ == "__main__":
    main()
