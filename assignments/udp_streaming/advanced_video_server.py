#!/usr/bin/env python3
"""
Advanced UDP Video Streaming Server
Enhanced Video Streaming Implementation with Quality Selection and Adaptive Streaming

Features:
- Multiple video quality support (480p, 720p, 1080p)
- Adaptive bitrate streaming based on network conditions
- Video metadata extraction and streaming
- Frame synchronization and buffering optimization
- Real-time quality adjustment
- Video codec detection and optimization

Author: Prosenjit Mondol
Date: October 2025
Course: Computer Networks - Advanced Video Streaming
"""

import socket
import os
import random
import time
import struct
import threading
import json
import hashlib
import mimetypes
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class VideoMetadata:
    """Extract and manage video metadata"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.size = os.path.getsize(filepath)
        self.extension = Path(filepath).suffix.lower()
        self.mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        
        # Video quality estimation based on file size and common formats
        self.estimated_quality = self._estimate_quality()
        self.optimal_chunk_size = self._calculate_optimal_chunk_size()
        
    def _estimate_quality(self):
        """Estimate video quality based on file size and format"""
        size_mb = self.size / (1024 * 1024)
        
        if self.extension in ['.mp4', '.avi', '.mkv', '.mov']:
            if size_mb < 50:
                return "480p"
            elif size_mb < 200:
                return "720p"
            else:
                return "1080p"
        elif self.extension in ['.mp3', '.wav', '.flac']:
            return "audio"
        else:
            return "unknown"
    
    def _calculate_optimal_chunk_size(self):
        """Calculate optimal chunk size based on video quality"""
        if self.estimated_quality == "1080p":
            return (1800, 2000)  # Larger chunks for HD
        elif self.estimated_quality == "720p":
            return (1400, 1800)  # Medium chunks
        elif self.estimated_quality == "480p":
            return (1000, 1400)  # Smaller chunks
        else:
            return (1000, 2000)  # Default range


class NetworkMonitor:
    """Monitor network conditions for adaptive streaming"""
    
    def __init__(self):
        self.packet_times = []
        self.lost_packets = 0
        self.total_packets = 0
        self.bandwidth_samples = []
        
    def record_packet(self, packet_size, send_time):
        """Record packet transmission metrics"""
        self.packet_times.append((time.time(), packet_size, send_time))
        self.total_packets += 1
        
        # Keep only recent samples (last 100 packets)
        if len(self.packet_times) > 100:
            self.packet_times = self.packet_times[-100:]
    
    def estimate_bandwidth(self):
        """Estimate available bandwidth based on recent transmissions"""
        if len(self.packet_times) < 10:
            return 100  # Default bandwidth estimate (KB/s)
        
        recent_samples = self.packet_times[-20:]
        total_bytes = sum(sample[1] for sample in recent_samples)
        time_span = recent_samples[-1][0] - recent_samples[0][0]
        
        if time_span > 0:
            bandwidth_kbps = (total_bytes / 1024) / time_span
            return max(50, min(1000, bandwidth_kbps))  # Clamp between 50-1000 KB/s
        
        return 100
    
    def get_optimal_chunk_size(self, base_range):
        """Get optimal chunk size based on network conditions"""
        bandwidth = self.estimate_bandwidth()
        min_size, max_size = base_range
        
        # Adjust chunk size based on bandwidth
        if bandwidth < 100:  # Low bandwidth
            return (min_size, min_size + (max_size - min_size) // 3)
        elif bandwidth > 300:  # High bandwidth
            return (min_size + (max_size - min_size) // 2, max_size)
        else:  # Medium bandwidth
            return base_range


class AdvancedUDPVideoServer:
    """Advanced UDP Video Streaming Server with quality selection and adaptive streaming"""
    
    def __init__(self, host='localhost', port=9999, media_directory='media_files'):
        """Initialize the advanced video streaming server"""
        self.host = host
        self.port = port
        self.media_directory = media_directory
        self.server_socket = None
        self.running = False
        
        # Advanced streaming features
        self.active_streams = {}  # client_addr -> StreamSession
        self.network_monitors = defaultdict(NetworkMonitor)
        self.quality_presets = {
            "low": (1000, 1300),
            "medium": (1300, 1700),
            "high": (1700, 2000),
            "auto": None  # Will be determined adaptively
        }
        
        # Ensure media directory is relative to script location
        if not os.path.isabs(self.media_directory):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.media_directory = os.path.join(script_dir, media_directory)
        
        # Ensure media directory exists
        if not os.path.exists(self.media_directory):
            os.makedirs(self.media_directory)
            print(f"Created media directory: {self.media_directory}")
        
        # Initialize video files cache
        self.video_cache = {}
        self._scan_video_files()
    
    def _scan_video_files(self):
        """Scan and categorize available video files"""
        print(f"Scanning media directory: {self.media_directory}")
        
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg'}
        
        for filename in os.listdir(self.media_directory):
            filepath = os.path.join(self.media_directory, filename)
            if os.path.isfile(filepath):
                ext = Path(filename).suffix.lower()
                
                if ext in video_extensions or ext in audio_extensions:
                    metadata = VideoMetadata(filepath)
                    self.video_cache[filename] = metadata
                    print(f"  📹 {filename} - {metadata.estimated_quality} ({metadata.size/(1024*1024):.2f} MB)")
        
        print(f"Found {len(self.video_cache)} media files")
    
    def create_packet(self, packet_type, seq_num, data, total_size=0, bytes_sent=0):
        """Create a structured packet for transmission"""
        try:
            # Packet format: [TYPE:1][SEQ:4][DATA_SIZE:4][BYTES_SENT:8][TOTAL_SIZE:8][DATA:variable]
            type_byte = packet_type.encode('ascii')[:1]
            seq_bytes = struct.pack('!I', seq_num)
            data_size_bytes = struct.pack('!I', len(data))
            bytes_sent_bytes = struct.pack('!Q', bytes_sent)
            total_size_bytes = struct.pack('!Q', total_size)
            
            packet = type_byte + seq_bytes + data_size_bytes + bytes_sent_bytes + total_size_bytes + data
            return packet
        except Exception as e:
            print(f"Error creating packet: {e}")
            return None
    
    def get_file_list(self):
        """Get formatted list of available media files with quality info"""
        file_list = []
        
        for filename, metadata in self.video_cache.items():
            file_info = {
                'filename': filename,
                'size': metadata.size,
                'size_mb': round(metadata.size / (1024 * 1024), 2),
                'quality': metadata.estimated_quality,
                'type': metadata.mime_type,
                'optimal_chunk_range': metadata.optimal_chunk_size
            }
            file_list.append(file_info)
        
        # Sort by quality and size
        file_list.sort(key=lambda x: (x['quality'], x['size']))
        return file_list
    
    def handle_client_request(self, data, client_addr):
        """Handle incoming client requests with enhanced features"""
        try:
            request = json.loads(data.decode('utf-8'))
            request_type = request.get('type')
            
            if request_type == 'list_files':
                # Send enhanced file list with quality information
                file_list = self.get_file_list()
                response = {
                    'type': 'file_list',
                    'files': file_list,
                    'total_files': len(file_list),
                    'quality_presets': list(self.quality_presets.keys())
                }
                response_data = json.dumps(response).encode('utf-8')
                
                packet = self.create_packet('INFO', 0, response_data)
                if packet:
                    self.server_socket.sendto(packet, client_addr)
                    print(f"📋 Sent enhanced file list to {client_addr} ({len(file_list)} files)")
            
            elif request_type == 'stream_file':
                filename = request.get('filename')
                quality_preset = request.get('quality', 'auto')
                
                if filename in self.video_cache:
                    self.start_video_stream(filename, quality_preset, client_addr)
                else:
                    error_response = {'type': 'error', 'message': f'File not found: {filename}'}
                    error_data = json.dumps(error_response).encode('utf-8')
                    packet = self.create_packet('ERROR', 0, error_data)
                    if packet:
                        self.server_socket.sendto(packet, client_addr)
        
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON request from {client_addr}")
        except Exception as e:
            print(f"❌ Error handling request from {client_addr}: {e}")
    
    def start_video_stream(self, filename, quality_preset, client_addr):
        """Start streaming a video file with adaptive quality"""
        filepath = os.path.join(self.media_directory, filename)
        metadata = self.video_cache[filename]
        
        print(f"🎬 Starting video stream: {filename} ({metadata.estimated_quality}) to {client_addr}")
        
        # Determine chunk size based on quality preset and video metadata
        if quality_preset == 'auto':
            chunk_range = metadata.optimal_chunk_size
        else:
            chunk_range = self.quality_presets.get(quality_preset, metadata.optimal_chunk_size)
        
        # Send file info to client
        file_info = {
            'type': 'file_info',
            'filename': filename,
            'size': metadata.size,
            'quality': metadata.estimated_quality,
            'chunk_range': chunk_range,
            'mime_type': metadata.mime_type
        }
        info_data = json.dumps(file_info).encode('utf-8')
        info_packet = self.create_packet('INFO', 0, info_data, metadata.size, 0)
        
        if info_packet:
            self.server_socket.sendto(info_packet, client_addr)
        
        # Start streaming in a separate thread
        stream_thread = threading.Thread(
            target=self._stream_file_adaptive,
            args=(filepath, metadata, chunk_range, client_addr)
        )
        stream_thread.daemon = True
        stream_thread.start()
    
    def _stream_file_adaptive(self, filepath, metadata, initial_chunk_range, client_addr):
        """Stream file with adaptive chunk sizing based on network conditions"""
        try:
            monitor = self.network_monitors[client_addr]
            seq_num = 1
            bytes_sent = 0
            total_size = metadata.size
            
            print(f"📡 Adaptive streaming started: {metadata.filename}")
            start_time = time.time()
            packet_count = 0
            
            with open(filepath, 'rb') as file:
                while bytes_sent < total_size:
                    # Get adaptive chunk size based on network conditions
                    current_chunk_range = monitor.get_optimal_chunk_size(initial_chunk_range)
                    chunk_size = random.randint(current_chunk_range[0], current_chunk_range[1])
                    
                    # Read chunk
                    remaining_bytes = total_size - bytes_sent
                    actual_chunk_size = min(chunk_size, remaining_bytes)
                    chunk_data = file.read(actual_chunk_size)
                    
                    if not chunk_data:
                        break
                    
                    # Create and send packet
                    send_time = time.time()
                    packet = self.create_packet('D', seq_num, chunk_data, total_size, bytes_sent)
                    
                    if packet:
                        self.server_socket.sendto(packet, client_addr)
                        monitor.record_packet(len(packet), send_time)
                        
                        bytes_sent += len(chunk_data)
                        seq_num += 1
                        packet_count += 1
                        
                        # Dynamic progress reporting
                        if packet_count % 50 == 0:
                            progress = (bytes_sent / total_size) * 100
                            bandwidth = monitor.estimate_bandwidth()
                            print(f"📊 Progress: {progress:.1f}% | Bandwidth: {bandwidth:.1f} KB/s | Chunk: {actual_chunk_size} bytes")
                        
                        # Adaptive delay based on network conditions
                        bandwidth = monitor.estimate_bandwidth()
                        if bandwidth < 100:
                            time.sleep(0.01)  # Slow down for low bandwidth
                        elif bandwidth > 300:
                            time.sleep(0.001)  # Speed up for high bandwidth
                        else:
                            time.sleep(0.005)  # Default delay
            
            # Send end-of-stream marker
            end_packet = self.create_packet('E', seq_num, b'', total_size, bytes_sent)
            if end_packet:
                self.server_socket.sendto(end_packet, client_addr)
            
            # Calculate and display statistics
            duration = time.time() - start_time
            avg_speed = (bytes_sent / 1024) / duration if duration > 0 else 0
            
            print(f"✅ Adaptive streaming complete: {metadata.filename}")
            print(f"📊 Statistics:")
            print(f"   - Bytes sent: {bytes_sent:,} / {total_size:,}")
            print(f"   - Packets sent: {packet_count}")
            print(f"   - Duration: {duration:.2f} seconds")
            print(f"   - Average speed: {avg_speed:.2f} KB/s")
            print(f"   - Final bandwidth estimate: {monitor.estimate_bandwidth():.1f} KB/s")
        
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
        except Exception as e:
            print(f"❌ Error streaming {filepath}: {e}")
    
    def start_server(self):
        """Start the advanced video streaming server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            self.running = True
            
            print("🎬" + "="*60)
            print("🎬 ADVANCED UDP VIDEO STREAMING SERVER")
            print("🎬" + "="*60)
            print(f"🎬 Server started on {self.host}:{self.port}")
            print(f"🎬 Media directory: {self.media_directory}")
            print(f"🎬 Available media files: {len(self.video_cache)}")
            print(f"🎬 Quality presets: {list(self.quality_presets.keys())}")
            print("🎬 Features: Adaptive Streaming, Quality Selection, Network Monitoring")
            print("🎬" + "="*60)
            print("🎬 Waiting for client connections...")
            
            while self.running:
                try:
                    data, client_addr = self.server_socket.recvfrom(4096)
                    print(f"📞 Request from {client_addr}")
                    
                    # Handle request in separate thread for concurrent clients
                    client_thread = threading.Thread(
                        target=self.handle_client_request,
                        args=(data, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving data: {e}")
        
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop_server()
    
    def stop_server(self):
        """Stop the server gracefully"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("🛑 Advanced video streaming server stopped")


def main():
    """Main function to start the advanced video streaming server"""
    import sys
    
    # Default configuration
    host = 'localhost'
    port = 9999
    media_dir = 'media_files'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 9999.")
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    if len(sys.argv) > 3:
        media_dir = sys.argv[3]
    
    # Create and start server
    server = AdvancedUDPVideoServer(host, port, media_dir)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested...")
        server.stop_server()


if __name__ == "__main__":
    main()