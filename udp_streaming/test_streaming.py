#!/usr/bin/env python3
"""
UDP Streaming Test Script
Assignment 4: Streaming Client-Server Application

This script provides automated testing for the UDP streaming assignment:
- Tests server startup and configuration
- Tests client-server communication
- Verifies file streaming functionality
- Checks packet handling and buffering
- Validates media player integration

Author: Prosenjit Mondol
Date: October 2025
Course: Computer Networks - Socket Programming
"""

import os
import sys
import time
import socket
import threading
import subprocess
import json
import struct
from datetime import datetime


class StreamingTester:
    def __init__(self):
        """Initialize the test environment"""
        self.server_host = 'localhost'
        self.server_port = 9998  # Use different port for testing
        self.test_results = []
        self.server_process = None
        
        # Test configuration
        self.media_dir = 'media_files'
        self.buffer_dir = 'client_buffer'
        
        print("="*60)
        print("UDP MULTIMEDIA STREAMING - AUTOMATED TEST SUITE")
        print("="*60)
        print(f"Test Configuration:")
        print(f"  Server: {self.server_host}:{self.server_port}")
        print(f"  Media Directory: {self.media_dir}")
        print(f"  Buffer Directory: {self.buffer_dir}")
        print("="*60)
    
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            'timestamp': timestamp,
            'test': test_name,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        print(f"[{timestamp}] {status_symbol} {test_name}: {status}")
        if details:
            print(f"    └─ {details}")
    
    def test_environment_setup(self):
        """Test 1: Environment Setup"""
        self.log_test("Environment Setup", "RUNNING")
        
        try:
            # Check if Python files exist
            if not os.path.exists('streaming_server.py'):
                self.log_test("Environment Setup", "FAIL", "streaming_server.py not found")
                return False
            
            if not os.path.exists('streaming_client.py'):
                self.log_test("Environment Setup", "FAIL", "streaming_client.py not found")
                return False
            
            # Create test directories
            os.makedirs(self.media_dir, exist_ok=True)
            os.makedirs(self.buffer_dir, exist_ok=True)
            
            # Create test media files
            self.create_test_media_files()
            
            self.log_test("Environment Setup", "PASS", "All files and directories ready")
            return True
            
        except Exception as e:
            self.log_test("Environment Setup", "FAIL", f"Error: {str(e)}")
            return False
    
    def create_test_media_files(self):
        """Create sample media files for testing"""
        # Small text file (simulates small media file)
        small_file_path = os.path.join(self.media_dir, "test_small.txt")
        with open(small_file_path, 'w') as f:
            f.write("This is a small test file for UDP streaming.\n" * 100)
        
        # Medium file (simulates audio file)
        medium_file_path = os.path.join(self.media_dir, "test_medium.txt")
        with open(medium_file_path, 'w') as f:
            content = "This is a medium-sized test file simulating an audio file.\n"
            f.write(content * 1000)  # About 50KB
        
        # Large file (simulates video file)
        large_file_path = os.path.join(self.media_dir, "test_large.txt")
        with open(large_file_path, 'wb') as f:
            # Create 1MB test file
            chunk = b"A" * 1024  # 1KB chunk
            for _ in range(1024):  # Write 1024 chunks = 1MB
                f.write(chunk)
        
        print(f"    └─ Created test files:")
        print(f"       - test_small.txt (~3KB)")
        print(f"       - test_medium.txt (~50KB)")
        print(f"       - test_large.txt (1MB)")
    
    def test_server_startup(self):
        """Test 2: Server Startup"""
        self.log_test("Server Startup", "RUNNING")
        
        try:
            # Start server in subprocess
            cmd = [sys.executable, 'streaming_server.py', str(self.server_port)]
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Check if server is responsive
            if self.test_server_connection():
                self.log_test("Server Startup", "PASS", f"Server running on port {self.server_port}")
                return True
            else:
                self.log_test("Server Startup", "FAIL", "Server not responding")
                return False
                
        except Exception as e:
            self.log_test("Server Startup", "FAIL", f"Error starting server: {str(e)}")
            return False
    
    def test_server_connection(self):
        """Test basic UDP connection to server"""
        try:
            # Create test UDP socket
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.settimeout(5)
            
            # Send test request
            test_request = "LIST"
            test_socket.sendto(test_request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Try to receive response
            data, _ = test_socket.recvfrom(4096)
            response = data.decode('utf-8')
            
            test_socket.close()
            return response.startswith("FILES:")
            
        except Exception:
            return False
    
    def test_file_listing(self):
        """Test 3: File Listing"""
        self.log_test("File Listing", "RUNNING")
        
        try:
            # Create UDP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(10)
            
            # Request file list
            request = "LIST"
            client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Receive response
            data, _ = client_socket.recvfrom(4096)
            response = data.decode('utf-8')
            
            client_socket.close()
            
            if response.startswith("FILES:"):
                file_data = response[6:]
                files = json.loads(file_data)
                
                if len(files) >= 3:  # Should have our 3 test files
                    file_names = [f['name'] for f in files]
                    self.log_test("File Listing", "PASS", f"Found {len(files)} files: {file_names}")
                    return True
                else:
                    self.log_test("File Listing", "FAIL", f"Expected 3+ files, got {len(files)}")
                    return False
            else:
                self.log_test("File Listing", "FAIL", f"Invalid response: {response}")
                return False
                
        except Exception as e:
            self.log_test("File Listing", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_small_file_streaming(self):
        """Test 4: Small File Streaming"""
        self.log_test("Small File Streaming", "RUNNING")
        
        try:
            return self.stream_file_test("test_small.txt", "Small File")
        except Exception as e:
            self.log_test("Small File Streaming", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_medium_file_streaming(self):
        """Test 5: Medium File Streaming"""
        self.log_test("Medium File Streaming", "RUNNING")
        
        try:
            return self.stream_file_test("test_medium.txt", "Medium File")
        except Exception as e:
            self.log_test("Medium File Streaming", "FAIL", f"Error: {str(e)}")
            return False
    
    def stream_file_test(self, filename, test_name):
        """Generic file streaming test"""
        try:
            # Create UDP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(30)
            
            # Request file streaming
            request = f"STREAM:{filename}"
            client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Receive file info
            data, _ = client_socket.recvfrom(4096)
            response = data.decode('utf-8')
            
            if not response.startswith("INFO:"):
                self.log_test(f"{test_name} Streaming", "FAIL", f"Expected INFO, got: {response}")
                return False
            
            info_data = response[5:]
            file_info = json.loads(info_data)
            expected_size = file_info['size']
            
            # Receive data packets
            received_bytes = 0
            packets_received = 0
            start_time = time.time()
            
            buffer_file_path = os.path.join(self.buffer_dir, f"test_{filename}")
            
            with open(buffer_file_path, 'wb') as buffer_file:
                while received_bytes < expected_size:
                    try:
                        data, _ = client_socket.recvfrom(65536)
                        
                        # Parse packet
                        if len(data) >= 21:
                            packet_type_byte = struct.unpack('!B', data[:1])[0]
                            packet_type = chr(packet_type_byte)
                            
                            if packet_type == 'D':  # Data packet
                                _, seq_num, data_size, bytes_sent, total_size = struct.unpack('!BII QQ', data[:21])
                                packet_data = data[21:21+data_size]
                                
                                buffer_file.write(packet_data)
                                received_bytes += len(packet_data)
                                packets_received += 1
                                
                            elif packet_type == 'E':  # End packet
                                break
                        
                        # Timeout check
                        if time.time() - start_time > 30:
                            self.log_test(f"{test_name} Streaming", "FAIL", "Timeout waiting for data")
                            return False
                            
                    except socket.timeout:
                        self.log_test(f"{test_name} Streaming", "FAIL", "Socket timeout")
                        return False
            
            client_socket.close()
            
            # Verify received data
            if received_bytes == expected_size:
                elapsed_time = time.time() - start_time
                speed_kbps = (received_bytes / elapsed_time) / 1024 if elapsed_time > 0 else 0
                
                self.log_test(f"{test_name} Streaming", "PASS", 
                             f"{received_bytes} bytes, {packets_received} packets, {speed_kbps:.1f} KB/s")
                return True
            else:
                self.log_test(f"{test_name} Streaming", "FAIL", 
                             f"Size mismatch: expected {expected_size}, got {received_bytes}")
                return False
                
        except Exception as e:
            self.log_test(f"{test_name} Streaming", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_packet_structure(self):
        """Test 6: Packet Structure Validation"""
        self.log_test("Packet Structure", "RUNNING")
        
        try:
            # This test validates that packets have correct structure
            # We'll stream a small file and examine packet format
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(10)
            
            # Request streaming
            request = "STREAM:test_small.txt"
            client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            # Skip INFO packet
            data, _ = client_socket.recvfrom(4096)
            
            # Get first data packet
            data, _ = client_socket.recvfrom(65536)
            
            client_socket.close()
            
            # Validate packet structure
            if len(data) < 21:
                self.log_test("Packet Structure", "FAIL", "Packet too small")
                return False
            
            # Parse header
            packet_type_byte, seq_num, data_size, bytes_sent, total_size = struct.unpack('!BII QQ', data[:21])
            packet_type = chr(packet_type_byte)
            
            # Validate fields
            if packet_type != 'D':
                self.log_test("Packet Structure", "FAIL", f"Invalid packet type: {packet_type}")
                return False
            
            if data_size < 1000 or data_size > 2000:
                self.log_test("Packet Structure", "FAIL", f"Invalid chunk size: {data_size}")
                return False
            
            if len(data) != 21 + data_size:
                self.log_test("Packet Structure", "FAIL", "Packet size mismatch")
                return False
            
            self.log_test("Packet Structure", "PASS", 
                         f"Valid packet: type={packet_type}, seq={seq_num}, size={data_size}")
            return True
            
        except Exception as e:
            self.log_test("Packet Structure", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test 7: Error Handling"""
        self.log_test("Error Handling", "RUNNING")
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(5)
            
            # Test invalid request
            request = "INVALID_REQUEST"
            client_socket.sendto(request.encode('utf-8'), (self.server_host, self.server_port))
            
            data, _ = client_socket.recvfrom(1024)
            response = data.decode('utf-8')
            
            if response.startswith("ERROR:"):
                self.log_test("Error Handling", "PASS", "Server properly handles invalid requests")
                result = True
            else:
                self.log_test("Error Handling", "FAIL", f"Expected error, got: {response}")
                result = False
            
            client_socket.close()
            return result
            
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Error: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test environment"""
        self.log_test("Cleanup", "RUNNING")
        
        try:
            # Stop server process
            if self.server_process:
                self.server_process.terminate()
                time.sleep(1)
                if self.server_process.poll() is None:
                    self.server_process.kill()
                self.server_process = None
            
            # Clean up test files (optional)
            # You might want to keep them for manual testing
            
            self.log_test("Cleanup", "PASS", "Test environment cleaned up")
            
        except Exception as e:
            self.log_test("Cleanup", "FAIL", f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = passed + failed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            print("\\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\\nDetailed Results:")
        for result in self.test_results:
            status_symbol = "✅" if result['status'] == "PASS" else "❌"
            print(f"  {status_symbol} [{result['timestamp']}] {result['test']}")
        
        print("="*60)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Your UDP streaming assignment is working correctly!")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        print("\\nNext Steps:")
        print("1. Review any failed tests and fix issues")
        print("2. Test manually with media files")
        print("3. Verify media player integration")
        print("4. Test with different file sizes and types")
        print("5. Test across different network conditions")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\\nStarting automated test suite...\\n")
        
        # Run tests in order
        tests = [
            self.test_environment_setup,
            self.test_server_startup,
            self.test_file_listing,
            self.test_small_file_streaming,
            self.test_medium_file_streaming,
            self.test_packet_structure,
            self.test_error_handling
        ]
        
        for test in tests:
            if not test():
                print(f"\\n⚠️  Test failed, continuing with remaining tests...\\n")
            time.sleep(1)  # Brief pause between tests
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        self.print_summary()


def main():
    """Main function to run the test suite"""
    try:
        # Change to the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Create and run tester
        tester = StreamingTester()
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\\n\\nTest suite interrupted by user")
        if 'tester' in locals():
            tester.cleanup()
    except Exception as e:
        print(f"\\nTest suite error: {e}")


if __name__ == "__main__":
    main()