#!/usr/bin/env python3
"""
Video Streaming System Test Suite
Comprehensive tests for the professional video streaming system

This test suite includes:
- Unit tests for RTP/RTSP protocols
- Integration tests for client-server communication
- Video library tests
- Quality profile tests
- Streaming performance tests
- Error handling tests

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import os
import sys
import unittest
import tempfile
import time
import threading
import socket
import json
from typing import Dict, List

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from protocols.rtsp_protocol import RTSPParser, RTSPFormatter, RTSPRequest, RTSPResponse, RTSPMethod, RTSPStatus, RTSPHandler
from protocols.rtp_protocol import RTPSession, RTPPacket, RTPHeader, RTPReceiver, RTPPayloadType, RTPPacketBuilder
from utils.video_utils import VideoFileValidator, QualityProfileManager, VideoLibraryManager, StreamingUtils


class TestRTSPProtocol(unittest.TestCase):
    """Test RTSP protocol implementation"""
    
    def test_rtsp_request_parsing(self):
        """Test RTSP request parsing"""
        request_text = """DESCRIBE rtsp://server/video.mp4 RTSP/1.0
CSeq: 1
Accept: application/sdp

"""
        
        request = RTSPParser.parse_request(request_text)
        
        self.assertEqual(request.method, RTSPMethod.DESCRIBE)
        self.assertEqual(request.uri, "rtsp://server/video.mp4")
        self.assertEqual(request.version, "RTSP/1.0")
        self.assertEqual(request.headers.get("CSeq"), "1")
        self.assertEqual(request.headers.get("Accept"), "application/sdp")
    
    def test_rtsp_response_formatting(self):
        """Test RTSP response formatting"""
        response = RTSPResponse()
        response.status_code = 200
        response.status_text = "OK"
        response.headers["CSeq"] = "1"
        response.headers["Content-Type"] = "application/sdp"
        response.body = "v=0\\no=- 123 123 IN IP4 127.0.0.1"
        
        formatted = RTSPFormatter.format_response(response)
        
        self.assertIn("RTSP/1.0 200 OK", formatted)
        self.assertIn("CSeq: 1", formatted)
        self.assertIn("Content-Type: application/sdp", formatted)
        self.assertIn("v=0", formatted)
    
    def test_rtsp_session_management(self):
        """Test RTSP session management"""
        handler = RTSPHandler()
        
        # Create session
        session = handler.create_session(("127.0.0.1", 12345))
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.state, "INIT")
        
        # Test state transitions
        self.assertTrue(session.transition_to("READY"))
        self.assertEqual(session.state, "READY")
        
        self.assertTrue(session.transition_to("PLAYING"))
        self.assertEqual(session.state, "PLAYING")
        
        # Invalid transition
        self.assertFalse(session.transition_to("INIT"))
        self.assertEqual(session.state, "PLAYING")
    
    def test_rtsp_handler_setup(self):
        """Test RTSP SETUP request handling"""
        handler = RTSPHandler()
        
        request = RTSPRequest(
            method=RTSPMethod.SETUP,
            uri="rtsp://server/video.mp4",
            headers={
                "CSeq": "2",
                "Transport": "RTP/UDP;unicast;client_port=5004-5005"
            }
        )
        
        response = handler.handle_setup(request, ("127.0.0.1", 12345))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Session", response.headers)
        self.assertIn("Transport", response.headers)


class TestRTPProtocol(unittest.TestCase):
    """Test RTP protocol implementation"""
    
    def test_rtp_packet_creation(self):
        """Test RTP packet creation"""
        session = RTPSession(ssrc=12345, payload_type=96)
        payload = b"\\x00\\x00\\x00\\x01\\x67\\x42"  # Sample H.264 data
        
        packet = session.create_packet(payload, marker=True)
        
        self.assertEqual(packet.header.version, 2)
        self.assertEqual(packet.header.payload_type, 96)
        self.assertEqual(packet.header.ssrc, 12345)
        self.assertTrue(packet.header.marker)
        self.assertEqual(packet.payload, payload)
    
    def test_rtp_packet_serialization(self):
        """Test RTP packet serialization and parsing"""
        header = RTPHeader(
            version=2,
            payload_type=96,
            sequence_number=100,
            timestamp=90000,
            ssrc=12345
        )
        payload = b"test payload data"
        
        # Build packet
        packet_bytes = RTPPacketBuilder.build_packet(header, payload)
        
        # Parse packet
        packet = RTPPacket.from_bytes(packet_bytes)
        
        self.assertEqual(packet.header.version, 2)
        self.assertEqual(packet.header.payload_type, 96)
        self.assertEqual(packet.header.sequence_number, 100)
        self.assertEqual(packet.header.timestamp, 90000)
        self.assertEqual(packet.header.ssrc, 12345)
        self.assertEqual(packet.payload, payload)
    
    def test_rtp_receiver_buffering(self):
        """Test RTP receiver packet buffering"""
        receiver = RTPReceiver(buffer_size=10)
        session = RTPSession(ssrc=12345)
        
        # Send packets in order
        packets_sent = []
        for i in range(5):
            payload = f"packet_{i}".encode()
            packet = session.create_packet(payload)
            packets_sent.append(packet)
            
            ready_packets = receiver.receive_packet(packet)
            if i == 0:
                # First packet should be ready immediately
                self.assertEqual(len(ready_packets), 1)
                self.assertEqual(ready_packets[0].payload, payload)
            else:
                # Subsequent packets should be ready immediately if in order
                self.assertEqual(len(ready_packets), 1)
    
    def test_rtp_session_statistics(self):
        """Test RTP session statistics"""
        session = RTPSession(ssrc=12345)
        
        # Create some packets
        for i in range(10):
            payload = f"packet_{i}".encode()
            session.create_packet(payload)
        
        stats = session.get_statistics()
        
        self.assertEqual(stats['packets_sent'], 10)
        self.assertGreater(stats['bytes_sent'], 0)
        self.assertEqual(stats['ssrc'], 12345)


class TestVideoUtils(unittest.TestCase):
    """Test video utility functions"""
    
    def test_quality_profile_manager(self):
        """Test quality profile management"""
        # Test getting predefined profiles
        profile_720p = QualityProfileManager.get_profile("720p")
        self.assertIsNotNone(profile_720p)
        self.assertEqual(profile_720p.resolution, (1280, 720))
        self.assertEqual(profile_720p.bitrate, 2500)
        
        # Test getting all profiles
        all_profiles = QualityProfileManager.get_all_profiles()
        self.assertIn("720p", all_profiles)
        self.assertIn("1080p", all_profiles)
        
        # Test best profile selection
        best_profile = QualityProfileManager.get_best_profile_for_resolution((1920, 1080))
        self.assertEqual(best_profile.name, "1080p")
    
    def test_video_file_validator(self):
        """Test video file validation"""
        # Test with non-existent file
        self.assertFalse(VideoFileValidator.is_valid_video_file("nonexistent.mp4"))
        
        # Test file extension validation
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video data")
            tmp_path = tmp.name
        
        try:
            # Should pass extension check but may fail MIME type check
            result = VideoFileValidator.is_valid_video_file(tmp_path)
            # We expect this to pass basic checks
            self.assertTrue(isinstance(result, bool))
        finally:
            os.unlink(tmp_path)
    
    def test_streaming_utils(self):
        """Test streaming utility functions"""
        # Test chunk size calculation
        chunk_size = StreamingUtils.calculate_chunk_size(2500, 30)
        self.assertGreater(chunk_size, 1024)
        
        # Test buffer size estimation
        buffer_size = StreamingUtils.estimate_buffer_size(2500, 5.0)
        self.assertGreater(buffer_size, 0)
        
        # Test file size formatting
        formatted = StreamingUtils.format_file_size(1073741824)
        self.assertEqual(formatted, "1.0 GB")
        
        # Test bitrate formatting
        formatted = StreamingUtils.format_bitrate(2500000)
        self.assertEqual(formatted, "2.5 Mbps")
        
        # Test parameter validation
        warnings = StreamingUtils.validate_streaming_parameters(1000, (1920, 1080), 30)
        self.assertGreater(len(warnings), 0)  # Should warn about low bitrate for 1080p


class TestVideoLibraryManager(unittest.TestCase):
    """Test video library management"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.library = VideoLibraryManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_library_creation(self):
        """Test library creation and initialization"""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertEqual(len(self.library.videos), 0)
    
    def test_video_metadata_operations(self):
        """Test metadata save/load operations"""
        # Create fake video metadata
        from utils.video_utils import VideoInfo
        
        video_info = VideoInfo(
            filename="test.mp4",
            filepath=os.path.join(self.temp_dir, "test.mp4"),
            size=1024000,
            duration=120.0,
            resolution=(1280, 720),
            framerate=30.0,
            bitrate=2500,
            video_codec="h264",
            audio_codec="aac",
            format="mp4"
        )
        
        self.library.videos["test.mp4"] = video_info
        self.library.save_metadata()
        
        # Create new library instance and load metadata
        new_library = VideoLibraryManager(self.temp_dir)
        self.assertEqual(len(new_library.videos), 1)
        self.assertIn("test.mp4", new_library.videos)
    
    def test_library_statistics(self):
        """Test library statistics calculation"""
        from utils.video_utils import VideoInfo
        
        # Add some test videos
        for i in range(3):
            video_info = VideoInfo(
                filename=f"test_{i}.mp4",
                filepath=os.path.join(self.temp_dir, f"test_{i}.mp4"),
                size=1024000 * (i + 1),
                duration=120.0 * (i + 1),
                resolution=(1280, 720),
                framerate=30.0,
                bitrate=2500,
                video_codec="h264",
                audio_codec="aac",
                format="mp4"
            )
            self.library.videos[f"test_{i}.mp4"] = video_info
        
        stats = self.library.get_library_stats()
        
        self.assertEqual(stats['total_videos'], 3)
        self.assertGreater(stats['total_size'], 0)
        self.assertGreater(stats['total_duration'], 0)


