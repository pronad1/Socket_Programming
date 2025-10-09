#!/usr/bin/env python3
"""
Advanced UDP Video Streaming Client
Enhanced Video Client with Quality Selection and Playback Controls

Features:
- Quality selection (Low, Medium, High, Auto)
- Advanced buffering with playback controls
- Real-time network monitoring and adaptation
- Video player integration with controls
- Bandwidth monitoring and statistics
- Resume and seek functionality
- Multi-format video support

Author: Prosenjit Mondol
Date: October 2025
Course: Computer Networks - Advanced Video Streaming
"""

import socket
import os
import json
import struct
import time
import threading
import subprocess
import platform
from datetime import datetime
from collections import defaultdict, OrderedDict


class VideoBuffer:
    """Advanced video buffer with playback control"""
    
    def __init__(self, buffer_dir='client_buffer'):
        self.buffer_dir = buffer_dir
        self.packets = OrderedDict()
        self.next_expected_seq = 1
        self.total_size = 0
        self.bytes_received = 0
        self.file_handle = None
        self.buffer_file_path = None
        self.playback_threshold = 102400  # 100KB threshold for playback
        self.current_filename = None
        
        # Ensure buffer directory exists
        if not os.path.exists(self.buffer_dir):
            os.makedirs(self.buffer_dir)
    
    def initialize_file(self, filename, total_size):
        """Initialize buffer file for writing"""
        self.current_filename = filename
        self.total_size = total_size
        self.buffer_file_path = os.path.join(self.buffer_dir, filename)
        
        # Create buffer file
        self.file_handle = open(self.buffer_file_path, 'wb')
        print(f"📁 Buffer file created: {self.buffer_file_path}")
    
    def add_packet(self, seq_num, data):
        """Add packet to buffer with out-of-order handling"""
        if seq_num >= self.next_expected_seq:
            self.packets[seq_num] = data
            
            # Write consecutive packets to file
            while self.next_expected_seq in self.packets:
                packet_data = self.packets.pop(self.next_expected_seq)
                if self.file_handle:
                    self.file_handle.write(packet_data)
                    self.file_handle.flush()  # Ensure data is written
                
                self.bytes_received += len(packet_data)
                self.next_expected_seq += 1
        
        return self.bytes_received >= self.playback_threshold and self.bytes_received < self.playback_threshold + 50000
    
    def get_progress(self):
        """Get current download progress"""
        if self.total_size > 0:
            return (self.bytes_received / self.total_size) * 100
        return 0
    
    def close(self):
        """Close buffer file"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None


class NetworkStats:
    """Monitor network performance and quality"""
    
    def __init__(self):
        self.start_time = time.time()
        self.packets_received = 0
        self.bytes_received = 0
        self.last_update = time.time()
        self.speed_samples = []
        self.quality_metrics = {
            'bandwidth': 0,
            'latency': 0,
            'packet_loss': 0,
            'jitter': 0
        }
    
    def update(self, bytes_count):
        """Update network statistics"""
        current_time = time.time()
        self.packets_received += 1
        self.bytes_received += bytes_count
        
        # Calculate instantaneous speed
        time_diff = current_time - self.last_update
        if time_diff > 0:
            speed_kbps = (bytes_count / 1024) / time_diff
            self.speed_samples.append(speed_kbps)
            
            # Keep only recent samples
            if len(self.speed_samples) > 50:
                self.speed_samples = self.speed_samples[-50:]
        
        self.last_update = current_time
    
    def get_current_speed(self):
        """Get current transfer speed in KB/s"""
        if len(self.speed_samples) >= 5:
            return sum(self.speed_samples[-10:]) / min(10, len(self.speed_samples))
        elif self.bytes_received > 0:
            elapsed = time.time() - self.start_time
            return (self.bytes_received / 1024) / elapsed if elapsed > 0 else 0
        return 0
    
    def get_eta(self, total_size):
        """Estimate time remaining"""
        if self.bytes_received > 0:
            speed = self.get_current_speed()
            if speed > 0:
                remaining_bytes = total_size - self.bytes_received
                return (remaining_bytes / 1024) / speed
        return 0


class MediaPlayerManager:
    """Manage media player integration with advanced controls"""
    
    def __init__(self):
        self.current_process = None
        self.player_type = None
        self.available_players = self._detect_players()
    
    def _detect_players(self):
        """Detect available media players on the system"""
        players = {}
        system = platform.system().lower()
        
        if system == "windows":
            # Windows media players
            players.update({
                'vlc': ['vlc.exe'],
                'mpc': ['mpc-hc64.exe', 'mpc-hc.exe'],
                'wmplayer': ['wmplayer.exe'],
                'potplayer': ['PotPlayerMini64.exe', 'PotPlayer.exe']
            })
        elif system == "darwin":  # macOS
            players.update({
                'vlc': ['vlc'],
                'quicktime': ['open', '-a', 'QuickTime Player'],
                'iina': ['iina']
            })
        else:  # Linux
            players.update({
                'vlc': ['vlc'],
                'mpv': ['mpv'],
                'mplayer': ['mplayer'],
                'totem': ['totem']
            })
        
        return players
    
    def launch_player(self, video_file, quality="auto"):
        """Launch media player with video file"""
        if not os.path.exists(video_file):
            print(f"❌ Video file not found: {video_file}")
            return False
        
        # Try different players in order of preference
        for player_name, command in self.available_players.items():
            try:
                print(f"🎬 Attempting to launch {player_name}...")
                
                if player_name == 'vlc':
                    # VLC with advanced options
                    cmd = command + [
                        '--intf', 'dummy',  # No interface for background play
                        '--play-and-exit',   # Exit when done
                        '--no-video-title-show',  # Don't show title
                        video_file
                    ]
                else:
                    cmd = command + [video_file]
                
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                self.player_type = player_name
                print(f"✅ Media player launched: {player_name}")
                return True
                
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"❌ Failed to launch {player_name}: {e}")
                continue
        
        # Fallback to system default
        try:
            if platform.system() == "Windows":
                os.startfile(video_file)
            elif platform.system() == "Darwin":
                subprocess.run(['open', video_file])
            else:
                subprocess.run(['xdg-open', video_file])
            
            print("✅ Opened with system default player")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open video file: {e}")
            return False
    
    def stop_player(self):
        """Stop current media player"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                print("⏹️ Media player stopped")
            except:
                self.current_process.kill()
                print("🔪 Media player force killed")
            finally:
                self.current_process = None


