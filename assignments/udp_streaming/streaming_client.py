#!/usr/bin/env python3
"""
UDP Multimedia Streaming Client
Assignment 4: Streaming Client-Server Application

This client implementation:
- Uses UDP (connectionless) sockets
- Requests multimedia files from streaming server
- Receives data in datagram packets
- Buffers received data for smooth playback
- Launches media player when sufficient data is received
- Supports real-time streaming during download

Author: Prosenjit Mondol
Date: October 2025
Course: Computer Networks - Socket Programming
"""

import socket
import os
import struct
import threading
import time
import json
import subprocess
import platform
from collections import defaultdict
from datetime import datetime


class UDPStreamingClient:
    def __init__(self, server_host='localhost', server_port=9999, buffer_dir='client_buffer'):
        """
        Initialize the UDP streaming client
        
        Args:
            server_host (str): Server host address
            server_port (int): Server port number
            buffer_dir (str): Directory for buffering received files
        """
        self.server_host = server_host
        self.server_port = server_port
        self.buffer_dir = buffer_dir
        self.client_socket = None
        self.receiving = False
        
        # Streaming state
        self.current_file = None
        self.expected_size = 0
        self.received_bytes = 0
        self.packets_received = 0
        self.packets_buffer = {}  # For handling out-of-order packets
        self.sequence_expected = 0
        self.streaming_complete = False
        
        # Media player state
        self.media_player_launched = False
        self.playback_threshold = 50000  # Bytes to buffer before starting playback
        
        # Ensure buffer directory exists
        if not os.path.exists(self.buffer_dir):
            os.makedirs(self.buffer_dir)
    
    def connect_to_server(self):
        """Establish UDP connection to server"""
        try:
            # Create UDP socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Set timeout for receiving packets
            self.client_socket.settimeout(30)  # 30 second timeout
            
            print(f"Connected to streaming server at {self.server_host}:{self.server_port}")
            return True
            
        except socket.error as e:
            print(f"Failed to create socket: {e}")
            return False
    
    def request_file_list(self):
        """Request list of available media files from server"""
        try:
            # Send list request
            request = "LIST"
            self.client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Receive response
            data, _ = self.client_socket.recvfrom(4096)
            response = data.decode('utf-8')
            
            if response.startswith("FILES:"):
                file_data = response[6:]  # Remove "FILES:" prefix
                files = json.loads(file_data)
                return files
            else:
                print(f"Server error: {response}")
                return []
                
        except socket.timeout:
            print("Timeout waiting for file list")
            return []
        except Exception as e:
            print(f"Error requesting file list: {e}")
            return []
    
    def display_available_files(self, files):
        """Display available files to user"""
        if not files:
            print("No media files available on server")
            return
        
        print("\\nAvailable media files:")
        print("-" * 50)
        for i, file_info in enumerate(files, 1):
            name = file_info['name']
            size = file_info['size']
            size_mb = size / (1024 * 1024)
            print(f"{i:2d}. {name} ({size_mb:.2f} MB)")
        print("-" * 50)
    
    def request_media_file(self, filename):
        """
        Request a specific media file from server
        
        Args:
            filename (str): Name of the media file to request
        """
        try:
            print(f"\\nRequesting media file: {filename}")
            
            # Reset streaming state
            self.current_file = filename
            self.received_bytes = 0
            self.packets_received = 0
            self.packets_buffer = {}
            self.sequence_expected = 0
            self.streaming_complete = False
            self.media_player_launched = False
            
            # Send streaming request
            request = f"STREAM:{filename}"
            self.client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Start receiving in separate thread
            self.receiving = True
            receive_thread = threading.Thread(target=self.receive_stream)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Monitor streaming progress
            self.monitor_streaming_progress()
            
        except Exception as e:
            print(f"Error requesting media file: {e}")
    
    def receive_stream(self):
        """Receive streaming data from server"""
        buffer_file_path = os.path.join(self.buffer_dir, self.current_file)
        
        try:
            with open(buffer_file_path, 'wb') as buffer_file:
                while self.receiving and not self.streaming_complete:
                    try:
                        # Receive packet from server
                        data, server_addr = self.client_socket.recvfrom(65536)
                        
                        if data.startswith(b"ERROR:"):
                            error_msg = data.decode('utf-8')
                            print(f"\\nServer error: {error_msg}")
                            break
                        elif data.startswith(b"INFO:"):
                            # Handle file info
                            info_data = data[5:].decode('utf-8')
                            file_info = json.loads(info_data)
                            self.expected_size = file_info['size']
                            print(f"Starting to receive: {file_info['filename']} ({self.expected_size} bytes)")
                            continue
                        
                        # Parse data packet
                        packet_info = self.parse_data_packet(data)
                        
                        if packet_info['type'] == 'DATA':
                            self.handle_data_packet(packet_info, buffer_file)
                        elif packet_info['type'] == 'END':
                            print("\\nReceived end-of-stream marker")
                            self.streaming_complete = True
                            break
                            
                    except socket.timeout:
                        print("\\nTimeout waiting for data")
                        break
                    except Exception as e:
                        print(f"\\nError receiving packet: {e}")
                        break
                
        except Exception as e:
            print(f"Error creating buffer file: {e}")
        finally:
            self.receiving = False
    
    def parse_data_packet(self, data):
        """
        Parse received data packet
        
        Args:
            data (bytes): Raw packet data
            
        Returns:
            dict: Parsed packet information
        """
        try:
            # Packet format: [TYPE:1][SEQ:4][DATA_SIZE:4][BYTES_SENT:8][TOTAL_SIZE:8][DATA:variable]
            if len(data) < 21:  # Minimum header size
                return {'type': 'INVALID'}
            
            packet_type_byte, seq_num, data_size, bytes_sent, total_size = struct.unpack('!BII QQ', data[:21])
            packet_type = chr(packet_type_byte)
            
            if packet_type == 'D':  # Data packet
                packet_data = data[21:21+data_size]
                return {
                    'type': 'DATA',
                    'sequence': seq_num,
                    'data_size': data_size,
                    'bytes_sent': bytes_sent,
                    'total_size': total_size,
                    'data': packet_data
                }
            elif packet_type == 'E':  # End packet
                return {
                    'type': 'END',
                    'sequence': seq_num
                }
            else:
                return {'type': 'UNKNOWN'}
                
        except Exception as e:
            print(f"Error parsing packet: {e}")
            return {'type': 'INVALID'}
    
    def handle_data_packet(self, packet_info, buffer_file):
        """
        Handle received data packet
        
        Args:
            packet_info (dict): Parsed packet information
            buffer_file: Open file handle for buffering
        """
        seq_num = packet_info['sequence']
        data = packet_info['data']
        
        # Write data to buffer file (in sequence order)
        if seq_num == self.sequence_expected:
            # Expected packet - write immediately
            buffer_file.write(data)
            buffer_file.flush()
            
            self.received_bytes += len(data)
            self.packets_received += 1
            self.sequence_expected += 1
            
            # Check if we have buffered packets to write
            while self.sequence_expected in self.packets_buffer:
                buffered_data = self.packets_buffer.pop(self.sequence_expected)
                buffer_file.write(buffered_data)
                buffer_file.flush()
                self.received_bytes += len(buffered_data)
                self.sequence_expected += 1
        else:
            # Out-of-order packet - buffer it
            self.packets_buffer[seq_num] = data
            self.packets_received += 1
        
        # Check if we should launch media player
        if (not self.media_player_launched and 
            self.received_bytes >= self.playback_threshold and 
            self.expected_size > 0):
            self.launch_media_player()
    
    def launch_media_player(self):
        """Launch media player for buffered content"""
        if self.media_player_launched:
            return
        
        self.media_player_launched = True
        buffer_file_path = os.path.join(self.buffer_dir, self.current_file)
        
        print(f"\\n🎬 Launching media player with {self.received_bytes} bytes buffered...")
        
        try:
            # Determine appropriate media player based on OS
            system = platform.system().lower()
            
            if system == "windows":
                # Try Windows Media Player or default association
                try:
                    os.startfile(buffer_file_path)
                    print("✅ Media player launched successfully")
                except:
                    subprocess.Popen(['start', buffer_file_path], shell=True)
            elif system == "darwin":  # macOS
                subprocess.Popen(['open', buffer_file_path])
                print("✅ Media player launched successfully")
            elif system == "linux":
                # Try common Linux media players
                players = ['vlc', 'mpv', 'mplayer', 'totem', 'xdg-open']
                for player in players:
                    try:
                        subprocess.Popen([player, buffer_file_path])
                        print(f"✅ Media player ({player}) launched successfully")
                        break
                    except FileNotFoundError:
                        continue
                else:
                    print("❌ No suitable media player found")
            else:
                print(f"❌ Media player launch not supported on {system}")
                
        except Exception as e:
            print(f"❌ Error launching media player: {e}")
    
    def monitor_streaming_progress(self):
        """Monitor and display streaming progress"""
        start_time = time.time()
        last_update = 0
        
        while self.receiving and not self.streaming_complete:
            time.sleep(0.5)  # Update every 500ms
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if self.expected_size > 0:
                progress = (self.received_bytes / self.expected_size) * 100
                
                # Calculate speed
                if elapsed_time > 0:
                    speed_bps = self.received_bytes / elapsed_time
                    speed_kbps = speed_bps / 1024
                    
                    # Estimate remaining time
                    if speed_bps > 0:
                        remaining_bytes = self.expected_size - self.received_bytes
                        eta_seconds = remaining_bytes / speed_bps
                        eta_minutes = eta_seconds / 60
                    else:
                        eta_minutes = 0
                    
                    # Display progress (update every 2 seconds to avoid spam)
                    if current_time - last_update >= 2.0:
                        print(f"\\rProgress: {progress:.1f}% "
                              f"({self.received_bytes}/{self.expected_size} bytes) "
                              f"Speed: {speed_kbps:.1f} KB/s "
                              f"ETA: {eta_minutes:.1f}min "
                              f"Packets: {self.packets_received}", end='', flush=True)
                        last_update = current_time
        
        # Final progress report
        if self.streaming_complete:
            elapsed_time = time.time() - start_time
            avg_speed = self.received_bytes / elapsed_time if elapsed_time > 0 else 0
            avg_speed_kbps = avg_speed / 1024
            
            print(f"\\n\\n✅ Streaming completed!")
            print(f"📊 Statistics:")
            print(f"   - Total bytes received: {self.received_bytes:,}")
            print(f"   - Total packets: {self.packets_received}")
            print(f"   - Total time: {elapsed_time:.2f} seconds")
            print(f"   - Average speed: {avg_speed_kbps:.1f} KB/s")
            print(f"   - Buffer file: {os.path.join(self.buffer_dir, self.current_file)}")
    
    def interactive_mode(self):
        """Run client in interactive mode"""
        print("\\n" + "="*60)
        print("UDP MULTIMEDIA STREAMING CLIENT")
        print("="*60)
        
        while True:
            try:
                print("\\nOptions:")
                print("1. List available media files")
                print("2. Stream a media file")
                print("3. Exit")
                
                choice = input("\\nEnter your choice (1-3): ").strip()
                
                if choice == '1':
                    print("\\nFetching file list from server...")
                    files = self.request_file_list()
                    self.display_available_files(files)
                
                elif choice == '2':
                    # First get file list
                    files = self.request_file_list()
                    if not files:
                        print("No files available or server error")
                        continue
                    
                    self.display_available_files(files)
                    
                    try:
                        selection = input("\\nEnter file number or filename: ").strip()
                        
                        # Check if it's a number
                        if selection.isdigit():
                            file_index = int(selection) - 1
                            if 0 <= file_index < len(files):
                                filename = files[file_index]['name']
                            else:
                                print("Invalid file number")
                                continue
                        else:
                            # Assume it's a filename
                            filename = selection
                        
                        # Request the file
                        self.request_media_file(filename)
                        
                    except ValueError:
                        print("Invalid selection")
                        continue
                
                elif choice == '3':
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\\n\\nClient interrupted by user")
                break
            except EOFError:
                print("\\n\\nInput stream closed")
                break
    
    def disconnect(self):
        """Disconnect from server and clean up"""
        self.receiving = False
        if self.client_socket:
            self.client_socket.close()
        print("\\nDisconnected from server")


def main():
    """Main function to start the streaming client"""
    import sys
    
    # Default values
    server_host = 'localhost'
    server_port = 9999
    buffer_dir = 'client_buffer'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Using default port 9999")
    
    if len(sys.argv) > 3:
        buffer_dir = sys.argv[3]
    
    # Create client
    client = UDPStreamingClient(server_host, server_port, buffer_dir)
    
    try:
        if client.connect_to_server():
            client.interactive_mode()
        else:
            print("Failed to connect to server")
    
    except KeyboardInterrupt:
        print("\\n\\nClient terminated by user")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()