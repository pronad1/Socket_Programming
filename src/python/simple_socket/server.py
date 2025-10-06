#!/usr/bin/env python3
"""
Simple TCP Server - Socket Programming Example
Author: [Your Name]
Date: October 2025

This is a basic TCP server implementation that demonstrates:
- Socket creation and binding
- Listening for client connections
- Message processing and response
- Error handling
"""

import socket
import sys
import threading
from datetime import datetime


class SimpleTCPServer:
    def __init__(self, host='localhost', port=12000):
        """
        Initialize the TCP server
        
        Args:
            host (str): Server host address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
    
    def start_server(self):
        """Start the TCP server and listen for connections"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Allow reuse of address
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind socket to address
            self.server_socket.bind((self.host, self.port))
            
            # Start listening (max 5 pending connections)
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Server listening on {self.host}:{self.port}")
            print("Waiting for client connections...")
            print("Press Ctrl+C to stop the server")
            
            while self.running:
                try:
                    # Accept client connection
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Connection established with {client_address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:  # Only print error if server is supposed to be running
                        print(f"Error accepting connection: {e}")
                        
        except socket.error as e:
            print(f"Error starting server: {e}")
        except KeyboardInterrupt:
            print("\nServer shutdown requested by user")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        """
        Handle communication with a connected client
        
        Args:
            client_socket: Client socket object
            client_address: Client address tuple
        """
        try:
            while self.running:
                # Receive message from client
                message = client_socket.recv(1024).decode('utf-8')
                
                if not message:
                    break
                    
                print(f"Received from {client_address}: {message}")
                
                # Process message (convert to uppercase as example)
                response = self.process_message(message)
                
                # Send response back to client
                client_socket.send(response.encode('utf-8'))
                
        except socket.error as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            print(f"Closing connection with {client_address}")
            client_socket.close()
    
    def process_message(self, message):
        """
        Process received message and generate response
        
        Args:
            message (str): Message received from client
            
        Returns:
            str: Response message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simple echo server that converts to uppercase
        if message.lower() == 'quit':
            return "Goodbye!"
        elif message.lower() == 'time':
            return f"Server time: {timestamp}"
        else:
            return f"[{timestamp}] Echo: {message.upper()}"
    
    def stop_server(self):
        """Stop the server and clean up resources"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped")


def main():
    """Main function to start the server"""
    # Default values
    host = 'localhost'
    port = 12000
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 12000")
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    # Create and start server
    server = SimpleTCPServer(host, port)
    server.start_server()


if __name__ == "__main__":
    main()