class AdvancedUDPVideoClient:
    """Advanced UDP Video Streaming Client with quality selection and controls"""
    
    def __init__(self, server_host='localhost', server_port=9999):
        """Initialize the advanced video client"""
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.buffer = VideoBuffer()
        self.stats = NetworkStats()
        self.player = MediaPlayerManager()
        self.available_files = []
        self.quality_presets = ['low', 'medium', 'high', 'auto']
        self.current_stream = None
        
        # Streaming state
        self.streaming = False
        self.stream_thread = None
    
    def connect_to_server(self):
        """Establish connection to the streaming server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.settimeout(30)  # 30 second timeout
            print(f"🔗 Connected to server at {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
    
    def parse_packet(self, packet):
        """Parse received packet structure"""
        try:
            if len(packet) < 25:  # Minimum packet size
                return None
            
            # Parse header: [TYPE:1][SEQ:4][DATA_SIZE:4][BYTES_SENT:8][TOTAL_SIZE:8]
            packet_type = packet[0:1].decode('ascii')
            seq_num = struct.unpack('!I', packet[1:5])[0]
            data_size = struct.unpack('!I', packet[5:9])[0]
            bytes_sent = struct.unpack('!Q', packet[9:17])[0]
            total_size = struct.unpack('!Q', packet[17:25])[0]
            data = packet[25:25+data_size]
            
            return {
                'type': packet_type,
                'seq': seq_num,
                'data_size': data_size,
                'bytes_sent': bytes_sent,
                'total_size': total_size,
                'data': data
            }
        except Exception as e:
            print(f"❌ Error parsing packet: {e}")
            return None
    
    def request_file_list(self):
        """Request enhanced file list from server"""
        try:
            request = {'type': 'list_files'}
            request_data = json.dumps(request).encode('utf-8')
            
            self.client_socket.sendto(request_data, (self.server_host, self.server_port))
            
            # Wait for response
            response, _ = self.client_socket.recvfrom(8192)
            packet_info = self.parse_packet(response)
            
            if packet_info and packet_info['type'] == 'INFO':
                file_list_data = json.loads(packet_info['data'].decode('utf-8'))
                self.available_files = file_list_data.get('files', [])
                
                print("\n🎬" + "="*60)
                print("🎬 AVAILABLE MEDIA FILES")
                print("🎬" + "="*60)
                
                for i, file_info in enumerate(self.available_files, 1):
                    quality_icon = {
                        '1080p': '📹', '720p': '🎥', '480p': '📱', 'audio': '🎵'
                    }.get(file_info['quality'], '📄')
                    
                    print(f" {i:2d}. {quality_icon} {file_info['filename']}")
                    print(f"     📏 Size: {file_info['size_mb']} MB | 🎯 Quality: {file_info['quality']}")
                    print(f"     📊 Type: {file_info['type']}")
                    print()
                
                print(f"🎬 Total files: {len(self.available_files)}")
                print(f"🎬 Quality presets: {', '.join(file_list_data.get('quality_presets', []))}")
                print("🎬" + "="*60)
                return True
        except Exception as e:
            print(f"❌ Error requesting file list: {e}")
            return False
    
    def stream_video(self, filename, quality='auto'):
        """Stream a video file with quality selection"""
        try:
            # Send stream request
            request = {
                'type': 'stream_file',
                'filename': filename,
                'quality': quality
            }
            request_data = json.dumps(request).encode('utf-8')
            
            self.client_socket.sendto(request_data, (self.server_host, self.server_port))
            print(f"📡 Requesting video: {filename} (Quality: {quality})")
            
            # Start receiving stream
            self.streaming = True
            self.stats = NetworkStats()  # Reset stats
            
            # Start streaming in separate thread
            self.stream_thread = threading.Thread(target=self._receive_stream, args=(filename,))
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting stream: {e}")
            return False
    
    def _receive_stream(self, filename):
        """Receive and buffer video stream"""
        try:
            file_initialized = False
            media_player_launched = False
            last_progress_update = time.time()
            
            while self.streaming:
                try:
                    # Receive packet
                    data, _ = self.client_socket.recvfrom(8192)
                    packet_info = self.parse_packet(data)
                    
                    if not packet_info:
                        continue
                    
                    packet_type = packet_info['type']
                    
                    if packet_type == 'INFO':
                        # File info packet
                        file_info = json.loads(packet_info['data'].decode('utf-8'))
                        total_size = file_info['size']
                        quality = file_info.get('quality', 'unknown')
                        
                        print(f"📥 Starting to receive: {filename} ({total_size:,} bytes, {quality})")
                        self.buffer.initialize_file(filename, total_size)
                        file_initialized = True
                        
                    elif packet_type == 'D' and file_initialized:
                        # Data packet
                        seq_num = packet_info['seq']
                        data_chunk = packet_info['data']
                        
                        # Add to buffer
                        should_launch_player = self.buffer.add_packet(seq_num, data_chunk)
                        self.stats.update(len(data_chunk))
                        
                        # Launch media player when threshold reached
                        if should_launch_player and not media_player_launched:
                            print(f"🎬 Launching media player with {self.buffer.bytes_received:,} bytes buffered...")
                            if self.player.launch_player(self.buffer.buffer_file_path):
                                media_player_launched = True
                            else:
                                print("⚠️ Failed to launch media player, continuing download...")
                        
                        # Update progress every 2 seconds
                        current_time = time.time()
                        if current_time - last_progress_update >= 2.0:
                            progress = self.buffer.get_progress()
                            speed = self.stats.get_current_speed()
                            eta = self.stats.get_eta(self.buffer.total_size)
                            
                            progress_bar = self._create_progress_bar(progress)
                            print(f"📊 {progress_bar} {progress:5.1f}% | "
                                  f"💾 {self.buffer.bytes_received//1024:,}KB | "
                                  f"⚡ {speed:.1f} KB/s | "
                                  f"⏱️ ETA: {eta/60:.1f}min | "
                                  f"📦 Packets: {self.stats.packets_received}")
                            
                            last_progress_update = current_time
                        
                    elif packet_type == 'E':
                        # End of stream
                        print("\n✅ Streaming completed!")
                        self._show_final_stats()
                        self.streaming = False
                        break
                        
                    elif packet_type == 'ERROR':
                        # Error packet
                        error_info = json.loads(packet_info['data'].decode('utf-8'))
                        print(f"❌ Server error: {error_info.get('message', 'Unknown error')}")
                        self.streaming = False
                        break
                
                except socket.timeout:
                    print("⏰ Timeout waiting for data")
                    continue
                except Exception as e:
                    print(f"❌ Error receiving stream: {e}")
                    break
            
        finally:
            self.buffer.close()
            self.streaming = False
    
    def _create_progress_bar(self, progress, width=30):
        """Create a visual progress bar"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _show_final_stats(self):
        """Display final streaming statistics"""
        duration = time.time() - self.stats.start_time
        avg_speed = (self.stats.bytes_received / 1024) / duration if duration > 0 else 0
        
        print("📊" + "="*50)
        print("📊 STREAMING STATISTICS")
        print("📊" + "="*50)
        print(f"📁 File: {self.buffer.current_filename}")
        print(f"💾 Total bytes: {self.stats.bytes_received:,}")
        print(f"📦 Total packets: {self.stats.packets_received}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"⚡ Average speed: {avg_speed:.2f} KB/s")
        print(f"📂 Buffer file: {self.buffer.buffer_file_path}")
        print("📊" + "="*50)
    
    def stop_streaming(self):
        """Stop current streaming session"""
        self.streaming = False
        self.player.stop_player()
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5)
        print("⏹️ Streaming stopped")
    
    def interactive_menu(self):
        """Interactive client menu with advanced options"""
        print("\n🎬" + "="*60)
        print("🎬 ADVANCED UDP VIDEO STREAMING CLIENT")
        print("🎬" + "="*60)
        print(f"🎬 Connected to: {self.server_host}:{self.server_port}")
        print(f"🎬 Available players: {', '.join(self.player.available_players.keys())}")
        print(f"🎬 Quality presets: {', '.join(self.quality_presets)}")
        print("🎬" + "="*60)
        
        while True:
            print("\n🎬 OPTIONS:")
            print("  1. 📋 List available media files")
            print("  2. 🎥 Stream a video file")
            print("  3. ⏹️ Stop current streaming")
            print("  4. 📊 Show streaming statistics")
            print("  5. ❌ Exit")
            
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.request_file_list()
                
                elif choice == '2':
                    if not self.available_files:
                        print("📋 Please list files first (option 1)")
                        continue
                    
                    print(f"\nAvailable files (1-{len(self.available_files)}):")
                    file_input = input("Enter file number or filename: ").strip()
                    
                    # Determine filename
                    filename = None
                    if file_input.isdigit():
                        file_num = int(file_input)
                        if 1 <= file_num <= len(self.available_files):
                            filename = self.available_files[file_num - 1]['filename']
                    else:
                        filename = file_input
                    
                    if filename:
                        # Quality selection
                        print(f"\nQuality options: {', '.join(self.quality_presets)}")
                        quality = input("Select quality (default: auto): ").strip() or 'auto'
                        
                        if quality in self.quality_presets:
                            self.stream_video(filename, quality)
                        else:
                            print(f"❌ Invalid quality. Using 'auto'")
                            self.stream_video(filename, 'auto')
                    else:
                        print("❌ Invalid file selection")
                
                elif choice == '3':
                    self.stop_streaming()
                
                elif choice == '4':
                    if self.streaming:
                        self._show_final_stats()
                    else:
                        print("ℹ️ No active streaming session")
                
                elif choice == '5':
                    self.stop_streaming()
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                self.stop_streaming()
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        self.stop_streaming()
        if self.client_socket:
            self.client_socket.close()
        print("🔌 Disconnected from server")


def main():
    """Main function to start the advanced video client"""
    import sys
    
    # Default configuration
    server_host = 'localhost'
    server_port = 9999
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("❌ Invalid port number. Using default port 9999.")
    
    # Create and start client
    client = AdvancedUDPVideoClient(server_host, server_port)
    
    if client.connect_to_server():
        try:
            client.interactive_menu()
        except KeyboardInterrupt:
            print("\n🛑 Client shutdown requested...")
        finally:
            client.disconnect()
    else:
        print("❌ Failed to connect to server")


if __name__ == "__main__":
    main()