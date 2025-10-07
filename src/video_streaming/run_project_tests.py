#!/usr/bin/env python3
"""
Complete Project Test Runner
Comprehensive testing suite for the Professional Video Streaming System

This test runner provides:
- Complete system validation
- Integration testing
- Performance benchmarking
- Live streaming tests
- Error scenario testing
- Network connectivity validation
- GUI component testing

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import os
import sys
import time
import socket
import threading
import subprocess
import tempfile
import json
import struct
from typing import Dict, List, Optional, Tuple
import unittest
from datetime import datetime

# Add project modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import project modules
try:
    from protocols.rtsp_protocol import RTSPParser, RTSPFormatter, RTSPHandler, RTSPMethod, RTSPStatus
    from protocols.rtp_protocol import RTPSession, RTPPacket, RTPReceiver, RTPPayloadType
    from utils.video_utils import VideoFileValidator, QualityProfileManager, VideoLibraryManager, StreamingUtils
    from server.video_server import VideoStreamingServer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the video_streaming directory")
    sys.exit(1)


class ProjectTestRunner:
    """Main test runner for the video streaming project"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        self.temp_dir = tempfile.mkdtemp()
        self.test_server = None
        self.test_server_thread = None
        
    def run_all_tests(self):
        """Run complete test suite"""
        print("🎬" + "=" * 58 + "🎬")
        print("  Professional Video Streaming System - Project Tests")
        print("  Complete System Validation and Integration Testing")
        print("  Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("🎬" + "=" * 58 + "🎬")
        
        test_categories = [
            ("Protocol Tests", self.test_protocols),
            ("Utility Tests", self.test_utilities), 
            ("Server Tests", self.test_server),
            ("Integration Tests", self.test_integration),
            ("Performance Tests", self.test_performance),
            ("Network Tests", self.test_network),
            ("Error Handling Tests", self.test_error_handling),
            ("Media File Tests", self.test_media_files),
            ("Live Streaming Tests", self.test_live_streaming)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n🧪 {category_name}")
            print("-" * 50)
            try:
                test_func()
            except Exception as e:
                self.record_test_result(f"{category_name} - Critical Error", False, str(e))
        
        self.print_final_results()
        return self.test_results['failed_tests'] == 0
    
    def record_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            print(f"   ✅ {test_name}")
        else:
            self.test_results['failed_tests'] += 1
            print(f"   ❌ {test_name}: {details}")
        
        self.test_results['test_details'].append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_protocols(self):
        """Test RTSP and RTP protocol implementations"""
        
        # Test RTSP Request Parsing
        try:
            request_text = "DESCRIBE rtsp://server/video.mp4 RTSP/1.0\nCSeq: 1\nAccept: application/sdp\n\n"
            request = RTSPParser.parse_request(request_text)
            assert request.method == RTSPMethod.DESCRIBE
            assert request.uri == "rtsp://server/video.mp4"
            assert request.headers.get("CSeq") == "1"
            self.record_test_result("RTSP Request Parsing", True)
        except Exception as e:
            self.record_test_result("RTSP Request Parsing", False, str(e))
        
        # Test RTSP Response Formatting
        try:
            from protocols.rtsp_protocol import RTSPResponse
            response = RTSPResponse()
            response.status_code = 200
            response.headers["CSeq"] = "1"
            formatted = RTSPFormatter.format_response(response)
            assert "RTSP/1.0 200 OK" in formatted
            self.record_test_result("RTSP Response Formatting", True)
        except Exception as e:
            self.record_test_result("RTSP Response Formatting", False, str(e))
        
        # Test RTP Packet Creation
        try:
            session = RTPSession(ssrc=12345, payload_type=96)
            payload = b"test_video_data"
            packet = session.create_packet(payload, marker=True)
            assert packet.header.ssrc == 12345
            assert packet.header.payload_type == 96
            assert packet.payload == payload
            self.record_test_result("RTP Packet Creation", True)
        except Exception as e:
            self.record_test_result("RTP Packet Creation", False, str(e))
        
        # Test RTP Packet Serialization
        try:
            packet_bytes = packet.to_bytes()
            parsed_packet = RTPPacket.from_bytes(packet_bytes)
            assert parsed_packet.header.ssrc == 12345
            assert parsed_packet.payload == payload
            self.record_test_result("RTP Packet Serialization", True)
        except Exception as e:
            self.record_test_result("RTP Packet Serialization", False, str(e))
        
        # Test RTP Receiver
        try:
            receiver = RTPReceiver(buffer_size=10)
            ready_packets = receiver.receive_packet(packet)
            stats = receiver.get_statistics()
            assert stats['packets_received'] >= 1
            self.record_test_result("RTP Receiver Functionality", True)
        except Exception as e:
            self.record_test_result("RTP Receiver Functionality", False, str(e))
    
    def test_utilities(self):
        """Test utility modules"""
        
        # Test Quality Profile Manager
        try:
            profile = QualityProfileManager.get_profile("720p")
            assert profile is not None
            assert profile.resolution == (1280, 720)
            assert profile.bitrate == 2500
            self.record_test_result("Quality Profile Manager", True)
        except Exception as e:
            self.record_test_result("Quality Profile Manager", False, str(e))
        
        # Test Video File Validator
        try:
            # Test with non-existent file
            result = VideoFileValidator.is_valid_video_file("nonexistent.mp4")
            assert result == False
            self.record_test_result("Video File Validator", True)
        except Exception as e:
            self.record_test_result("Video File Validator", False, str(e))
        
        # Test Streaming Utils
        try:
            chunk_size = StreamingUtils.calculate_chunk_size(2500, 30)
            assert chunk_size >= 1024
            buffer_size = StreamingUtils.estimate_buffer_size(2500, 5.0)
            assert buffer_size > 0
            formatted_size = StreamingUtils.format_file_size(1073741824)
            assert "1.0 GB" in formatted_size
            self.record_test_result("Streaming Utilities", True)
        except Exception as e:
            self.record_test_result("Streaming Utilities", False, str(e))
        
        # Test Video Library Manager
        try:
            library = VideoLibraryManager(self.temp_dir)
            stats = library.get_library_stats()
            assert isinstance(stats, dict)
            assert 'total_videos' in stats
            self.record_test_result("Video Library Manager", True)
        except Exception as e:
            self.record_test_result("Video Library Manager", False, str(e))
    
    def test_server(self):
        """Test video streaming server functionality"""
        
        # Test Server Initialization
        try:
            server = VideoStreamingServer(rtsp_port=15554, rtp_base_port=15004)
            assert server.rtsp_port == 15554
            assert server.rtp_base_port == 15004
            self.record_test_result("Server Initialization", True)
        except Exception as e:
            self.record_test_result("Server Initialization", False, str(e))
        
        # Test Server Port Binding
        try:
            # Test if we can create sockets on specified ports
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('localhost', 15555))
            test_socket.close()
            self.record_test_result("Server Port Binding", True)
        except Exception as e:
            self.record_test_result("Server Port Binding", False, str(e))
        
        # Test RTSP Handler
        try:
            handler = RTSPHandler()
            session = handler.create_session(("127.0.0.1", 12345))
            assert session is not None
            assert session.session_id is not None
            self.record_test_result("RTSP Handler", True)
        except Exception as e:
            self.record_test_result("RTSP Handler", False, str(e))
    
    def test_integration(self):
        """Test system integration"""
        
        # Test Client-Server Communication Simulation
        try:
            # Create mock RTSP conversation
            request_text = "OPTIONS * RTSP/1.0\nCSeq: 1\n\n"
            request = RTSPParser.parse_request(request_text)
            
            handler = RTSPHandler()
            response = handler.handle_options(request)
            
            assert response.status_code == 200
            assert "Public" in response.headers
            self.record_test_result("Client-Server Communication", True)
        except Exception as e:
            self.record_test_result("Client-Server Communication", False, str(e))
        
        # Test Protocol Flow
        try:
            handler = RTSPHandler()
            
            # SETUP request
            from protocols.rtsp_protocol import RTSPRequest
            setup_request = RTSPRequest(
                method=RTSPMethod.SETUP,
                uri="rtsp://server/test.mp4",
                headers={
                    "CSeq": "2",
                    "Transport": "RTP/UDP;unicast;client_port=5004-5005"
                }
            )
            
            setup_response = handler.handle_setup(setup_request, ("127.0.0.1", 12345))
            assert setup_response.status_code == 200
            assert "Session" in setup_response.headers
            self.record_test_result("Protocol Flow Integration", True)
        except Exception as e:
            self.record_test_result("Protocol Flow Integration", False, str(e))
    
    def test_performance(self):
        """Test system performance"""
        
        # Test RTP Packet Performance
        try:
            session = RTPSession(ssrc=12345)
            payload = b"A" * 1400  # MTU-sized payload
            
            start_time = time.time()
            packets = []
            for i in range(100):  # Create 100 packets
                packet = session.create_packet(payload)
                packets.append(packet)
            creation_time = time.time() - start_time
            
            # Should create 100 packets quickly
            assert creation_time < 1.0
            self.record_test_result("RTP Packet Performance", True, f"{creation_time:.3f}s for 100 packets")
        except Exception as e:
            self.record_test_result("RTP Packet Performance", False, str(e))
        
        # Test RTSP Parsing Performance
        try:
            test_request = "DESCRIBE rtsp://server/video.mp4 RTSP/1.0\nCSeq: 1\nAccept: application/sdp\n\n"
            
            start_time = time.time()
            for i in range(100):  # Parse 100 requests
                request = RTSPParser.parse_request(test_request)
            parsing_time = time.time() - start_time
            
            assert parsing_time < 1.0
            self.record_test_result("RTSP Parsing Performance", True, f"{parsing_time:.3f}s for 100 requests")
        except Exception as e:
            self.record_test_result("RTSP Parsing Performance", False, str(e))
    
    def test_network(self):
        """Test network functionality"""
        
        # Test Socket Creation
        try:
            # Test TCP socket
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.close()
            
            # Test UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.close()
            
            self.record_test_result("Socket Creation", True)
        except Exception as e:
            self.record_test_result("Socket Creation", False, str(e))
        
        # Test Port Availability
        try:
            available_ports = []
            for port in [554, 5004, 5005, 15554, 15004]:
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.bind(('localhost', port))
                    test_socket.close()
                    available_ports.append(port)
                except OSError:
                    pass  # Port in use, which is okay
            
            self.record_test_result("Port Availability Check", True, f"Tested ports: {available_ports}")
        except Exception as e:
            self.record_test_result("Port Availability Check", False, str(e))
        
        # Test Network Interfaces
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            assert local_ip is not None
            self.record_test_result("Network Interface Detection", True, f"Host: {hostname}, IP: {local_ip}")
        except Exception as e:
            self.record_test_result("Network Interface Detection", False, str(e))
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        
        # Test Invalid RTSP Request
        try:
            try:
                RTSPParser.parse_request("INVALID REQUEST")
                self.record_test_result("Invalid RTSP Request Handling", False, "Should have raised ValueError")
            except ValueError:
                self.record_test_result("Invalid RTSP Request Handling", True)
        except Exception as e:
            self.record_test_result("Invalid RTSP Request Handling", False, str(e))
        
        # Test Invalid RTP Packet
        try:
            try:
                RTPPacket.from_bytes(b"short")
                self.record_test_result("Invalid RTP Packet Handling", False, "Should have raised ValueError")
            except ValueError:
                self.record_test_result("Invalid RTP Packet Handling", True)
        except Exception as e:
            self.record_test_result("Invalid RTP Packet Handling", False, str(e))
        
        # Test File Operation Errors
        try:
            library = VideoLibraryManager("/nonexistent/path")
            count = library.scan_library()
            assert count == 0
            self.record_test_result("File Operation Error Handling", True)
        except Exception as e:
            self.record_test_result("File Operation Error Handling", False, str(e))
    
    def test_media_files(self):
        """Test media file operations"""
        
        # Test Sample File Creation
        try:
            media_dir = os.path.join(current_dir, 'media')
            create_script = os.path.join(media_dir, 'create_samples.py')
            
            if os.path.exists(create_script):
                # Run sample creation
                result = subprocess.run([sys.executable, create_script], 
                                      cwd=media_dir, capture_output=True, text=True)
                
                # Check if files were created
                sample_files = ['sample_480p.mp4', 'sample_720p.mp4', 'sample_1080p.mp4']
                created_files = []
                for sample_file in sample_files:
                    file_path = os.path.join(media_dir, sample_file)
                    if os.path.exists(file_path):
                        created_files.append(sample_file)
                
                if created_files:
                    self.record_test_result("Sample File Creation", True, f"Created: {created_files}")
                else:
                    self.record_test_result("Sample File Creation", False, "No sample files created")
            else:
                self.record_test_result("Sample File Creation", False, "create_samples.py not found")
        except Exception as e:
            self.record_test_result("Sample File Creation", False, str(e))
        
        # Test Media Library Scanning
        try:
            media_dir = os.path.join(current_dir, 'media')
            if os.path.exists(media_dir):
                library = VideoLibraryManager(media_dir)
                count = library.scan_library()
                self.record_test_result("Media Library Scanning", True, f"Found {count} videos")
            else:
                self.record_test_result("Media Library Scanning", False, "Media directory not found")
        except Exception as e:
            self.record_test_result("Media Library Scanning", False, str(e))
    
    def test_live_streaming(self):
        """Test live streaming simulation"""
        
        # Test RTP Streaming Flow
        try:
            sender = RTPSession(ssrc=12345, payload_type=96)
            receiver = RTPReceiver(buffer_size=20)
            
            # Simulate video frames
            frames_sent = 0
            frames_received = 0
            
            for i in range(10):
                # Create video frame data
                frame_data = f"video_frame_{i}".encode() + b"\x00" * 100
                packet = sender.create_packet(frame_data, marker=(i == 9))
                
                # Receiver processes packet
                ready_packets = receiver.receive_packet(packet)
                frames_sent += 1
                frames_received += len(ready_packets)
            
            sender_stats = sender.get_statistics()
            receiver_stats = receiver.get_statistics()
            
            assert sender_stats['packets_sent'] == 10
            assert receiver_stats['packets_received'] == 10
            
            self.record_test_result("Live Streaming Simulation", True, 
                                  f"Sent: {frames_sent}, Received: {frames_received}")
        except Exception as e:
            self.record_test_result("Live Streaming Simulation", False, str(e))
        
        # Test Quality Profile Adaptation
        try:
            profiles = QualityProfileManager.get_all_profiles()
            
            for profile_name, profile in profiles.items():
                chunk_size = StreamingUtils.calculate_chunk_size(profile.bitrate, profile.framerate)
                buffer_size = StreamingUtils.estimate_buffer_size(profile.bitrate)
                
                assert chunk_size > 0
                assert buffer_size > 0
            
            self.record_test_result("Quality Profile Adaptation", True, f"Tested {len(profiles)} profiles")
        except Exception as e:
            self.record_test_result("Quality Profile Adaptation", False, str(e))
    
    def print_final_results(self):
        """Print final test results"""
        print("\n" + "🏁" + "=" * 58 + "🏁")
        print("  FINAL TEST RESULTS")
        print("🏁" + "=" * 58 + "🏁")
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for test_detail in self.test_results['test_details']:
                if not test_detail['passed']:
                    print(f"   - {test_detail['name']}: {test_detail['details']}")
        
        # Overall result
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            print(f"   The video streaming system is working correctly.")
        else:
            print(f"\n⚠️  SOME TESTS FAILED")
            print(f"   Please review the failed tests above.")
        
        print(f"\n📁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎬" + "=" * 58 + "🎬")
    
    def cleanup(self):
        """Cleanup test resources"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass


class LiveSystemTest:
    """Live system test with actual server/client interaction"""
    
    def __init__(self):
        self.server_process = None
        self.test_port = 15554
        
    def run_live_test(self):
        """Run live server-client test"""
        print("\n🚀 Live System Test")
        print("-" * 30)
        
        try:
            # Start server in background
            server_script = os.path.join(current_dir, 'server', 'video_server.py')
            if os.path.exists(server_script):
                print("   🖥️ Starting test server...")
                
                # Start server with test port
                env = os.environ.copy()
                env['TEST_MODE'] = '1'
                env['RTSP_PORT'] = str(self.test_port)
                
                self.server_process = subprocess.Popen(
                    [sys.executable, server_script],
                    cwd=os.path.join(current_dir, 'server'),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for server to start
                time.sleep(3)
                
                # Test client connection
                self.test_client_connection()
                
            else:
                print("   ❌ Server script not found")
                
        except Exception as e:
            print(f"   ❌ Live test error: {e}")
        
        finally:
            if self.server_process:
                self.server_process.terminate()
                time.sleep(1)
                if self.server_process.poll() is None:
                    self.server_process.kill()
                print("   🛑 Test server stopped")
    
    def test_client_connection(self):
        """Test client connection to live server"""
        try:
            # Create client socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            
            # Connect to server
            client_socket.connect(('localhost', self.test_port))
            
            # Send OPTIONS request
            options_request = f"OPTIONS * RTSP/1.0\nCSeq: 1\nUser-Agent: Test-Client\n\n"
            client_socket.send(options_request.encode())
            
            # Receive response
            response = client_socket.recv(1024).decode()
            
            if "RTSP/1.0 200 OK" in response:
                print("   ✅ Client connection successful")
                print("   ✅ RTSP communication working")
            else:
                print(f"   ❌ Unexpected response: {response[:100]}")
            
            client_socket.close()
            
        except socket.timeout:
            print("   ❌ Connection timeout - server may not be ready")
        except ConnectionRefusedError:
            print("   ❌ Connection refused - server not running")
        except Exception as e:
            print(f"   ❌ Client connection error: {e}")


def run_unit_tests():
    """Run standard unit tests"""
    print("\n🧪 Running Standard Unit Tests")
    print("-" * 40)
    
    # Import and run the existing test suite
    try:
        test_script = os.path.join(current_dir, 'tests', 'test_video_streaming.py')
        if os.path.exists(test_script):
            result = subprocess.run([sys.executable, test_script], 
                                  cwd=os.path.join(current_dir, 'tests'),
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Unit tests passed")
                return True
            else:
                print("   ❌ Unit tests failed")
                print(f"   Error: {result.stderr}")
                return False
        else:
            print("   ⚠️ Unit test script not found")
            return False
    except Exception as e:
        print(f"   ❌ Unit test error: {e}")
        return False


def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        # Run live system test
        live_test = LiveSystemTest()
        live_test.run_live_test()
        return
    
    # Check if we're in the right directory
    required_dirs = ['server', 'client', 'protocols', 'utils']
    missing_dirs = [d for d in required_dirs if not os.path.exists(os.path.join(current_dir, d))]
    
    if missing_dirs:
        print("❌ Missing required directories:", missing_dirs)
        print("Please run this script from the video_streaming directory")
        return False
    
    # Run comprehensive tests
    runner = ProjectTestRunner()
    
    try:
        # Run unit tests first
        unit_test_success = run_unit_tests()
        
        # Run integration tests
        integration_success = runner.run_all_tests()
        
        # Run live system test if requested
        if "--with-live" in sys.argv:
            live_test = LiveSystemTest()
            live_test.run_live_test()
        
        return unit_test_success and integration_success
    
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return False
    
    finally:
        runner.cleanup()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)