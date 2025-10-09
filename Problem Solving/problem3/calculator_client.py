import socket

HOST = 'localhost'
PORT = 5000

# Main client function
def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        # Get input from the user
        num1 = input("Enter the first integer: ")
        num2 = input("Enter the second integer: ")
        operation = input("Enter the arithmetic operation (+, -, *, /, %): ")

        # Send the data to the server
        data = f"{num1} {num2} {operation}"
        client_socket.sendall(data.encode())

        # Receive and display the result
        result = client_socket.recv(1024).decode()
        print(f"Result: {result}")

if __name__ == "__main__":
    start_client()
