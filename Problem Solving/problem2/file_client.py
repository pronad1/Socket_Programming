import socket

HOST = 'localhost'
PORT = 5000
OUTPUT_FILENAME = 'downloaded_file.txt'

# Main client function
def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        # Get the file name from user input
        file_name = input("Enter the name of the file to download: ")
        client_socket.sendall(file_name.encode())

        # Open the output file to save the downloaded content
        with open(OUTPUT_FILENAME, 'wb') as output_file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Check for error message
                if b"Error: File not found" in data:
                    print("Error: File not found on server.")
                    break
                output_file.write(data)
                print(f"Received {len(data)} bytes")

        print("File download complete")

if __name__ == "__main__":
    start_client()
