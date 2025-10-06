#!/usr/bin/env python3
"""
UDP Multimedia Streaming Server
Assignment 4: Streaming Client-Server Application

This server implementation:
- Uses UDP (connectionless) sockets
- Reads multimedia files in chunks of 1000-2000 bytes
- Sends data as datagram packets to clients
- Handles multiple client requests
- Implements packet sequencing for ordered delivery

Author: [Your Name]
Date: October 2025
Course: Computer Networks - Socket Programming
"""

import socket
import os
import random
import time
import struct
import threading
import json
from datetime import datetime


class UDPStreamingServer:
    def __init__(self, host='localhost', port=9999, media_directory='media_files'):
        """
        Initialize the UDP streaming server
        
        Args:
            host (str): Server host address
            port (int): Server port number
            media_directory (str): Directory containing media files
        """
        self.host = host
        self.port = port
        self.media_directory = media_directory
        self.server_socket = None
        self.running = False
        self.clients = {}  # Track active streaming sessions
        
        # Ensure media directory exists
        if not os.path.exists(self.media_directory):
            os.makedirs(self.media_directory)
            print(f"Created media directory: {self.media_directory}")
    
    def start_server(self):
        """Start the UDP streaming server"""
        try:
            # Create UDP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Bind socket to address
            self.server_socket.bind((self.host, self.port))
            self.running = True
            
            print(f"UDP Streaming Server started on {self.host}:{self.port}")
            print(f"Media directory: {os.path.abspath(self.media_directory)}")
            print("Available media files:")
            self.list_media_files()
            print("\\nWaiting for client requests...")
            print("Press Ctrl+C to stop the server\\n")
            
            while self.running:
                try:
                    # Receive request from client
                    data, client_address = self.server_socket.recvfrom(1024)
                    
                    # Process request in separate thread
                    request_thread = threading.Thread(
                        target=self.handle_client_request,
                        args=(data, client_address)
                    )
                    request_thread.daemon = True
                    request_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Error receiving data: {e}")
                        
        except socket.error as e:
            print(f"Error starting server: {e}")
        except KeyboardInterrupt:
            print("\\nServer shutdown requested by user")
        finally:
            self.stop_server()
    
    def handle_client_request(self, data, client_address):
        """
        Handle client request for media file
        
        Args:
            data (bytes): Request data from client
            client_address (tuple): Client address
        """
        try:
            # Decode request
            request = data.decode('utf-8')
            print(f"Request from {client_address}: {request}")
            
            if request.startswith("LIST"):
                # Send list of available files
                self.send_file_list(client_address)
            elif request.startswith("STREAM:"):
                # Extract filename from request
                filename = request.split(":", 1)[1].strip()
                self.stream_file(filename, client_address)
            else:
                # Invalid request
                error_msg = "ERROR: Invalid request format"
                self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
                
        except Exception as e:
            print(f"Error handling request from {client_address}: {e}")
            error_msg = f"ERROR: {str(e)}"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
    
    def send_file_list(self, client_address):
        """Send list of available media files to client"""
        try:
            files = []
            if os.path.exists(self.media_directory):
                for filename in os.listdir(self.media_directory):
                    if self.is_media_file(filename):
                        filepath = os.path.join(self.media_directory, filename)
                        size = os.path.getsize(filepath)
                        files.append({"name": filename, "size": size})
            
            file_list = json.dumps(files)
            response = f"FILES:{file_list}"
            self.server_socket.sendto(response.encode('utf-8'), client_address)
            
        except Exception as e:
            error_msg = f"ERROR: Failed to get file list - {str(e)}"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
    
    def stream_file(self, filename, client_address):
        """
        Stream media file to client in chunks
        
        Args:
            filename (str): Name of the media file to stream
            client_address (tuple): Client address
        """
        filepath = os.path.join(self.media_directory, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            error_msg = f"ERROR: File '{filename}' not found"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
            return
        
        # Check if it's a valid media file
        if not self.is_media_file(filename):
            error_msg = f"ERROR: '{filename}' is not a supported media file"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
            return
        
        try:
            file_size = os.path.getsize(filepath)
            print(f"Streaming '{filename}' ({file_size} bytes) to {client_address}")
            
            # Send file info first
            file_info = {
                "filename": filename,
                "size": file_size,
                "status": "START"
            }
            info_msg = f"INFO:{json.dumps(file_info)}"
            self.server_socket.sendto(info_msg.encode('utf-8'), client_address)
            
            # Stream file in chunks
            with open(filepath, 'rb') as file:
                sequence_number = 0
                bytes_sent = 0
                
                while bytes_sent < file_size:
                    # Random chunk size between 1000 and 2000 bytes
                    chunk_size = random.randint(1000, 2000)
                    
                    # Adjust chunk size for last packet if necessary
                    remaining_bytes = file_size - bytes_sent
                    if remaining_bytes < chunk_size:
                        chunk_size = remaining_bytes
                    
                    # Read chunk from file
                    chunk_data = file.read(chunk_size)
                    
                    if not chunk_data:
                        break
                    
                    # Create packet with header (sequence number, chunk size, data)
                    packet = self.create_data_packet(sequence_number, chunk_data, bytes_sent, file_size)
                    
                    # Send packet to client
                    self.server_socket.sendto(packet, client_address)
                    
                    bytes_sent += len(chunk_data)
                    sequence_number += 1
                    
                    # Progress logging
                    progress = (bytes_sent / file_size) * 100
                    print(f"Sent packet {sequence_number}: {len(chunk_data)} bytes "
                          f"({progress:.1f}% complete)")
                    
                    # Small delay to simulate network streaming
                    time.sleep(0.01)  # 10ms delay between packets
                
                # Send end-of-stream marker
                end_packet = self.create_end_packet(sequence_number)
                self.server_socket.sendto(end_packet, client_address)
                
                print(f"Streaming complete: {bytes_sent} bytes sent in {sequence_number} packets")
                
        except Exception as e:
            print(f"Error streaming file '{filename}' to {client_address}: {e}")
            error_msg = f"ERROR: Streaming failed - {str(e)}"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
    
    def create_data_packet(self, seq_num, data, bytes_sent, total_size):
        """
        Create a data packet with header information
        
        Args:
            seq_num (int): Sequence number
            data (bytes): Chunk data
            bytes_sent (int): Total bytes sent so far
            total_size (int): Total file size
            
        Returns:
            bytes: Formatted packet
        """
        # Packet format: [TYPE:1][SEQ:4][DATA_SIZE:4][BYTES_SENT:8][TOTAL_SIZE:8][DATA:variable]
        packet_type = b'D'  # Data packet
        header = struct.pack('!BII QQ', 
                           ord(packet_type), 
                           seq_num, 
                           len(data),
                           bytes_sent,
                           total_size)
        return header + data
    
    def create_end_packet(self, seq_num):
        """Create end-of-stream packet"""
        packet_type = b'E'  # End packet
        header = struct.pack('!BII QQ', 
                           ord(packet_type), 
                           seq_num, 
                           0, 0, 0)
        return header
    
    def is_media_file(self, filename):
        """
        Check if file is a supported media file
        
        Args:
            filename (str): Filename to check
            
        Returns:
            bool: True if it's a media file
        """
        media_extensions = {
            # Video files
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v',
            # Audio files
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            # Other multimedia
            '.gif', '.webp'
        }
        
        return any(filename.lower().endswith(ext) for ext in media_extensions)
    
    def list_media_files(self):
        """List all available media files"""
        if not os.path.exists(self.media_directory):
            print("  No media directory found")
            return
            
        media_files = []
        for filename in os.listdir(self.media_directory):
            if self.is_media_file(filename):
                filepath = os.path.join(self.media_directory, filename)
                size = os.path.getsize(filepath)
                media_files.append((filename, size))
        
        if media_files:
            for filename, size in media_files:
                size_mb = size / (1024 * 1024)
                print(f"  - {filename} ({size_mb:.2f} MB)")
        else:
            print("  No media files found")
            print(f"  Place media files in: {os.path.abspath(self.media_directory)}")
    
    def stop_server(self):
        """Stop the server and clean up resources"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("\\nUDP Streaming Server stopped")


def create_sample_media_info():
    """Create a sample media file info for testing"""
    sample_content = """This is a sample multimedia file content for testing the UDP streaming server.
This content simulates a media file that would be streamed to clients.

Imagine this is audio or video data that needs to be transmitted in chunks
and played back in real-time as it's being received.

The streaming protocol demonstrates:
- UDP connectionless communication
- Chunked data transmission
- Real-time streaming capabilities
- Packet sequencing and ordering
- Buffer management for smooth playback

This sample file helps test the streaming functionality without requiring
actual large media files during development and testing.
""" * 50  # Make it larger for better testing

    return sample_content.encode('utf-8')


def main():
    """Main function to start the streaming server"""
    import sys
    
    # Default values
    host = 'localhost'
    port = 9999
    media_dir = 'media_files'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 9999")
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    if len(sys.argv) > 3:
        media_dir = sys.argv[3]
    
    # Create sample media file if directory is empty
    abs_media_dir = os.path.abspath(media_dir)
    sample_file_path = os.path.join(abs_media_dir, "sample_media.txt")
    
    if not os.path.exists(abs_media_dir):
        os.makedirs(abs_media_dir)
    
    if not os.listdir(abs_media_dir):
        with open(sample_file_path, 'wb') as f:
            f.write(create_sample_media_info())
        print(f"Created sample media file: {sample_file_path}")
    
    # Create and start server
    server = UDPStreamingServer(host, port, media_dir)
    
    print("="*60)
    print("UDP MULTIMEDIA STREAMING SERVER")
    print("="*60)
    print(f"Server Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Media Directory: {abs_media_dir}")
    print("="*60)
    
    server.start_server()


if __name__ == "__main__":
    main()