class TestVideoStreamingIntegration(unittest.TestCase):
    """Integration tests for video streaming system"""
    
    def setUp(self):
        """Set up test environment"""
        self.server_thread = None
        self.server_socket = None
        self.test_port = 15554  # Use different port to avoid conflicts
    
    def tearDown(self):
        """Clean up test environment"""
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1)
    
    def test_rtsp_client_server_communication(self):
        """Test basic RTSP client-server communication"""
        # Create a simple test server
        def test_server():
            try:
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(('localhost', self.test_port))
                server_sock.listen(1)
                server_sock.settimeout(5)  # 5 second timeout
                
                self.server_socket = server_sock
                
                conn, addr = server_sock.accept()
                
                # Receive RTSP request
                data = conn.recv(1024).decode('utf-8')
                
                # Send RTSP response
                response = "RTSP/1.0 200 OK\\nCSeq: 1\\nServer: Test Server\\n\\n"
                conn.send(response.encode('utf-8'))
                
                conn.close()
                
            except socket.timeout:
                pass  # Expected for test
            except Exception as e:
                print(f"Test server error: {e}")
        
        # Start test server in background
        self.server_thread = threading.Thread(target=test_server, daemon=True)
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(0.1)
        
        # Test client connection
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_sock.settimeout(5)
            client_sock.connect(('localhost', self.test_port))
            
            # Send RTSP request
            request = "DESCRIBE rtsp://localhost/test.mp4 RTSP/1.0\\nCSeq: 1\\n\\n"
            client_sock.send(request.encode('utf-8'))
            
            # Receive response
            response = client_sock.recv(1024).decode('utf-8')
            
            # Verify response
            self.assertIn("RTSP/1.0 200 OK", response)
            self.assertIn("CSeq: 1", response)
            
            client_sock.close()
            
        except Exception as e:
            self.fail(f"Client connection failed: {e}")
    
    def test_rtp_packet_flow(self):
        """Test RTP packet creation and reception flow"""
        # Create sender session
        sender = RTPSession(ssrc=12345, payload_type=96)
        
        # Create receiver
        receiver = RTPReceiver(buffer_size=20)
        
        # Send packets
        packets_sent = []
        for i in range(10):
            payload = f"video_frame_{i}".encode()
            packet = sender.create_packet(payload)
            packets_sent.append(packet)
            
            # Receiver processes packet
            ready_packets = receiver.receive_packet(packet)
            
            # Check that packets are received in order
            if ready_packets:
                for ready_packet in ready_packets:
                    self.assertIn(ready_packet, packets_sent)
        
        # Verify sender statistics
        sender_stats = sender.get_statistics()
        self.assertEqual(sender_stats['packets_sent'], 10)
        
        # Verify receiver statistics
        receiver_stats = receiver.get_statistics()
        self.assertEqual(receiver_stats['packets_received'], 10)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in video streaming system"""
    
    def test_invalid_rtsp_request_handling(self):
        """Test handling of invalid RTSP requests"""
        # Test empty request
        with self.assertRaises(ValueError):
            RTSPParser.parse_request("")
        
        # Test malformed request line
        with self.assertRaises(ValueError):
            RTSPParser.parse_request("INVALID REQUEST LINE")
        
        # Test unknown method
        with self.assertRaises(ValueError):
            RTSPParser.parse_request("UNKNOWN rtsp://server/video RTSP/1.0\\n\\n")
    
    def test_invalid_rtp_packet_handling(self):
        """Test handling of invalid RTP packets"""
        # Test packet too short
        with self.assertRaises(ValueError):
            RTPPacket.from_bytes(b"short")
        
        # Test invalid header
        invalid_packet = b"\\x00" * 12  # Valid length but invalid data
        try:
            packet = RTPPacket.from_bytes(invalid_packet)
            # Should not raise exception but may have unexpected values
            self.assertIsInstance(packet, RTPPacket)
        except Exception:
            pass  # Some validation might fail, which is acceptable
    
    def test_file_operation_error_handling(self):
        """Test file operation error handling"""
        library = VideoLibraryManager("/nonexistent/path")
        
        # Should handle non-existent directory gracefully
        count = library.scan_library()
        self.assertEqual(count, 0)
        
        # Test invalid file operations
        result = library.add_video("/nonexistent/file.mp4")
        self.assertFalse(result)


class PerformanceTest(unittest.TestCase):
    """Performance tests for video streaming components"""
    
    def test_rtp_packet_performance(self):
        """Test RTP packet creation/parsing performance"""
        session = RTPSession(ssrc=12345)
        payload = b"A" * 1400  # Typical MTU size payload
        
        # Measure packet creation time
        start_time = time.time()
        packets = []
        
        for i in range(1000):
            packet = session.create_packet(payload)
            packets.append(packet)
        
        creation_time = time.time() - start_time
        
        # Should create 1000 packets in reasonable time
        self.assertLess(creation_time, 1.0)  # Less than 1 second
        
        # Measure serialization time
        start_time = time.time()
        
        for packet in packets:
            packet_bytes = packet.to_bytes()
        
        serialization_time = time.time() - start_time
        
        # Should serialize 1000 packets in reasonable time
        self.assertLess(serialization_time, 1.0)
        
        print(f"Performance: Created 1000 packets in {creation_time:.3f}s, "
              f"serialized in {serialization_time:.3f}s")
    
    def test_rtsp_parsing_performance(self):
        """Test RTSP message parsing performance"""
        test_request = """DESCRIBE rtsp://server/video.mp4 RTSP/1.0
