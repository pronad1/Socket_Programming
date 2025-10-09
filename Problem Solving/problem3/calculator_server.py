import socket

HOST = 'localhost'
PORT = 5000

# Function to perform the calculation
def perform_operation(num1, num2, operation):
    try:
        num1, num2 = int(num1), int(num2)
        if operation == '+':
            return str(num1 + num2)
        elif operation == '-':
            return str(num1 - num2)
        elif operation == '*':
            return str(num1 * num2)
        elif operation == '/':
            if num2 == 0:
                return "Error: Division by zero"
            return str(num1 / num2)
        elif operation == '%':
            if num2 == 0:
                return "Error: Division by zero"
            return str(num1 % num2)
        else:
            return "Error: Invalid operation"
    except ValueError:
        return "Error: Invalid input"

# Main server function
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Server is listening...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024).decode()
                if not data:
                    break

                # Parse the received data
                num1, num2, operation = data.split()
                result = perform_operation(num1, num2, operation)
                conn.sendall(result.encode())

if __name__ == "__main__":
    start_server()
