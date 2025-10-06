#!/usr/bin/env python3
"""
Simple TCP Client - Socket Programming Example
Author: [Your Name]
Date: October 2025

This is a basic TCP client implementation that demonstrates:
- Socket creation and connection
- Sending messages to server
- Receiving and displaying responses
- Error handling and reconnection
"""

import socket
import sys
import time


class SimpleTCPClient:
    def __init__(self, server_host='localhost', server_port=12000):
        """
        Initialize the TCP client
        
        Args:
            server_host (str): Server host address
            server_port (int): Server port number
        """
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.connected = False
    
    def connect_to_server(self):
        """Establish connection to the server"""
        try:
            # Create TCP socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set connection timeout
            self.client_socket.settimeout(10)
            
            print(f"Connecting to server at {self.server_host}:{self.server_port}")
            
            # Connect to server
            self.client_socket.connect((self.server_host, self.server_port))
            self.connected = True
            
            print(f"Successfully connected to server at {self.server_host}:{self.server_port}")
            return True
            
        except socket.timeout:
            print("Connection timeout. Server may not be running.")
            return False
        except socket.error as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def send_message(self, message):
        """
        Send message to server and receive response
        
        Args:
            message (str): Message to send
            
        Returns:
            str: Server response or None if error
        """
        if not self.connected:
            print("Not connected to server")
            return None
            
        try:
            # Send message to server
            self.client_socket.send(message.encode('utf-8'))
            
            # Receive response from server
            response = self.client_socket.recv(1024).decode('utf-8')
            return response
            
        except socket.error as e:
            print(f"Error communicating with server: {e}")
            self.connected = False
            return None
    
    def interactive_mode(self):
        """Run client in interactive mode"""
        print("\\nInteractive mode started")
        print("Commands:")
        print("  - Type any message to send to server")
        print("  - 'time' to get server time")
        print("  - 'quit' to disconnect")
        print("  - 'exit' to quit client")
        print("-" * 40)
        
        while self.connected:
            try:
                # Get user input
                user_input = input("Enter message: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    break
                
                # Send message and get response
                response = self.send_message(user_input)
                
                if response:
                    print(f"Server response: {response}")
                    
                    # Check if server sent goodbye message
                    if "goodbye" in response.lower():
                        print("Server closed the connection")
                        break
                else:
                    print("Failed to get response from server")
                    break
                    
            except KeyboardInterrupt:
                print("\\nClient interrupted by user")
                break
            except EOFError:
                print("\\nInput stream closed")
                break
    
    def send_single_message(self, message):
        """
        Send a single message and return response
        
        Args:
            message (str): Message to send
            
        Returns:
            str: Server response
        """
        if self.connect_to_server():
            response = self.send_message(message)
            self.disconnect()
            return response
        return None
    
    def disconnect(self):
        """Disconnect from server and clean up"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.connected = False
        print("Disconnected from server")


def main():
    """Main function to start the client"""
    # Default values
    host = 'localhost'
    port = 12000
    message = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Using default port 12000")
    
    if len(sys.argv) > 3:
        message = ' '.join(sys.argv[3:])
    
    # Create client
    client = SimpleTCPClient(host, port)
    
    try:
        if message:
            # Single message mode
            print(f"Sending single message: '{message}'")
            response = client.send_single_message(message)
            if response:
                print(f"Server response: {response}")
            else:
                print("Failed to send message")
        else:
            # Interactive mode
            if client.connect_to_server():
                client.interactive_mode()
            else:
                print("Failed to connect to server")
    
    except KeyboardInterrupt:
        print("\\nClient terminated by user")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()