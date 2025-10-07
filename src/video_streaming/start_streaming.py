#!/usr/bin/env python3
"""
Video Streaming System Launcher
Quick start script for the professional video streaming system

This script provides:
- Easy server and client startup
- Sample media file creation
- System testing and validation
- Configuration management

Usage:
    python start_streaming.py server    # Start video server
    python start_streaming.py client    # Start video client
    python start_streaming.py setup     # Setup sample files
    python start_streaming.py test      # Run tests
    python start_streaming.py all       # Start both server and client

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import os
import sys
import time
import subprocess
import threading
from typing import List, Optional


def print_banner():
    """Print startup banner"""
    print("🎬" + "=" * 58 + "🎬")
    print("  Professional Video Streaming System Launcher")
    print("  RTSP/RTP Video Streaming with GUI Client")
    print("  Author: Prosenjit Mondol | October 2025")
    print("🎬" + "=" * 58 + "🎬")


def check_dependencies() -> bool:
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    try:
        import tkinter
        print("   ✅ tkinter available")
    except ImportError:
        print("   ❌ tkinter not available (required for GUI client)")
        return False
    
    try:
        import socket
        import threading
        import json
        import struct
        print("   ✅ Standard libraries available")
    except ImportError as e:
        print(f"   ❌ Missing standard library: {e}")
        return False
    
    return True


def get_project_paths():
    """Get project directory paths"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    paths = {
        'root': current_dir,
        'server': os.path.join(current_dir, 'server'),
        'client': os.path.join(current_dir, 'client'),
        'media': os.path.join(current_dir, 'media'),
        'tests': os.path.join(current_dir, 'tests'),
        'protocols': os.path.join(current_dir, 'protocols'),
        'utils': os.path.join(current_dir, 'utils')
    }
    
    return paths


def setup_sample_files():
    """Setup sample media files for testing"""
    print("📁 Setting up sample media files...")
    
    paths = get_project_paths()
    media_script = os.path.join(paths['media'], 'create_samples.py')
    
    if os.path.exists(media_script):
        try:
            os.chdir(paths['media'])
            subprocess.run([sys.executable, 'create_samples.py'], check=True)
            print("   ✅ Sample media files created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error creating sample files: {e}")
            return False
    else:
        print(f"   ❌ Sample creation script not found: {media_script}")
        return False


def start_server():
    """Start the video streaming server"""
    print("🖥️ Starting video streaming server...")
    
    paths = get_project_paths()
    server_script = os.path.join(paths['server'], 'video_server.py')
    
    if os.path.exists(server_script):
        try:
            os.chdir(paths['server'])
            print("   📡 Starting RTSP/RTP server on port 554...")
            subprocess.run([sys.executable, 'video_server.py'])
        except KeyboardInterrupt:
            print("\\n   🛑 Server stopped by user")
        except Exception as e:
            print(f"   ❌ Server error: {e}")
    else:
        print(f"   ❌ Server script not found: {server_script}")


def start_client():
    """Start the video streaming client"""
    print("💻 Starting video streaming client...")
    
    paths = get_project_paths()
    client_script = os.path.join(paths['client'], 'video_client.py')
    
    if os.path.exists(client_script):
        try:
            os.chdir(paths['client'])
            print("   🎬 Starting GUI video client...")
            subprocess.run([sys.executable, 'video_client.py'])
        except KeyboardInterrupt:
            print("\\n   🛑 Client stopped by user")
        except Exception as e:
            print(f"   ❌ Client error: {e}")
    else:
        print(f"   ❌ Client script not found: {client_script}")


def run_tests():
    """Run the test suite"""
    print("🧪 Running video streaming tests...")
    
    paths = get_project_paths()
    test_script = os.path.join(paths['tests'], 'test_video_streaming.py')
    
    if os.path.exists(test_script):
        try:
            os.chdir(paths['tests'])
            subprocess.run([sys.executable, 'test_video_streaming.py'], check=True)
            print("   ✅ All tests completed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Some tests failed: {e}")
        except Exception as e:
            print(f"   ❌ Test error: {e}")
    else:
        print(f"   ❌ Test script not found: {test_script}")


def start_both():
    """Start both server and client"""
    print("🚀 Starting complete video streaming system...")
    
    # Start server in background thread
    def server_thread():
        time.sleep(1)  # Small delay
        start_server()
    
    server_t = threading.Thread(target=server_thread, daemon=True)
    server_t.start()
    
    print("   ⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Start client
    start_client()


def show_help():
    """Show usage help"""
    print("📖 Usage: python start_streaming.py [command]")
    print()
    print("Available commands:")
    print("   server    - Start video streaming server")
    print("   client    - Start video streaming client GUI")
    print("   setup     - Create sample media files for testing")
    print("   test      - Run comprehensive test suite")
    print("   all       - Start both server and client")
    print("   help      - Show this help message")
    print()
    print("Examples:")
    print("   python start_streaming.py server")
    print("   python start_streaming.py client") 
    print("   python start_streaming.py all")
    print()
    print("🎬 Professional Video Streaming System")
    print("   RTSP Control Protocol + RTP Data Streaming")
    print("   GUI Client with Video Controls")
    print("   Quality Profiles: 480p, 720p, 1080p, 4K")


def main():
    """Main launcher function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\\n❌ Dependency check failed. Please install required packages.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "server":
        setup_sample_files()  # Ensure sample files exist
        start_server()
    
    elif command == "client":
        start_client()
    
    elif command == "setup":
        setup_sample_files()
    
    elif command == "test":
        run_tests()
    
    elif command == "all":
        setup_sample_files()  # Ensure sample files exist
        start_both()
    
    elif command in ["help", "-h", "--help"]:
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n🛑 Launcher stopped by user")
    except Exception as e:
        print(f"\\n❌ Launcher error: {e}")
        sys.exit(1)