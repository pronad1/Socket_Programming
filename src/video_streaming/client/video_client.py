#!/usr/bin/env python3
"""
Professional Video Streaming Client
RTSP/RTP Video Client with GUI Controls

This client provides:
- RTSP protocol support for video control
- RTP video stream reception
- GUI interface with video controls
- Multiple video format support
- Quality selection
- Playlist management
- Real-time streaming statistics

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import socket
import threading
import time
import os
import json
import struct
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import subprocess
import platform


class VideoStreamingClient:
    """Professional Video Streaming Client with GUI"""
    
    def __init__(self, server_host='localhost', rtsp_port=554, rtp_port=5004):
        """
        Initialize the video streaming client
        
        Args:
            server_host (str): Video server host
            rtsp_port (int): RTSP control port
            rtp_port (int): RTP data port
        """
        self.server_host = server_host
        self.rtsp_port = rtsp_port
        self.rtp_port = rtp_port
        
        # Network connections
        self.rtsp_socket = None
        self.rtp_socket = None
        self.connected = False
        
        # Streaming state
        self.session_id = None
        self.current_video = None
        self.playing = False
        self.stream_stats = {
            'packets_received': 0,
            'bytes_received': 0,
            'frames_received': 0,
            'start_time': None,
            'last_packet_time': None
        }
        
        # Video library
        self.video_library = []
        self.current_playlist = []
        
        # GUI components
        self.root = None
        self.setup_gui()
        
        # Buffer for video data
        self.video_buffer = []
        self.buffer_file = None
        
        print("🎬 Video Streaming Client Initialized")
        print(f"   🌐 Server: {self.server_host}:{self.rtsp_port}")
        print(f"   📡 RTP Port: {self.rtp_port}")
    
    def setup_gui(self):
        """Setup the GUI interface"""
        self.root = tk.Tk()
        self.root.title("Professional Video Streaming Client")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2b2b2b', foreground='white')
        style.configure('Info.TLabel', font=('Arial', 10), background='#2b2b2b', foreground='#cccccc')
        
        self.setup_connection_frame()
        self.setup_control_frame()
        self.setup_video_library_frame()
        self.setup_playlist_frame()
        self.setup_stats_frame()
        self.setup_status_frame()
    
    def setup_connection_frame(self):
        """Setup connection controls"""
        conn_frame = ttk.LabelFrame(self.root, text="Server Connection", padding=10)
        conn_frame.pack(fill='x', padx=10, pady=5)
        
        # Server settings
        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0, sticky='w', padx=5)
        self.server_entry = ttk.Entry(conn_frame, width=20)
        self.server_entry.insert(0, self.server_host)
        self.server_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(conn_frame, text="RTSP Port:").grid(row=0, column=2, sticky='w', padx=5)
        self.rtsp_port_entry = ttk.Entry(conn_frame, width=10)
        self.rtsp_port_entry.insert(0, str(self.rtsp_port))
        self.rtsp_port_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(conn_frame, text="RTP Port:").grid(row=0, column=4, sticky='w', padx=5)
        self.rtp_port_entry = ttk.Entry(conn_frame, width=10)
        self.rtp_port_entry.insert(0, str(self.rtp_port))
        self.rtp_port_entry.grid(row=0, column=5, padx=5)
        
        # Connection buttons
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_btn.grid(row=0, column=6, padx=10)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_from_server, state='disabled')
        self.disconnect_btn.grid(row=0, column=7, padx=5)
        
        # Connection status
        self.connection_status = ttk.Label(conn_frame, text="Disconnected", foreground='red')
        self.connection_status.grid(row=1, column=0, columnspan=8, pady=5)
    
    def setup_control_frame(self):
        """Setup video control buttons"""
        control_frame = ttk.LabelFrame(self.root, text="Video Controls", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Playback controls
        self.play_btn = ttk.Button(control_frame, text="▶ Play", command=self.play_video, state='disabled')
        self.play_btn.pack(side='left', padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="⏸ Pause", command=self.pause_video, state='disabled')
        self.pause_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop", command=self.stop_video, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Volume control
        ttk.Label(control_frame, text="Volume:").pack(side='left', padx=20)
        self.volume_scale = ttk.Scale(control_frame, from_=0, to=100, orient='horizontal', length=100)
        self.volume_scale.set(50)
        self.volume_scale.pack(side='left', padx=5)
        
        # Quality selection
        ttk.Label(control_frame, text="Quality:").pack(side='left', padx=20)
        self.quality_var = tk.StringVar(value="720p")
        quality_combo = ttk.Combobox(control_frame, textvariable=self.quality_var, 
                                   values=["480p", "720p", "1080p", "4K"], state="readonly", width=10)
        quality_combo.pack(side='left', padx=5)
        
        # Launch media player
        self.launch_player_btn = ttk.Button(control_frame, text="🎬 Launch Player", 
                                          command=self.launch_external_player, state='disabled')
        self.launch_player_btn.pack(side='right', padx=5)
    
    def setup_video_library_frame(self):
        """Setup video library display"""
        library_frame = ttk.LabelFrame(self.root, text="Video Library", padding=10)
        library_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for video list
        columns = ('Name', 'Size', 'Duration', 'Quality', 'Description')
        self.library_tree = ttk.Treeview(library_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.library_tree.heading('Name', text='Video Name')
        self.library_tree.heading('Size', text='Size (MB)')
        self.library_tree.heading('Duration', text='Duration (s)')
        self.library_tree.heading('Quality', text='Quality')
        self.library_tree.heading('Description', text='Description')
        
        self.library_tree.column('Name', width=200)
        self.library_tree.column('Size', width=80)
        self.library_tree.column('Duration', width=80)
        self.library_tree.column('Quality', width=80)
        self.library_tree.column('Description', width=300)
        
        # Scrollbar for library
        library_scroll = ttk.Scrollbar(library_frame, orient='vertical', command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=library_scroll.set)
        
        # Pack library components
        self.library_tree.pack(side='left', fill='both', expand=True)
        library_scroll.pack(side='right', fill='y')
        
        # Library buttons
        library_btn_frame = ttk.Frame(library_frame)
        library_btn_frame.pack(fill='x', pady=5)
        
        self.refresh_btn = ttk.Button(library_btn_frame, text="🔄 Refresh Library", 
                                     command=self.refresh_video_library, state='disabled')
        self.refresh_btn.pack(side='left', padx=5)
        
        self.select_video_btn = ttk.Button(library_btn_frame, text="📺 Select Video", 
                                         command=self.select_video, state='disabled')
        self.select_video_btn.pack(side='left', padx=5)
        
        # Bind double-click to select video
        self.library_tree.bind('<Double-1>', lambda e: self.select_video())
    
    def setup_playlist_frame(self):
        """Setup playlist management"""
        playlist_frame = ttk.LabelFrame(self.root, text="Current Selection", padding=10)
        playlist_frame.pack(fill='x', padx=10, pady=5)
        
        self.current_video_label = ttk.Label(playlist_frame, text="No video selected", 
                                           style='Info.TLabel')
        self.current_video_label.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(playlist_frame, variable=self.progress_var, 
                                          length=300, mode='determinate')
        self.progress_bar.pack(side='right', padx=20)
        
        self.progress_label = ttk.Label(playlist_frame, text="00:00 / 00:00", style='Info.TLabel')
        self.progress_label.pack(side='right', padx=5)
    
    def setup_stats_frame(self):
        """Setup streaming statistics display"""
        stats_frame = ttk.LabelFrame(self.root, text="Streaming Statistics", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Stats labels
        self.stats_packets = ttk.Label(stats_frame, text="Packets: 0", style='Info.TLabel')
        self.stats_packets.pack(side='left', padx=10)
        
        self.stats_bytes = ttk.Label(stats_frame, text="Data: 0 MB", style='Info.TLabel')
        self.stats_bytes.pack(side='left', padx=10)
        
        self.stats_fps = ttk.Label(stats_frame, text="FPS: 0", style='Info.TLabel')
        self.stats_fps.pack(side='left', padx=10)
        
        self.stats_bitrate = ttk.Label(stats_frame, text="Bitrate: 0 kbps", style='Info.TLabel')
        self.stats_bitrate.pack(side='left', padx=10)
        
        # Buffer status
        self.buffer_status = ttk.Label(stats_frame, text="Buffer: 0%", style='Info.TLabel')
        self.buffer_status.pack(side='right', padx=10)
    
    def setup_status_frame(self):
        """Setup status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief='sunken', 
                                     style='Info.TLabel')
        self.status_label.pack(fill='x', padx=5, pady=2)
    
    def connect_to_server(self):
        """Connect to video streaming server"""
        try:
            # Get connection parameters
            self.server_host = self.server_entry.get()
            self.rtsp_port = int(self.rtsp_port_entry.get())
            self.rtp_port = int(self.rtp_port_entry.get())
            
            # Create RTSP connection
            self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rtsp_socket.settimeout(10)
            self.rtsp_socket.connect((self.server_host, self.rtsp_port))
            
            # Create RTP socket for receiving video data
            self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rtp_socket.bind(('', self.rtp_port))
            
            self.connected = True
            self.update_connection_status("Connected", 'green')
            self.update_status("Connected to server")
            
            # Enable controls
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            self.refresh_btn.config(state='normal')
            
            # Start RTP receiver thread
            rtp_thread = threading.Thread(target=self.rtp_receiver, daemon=True)
            rtp_thread.start()
            
            # Refresh video library
            self.refresh_video_library()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.update_status(f"Connection failed: {e}")
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        try:
            if self.playing:
                self.stop_video()
            
            self.connected = False
            
            if self.rtsp_socket:
                self.rtsp_socket.close()
                self.rtsp_socket = None
            
            if self.rtp_socket:
                self.rtp_socket.close()
                self.rtp_socket = None
            
            self.update_connection_status("Disconnected", 'red')
            self.update_status("Disconnected from server")
            
            # Disable controls
            self.connect_btn.config(state='normal')
            self.disconnect_btn.config(state='disabled')
            self.refresh_btn.config(state='disabled')
            self.play_btn.config(state='disabled')
            self.pause_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.select_video_btn.config(state='disabled')
            self.launch_player_btn.config(state='disabled')
            
            # Clear library
            for item in self.library_tree.get_children():
                self.library_tree.delete(item)
            
        except Exception as e:
            self.update_status(f"Disconnect error: {e}")
    
    def refresh_video_library(self):
        """Refresh video library from server"""
        if not self.connected:
            return
        
        try:
            # Send GET_VIDEOS request
            request = "GET_VIDEOS rtsp://server/ RTSP/1.0\\nCSeq: 1\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            
            # Receive response
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            # Parse response
            lines = response.split('\\n')
            content_start = False
            content_lines = []
            
            for line in lines:
                if content_start:
                    content_lines.append(line)
                elif line.strip() == '':
                    content_start = True
            
            if content_lines:
                content = '\\n'.join(content_lines)
                self.video_library = json.loads(content)
                self.update_video_library_display()
                self.update_status(f"Library updated: {len(self.video_library)} videos")
            
        except Exception as e:
            self.update_status(f"Library refresh error: {e}")
    
    def update_video_library_display(self):
        """Update the video library display"""
        # Clear existing items
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        # Add videos to tree
        for video in self.video_library:
            size_mb = video['size'] / (1024 * 1024)
            self.library_tree.insert('', 'end', values=(
                video['name'],
                f"{size_mb:.1f}",
                video['duration'],
                video['resolution'],
                video['description']
            ))
        
        # Enable selection button
        self.select_video_btn.config(state='normal')
    
    def select_video(self):
        """Select video for streaming"""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a video first")
            return
        
        item = self.library_tree.item(selection[0])
        video_name = item['values'][0]
        
        # Find video info
        video_info = next((v for v in self.video_library if v['name'] == video_name), None)
        if not video_info:
            return
        
        self.current_video = video_info
        self.current_video_label.config(text=f"Selected: {video_name}")
        
        # Setup video session
        self.setup_video_session(video_name)
        
        # Enable playback controls
        self.play_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        self.launch_player_btn.config(state='normal')
        
        self.update_status(f"Video selected: {video_name}")
    
    def setup_video_session(self, video_name: str):
        """Setup RTSP session for video"""
        try:
            # Send DESCRIBE request
            request = f"DESCRIBE rtsp://server/{video_name} RTSP/1.0\\nCSeq: 2\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            # Send SETUP request
            request = f"SETUP rtsp://server/{video_name} RTSP/1.0\\nCSeq: 3\\nTransport: RTP/UDP;unicast;client_port={self.rtp_port}-{self.rtp_port+1}\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            # Extract session ID
            for line in response.split('\\n'):
                if line.startswith('Session:'):
                    self.session_id = line.split(':')[1].strip()
                    break
            
        except Exception as e:
            self.update_status(f"Session setup error: {e}")
    
    def play_video(self):
        """Start video playback"""
        if not self.current_video or not self.session_id:
            return
        
        try:
            # Send PLAY request
            request = f"PLAY rtsp://server/{self.current_video['name']} RTSP/1.0\\nCSeq: 4\\nSession: {self.session_id}\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            self.playing = True
            self.stream_stats['start_time'] = time.time()
            self.stream_stats['packets_received'] = 0
            self.stream_stats['bytes_received'] = 0
            
            # Update controls
            self.play_btn.config(state='disabled')
            self.pause_btn.config(state='normal')
            
            # Start video file buffering
            self.start_video_buffering()
            
            self.update_status(f"Playing: {self.current_video['name']}")
            
        except Exception as e:
            self.update_status(f"Play error: {e}")
    
    def pause_video(self):
        """Pause video playback"""
        if not self.session_id:
            return
        
        try:
            # Send PAUSE request
            request = f"PAUSE rtsp://server/{self.current_video['name']} RTSP/1.0\\nCSeq: 5\\nSession: {self.session_id}\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            self.playing = False
            
            # Update controls
            self.play_btn.config(state='normal')
            self.pause_btn.config(state='disabled')
            
            self.update_status("Video paused")
            
        except Exception as e:
            self.update_status(f"Pause error: {e}")
    
    def stop_video(self):
        """Stop video playback"""
        if not self.session_id:
            return
        
        try:
            # Send TEARDOWN request
            request = f"TEARDOWN rtsp://server/{self.current_video['name']} RTSP/1.0\\nCSeq: 6\\nSession: {self.session_id}\\n\\n"
            self.rtsp_socket.send(request.encode('utf-8'))
            response = self.rtsp_socket.recv(4096).decode('utf-8')
            
            self.playing = False
            self.session_id = None
            
            # Update controls
            self.play_btn.config(state='disabled')
            self.pause_btn.config(state='disabled')
            
            # Close buffer file
            if self.buffer_file:
                self.buffer_file.close()
                self.buffer_file = None
            
            self.update_status("Video stopped")
            
        except Exception as e:
            self.update_status(f"Stop error: {e}")
    
    def start_video_buffering(self):
        """Start buffering video data to file"""
        if not self.current_video:
            return
        
        # Create buffer file
        buffer_dir = "client_buffer"
        if not os.path.exists(buffer_dir):
            os.makedirs(buffer_dir)
        
        buffer_filename = f"buffer_{self.current_video['name']}"
        buffer_path = os.path.join(buffer_dir, buffer_filename)
        
        try:
            self.buffer_file = open(buffer_path, 'wb')
            self.update_status(f"Buffering to: {buffer_path}")
        except Exception as e:
            self.update_status(f"Buffer file error: {e}")
    
    def rtp_receiver(self):
        """Receive RTP video packets"""
        while self.connected:
            try:
                if not self.rtp_socket:
                    break
                
                # Receive RTP packet
                data, addr = self.rtp_socket.recvfrom(2048)
                
                if self.playing and len(data) > 12:  # RTP header is 12 bytes
                    # Parse RTP header
                    header = struct.unpack('!BBHII', data[:12])
                    payload = data[12:]
                    
                    # Update statistics
                    self.stream_stats['packets_received'] += 1
                    self.stream_stats['bytes_received'] += len(payload)
                    self.stream_stats['last_packet_time'] = time.time()
                    
                    # Buffer video data
                    if self.buffer_file:
                        self.buffer_file.write(payload)
                        self.buffer_file.flush()
                    
                    # Update GUI statistics (every 10 packets)
                    if self.stream_stats['packets_received'] % 10 == 0:
                        self.root.after(0, self.update_streaming_stats)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.connected:
                    self.update_status(f"RTP receive error: {e}")
                break
    
    def update_streaming_stats(self):
        """Update streaming statistics display"""
        stats = self.stream_stats
        
        # Calculate derived statistics
        if stats['start_time']:
            elapsed = time.time() - stats['start_time']
            fps = stats['packets_received'] / elapsed if elapsed > 0 else 0
            bitrate = (stats['bytes_received'] * 8) / (elapsed * 1000) if elapsed > 0 else 0  # kbps
            data_mb = stats['bytes_received'] / (1024 * 1024)
            
            # Update GUI
            self.stats_packets.config(text=f"Packets: {stats['packets_received']}")
            self.stats_bytes.config(text=f"Data: {data_mb:.2f} MB")
            self.stats_fps.config(text=f"FPS: {fps:.1f}")
            self.stats_bitrate.config(text=f"Bitrate: {bitrate:.1f} kbps")
            
            # Calculate buffer percentage (simplified)
            if self.current_video:
                buffer_percent = min(100, (stats['bytes_received'] / (self.current_video['size'] / 10)) * 100)
                self.buffer_status.config(text=f"Buffer: {buffer_percent:.1f}%")
    
    def launch_external_player(self):
        """Launch external media player"""
        if not self.current_video or not self.buffer_file:
            messagebox.showwarning("No Video", "No video is currently buffering")
            return
        
        buffer_path = self.buffer_file.name
        
        try:
            system = platform.system().lower()
            
            if system == "windows":
                os.startfile(buffer_path)
            elif system == "darwin":  # macOS
                subprocess.run(['open', buffer_path])
            elif system == "linux":
                # Try common players
                players = ['vlc', 'mpv', 'mplayer', 'totem']
                for player in players:
                    try:
                        subprocess.run([player, buffer_path])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    subprocess.run(['xdg-open', buffer_path])
            
            self.update_status(f"Launched player for: {self.current_video['name']}")
            
        except Exception as e:
            messagebox.showerror("Player Error", f"Failed to launch player: {e}")
    
    def update_connection_status(self, status: str, color: str):
        """Update connection status display"""
        self.connection_status.config(text=status, foreground=color)
    
    def update_status(self, message: str):
        """Update status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"[{timestamp}] {message}")
    
    def run(self):
        """Run the video streaming client"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()


def main():
    """Main function to start the video streaming client"""
    import sys
    
    # Default configuration
    server_host = 'localhost'
    rtsp_port = 554
    rtp_port = 5004
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            rtsp_port = int(sys.argv[2])
        except ValueError:
            print("❌ Invalid RTSP port. Using default 554")
    
    if len(sys.argv) > 3:
        try:
            rtp_port = int(sys.argv[3])
        except ValueError:
            print("❌ Invalid RTP port. Using default 5004")
    
    # Create and run client
    try:
        print("🎬 Starting Professional Video Streaming Client...")
        client = VideoStreamingClient(server_host, rtsp_port, rtp_port)
        client.run()
    except Exception as e:
        print(f"❌ Client error: {e}")


if __name__ == "__main__":
    main()