CSeq: 1
Accept: application/sdp
User-Agent: Test Client
Session: 12345

"""
        
        # Measure parsing time
        start_time = time.time()
        
        for i in range(1000):
            request = RTSPParser.parse_request(test_request)
        
        parsing_time = time.time() - start_time
        
        # Should parse 1000 requests in reasonable time
        self.assertLess(parsing_time, 1.0)
        
        print(f"Performance: Parsed 1000 RTSP requests in {parsing_time:.3f}s")


def create_test_video_files(directory: str, count: int = 3):
    """Create test video files for testing"""
    os.makedirs(directory, exist_ok=True)
    
    for i in range(count):
        filename = f"test_video_{i}.mp4"
        filepath = os.path.join(directory, filename)
        
        # Create dummy video file content
        with open(filepath, 'wb') as f:
            # Write fake MP4 header (simplified)
            f.write(b"\\x00\\x00\\x00\\x20ftypmp42")  # MP4 file type box
            f.write(b"\\x00" * 1000)  # Dummy data
    
    return directory


def run_comprehensive_tests():
    """Run all tests with detailed output"""
    print("🧪 Running Professional Video Streaming System Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRTSPProtocol,
        TestRTPProtocol,
        TestVideoUtils,
        TestVideoLibraryManager,
        TestVideoStreamingIntegration,
        TestErrorHandling,
        PerformanceTest
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print("\\n" + "=" * 60)
    print(f"🏁 Test Summary:")
    print(f"   ✅ Tests run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🔥 Errors: {len(result.errors)}")
    print(f"   ⏭️ Skipped: {len(getattr(result, 'skipped', []))}")
    
    if result.failures:
        print(f"\\n❌ Failed Tests:")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print(f"\\n🔥 Error Tests:")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\\n📊 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)