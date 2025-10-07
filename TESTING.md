# Testing Guide for Socket Programming Projects

This guide explains how to test and validate all socket programming projects including the UDP streaming assignment and the professional video streaming system.

## 🧪 Available Test Scripts

### 1. Quick Project Validation
```bash
# Run from project root directory
python validate_project.py

# Quick health check only
python validate_project.py --quick

# Check specific components
python validate_project.py --assignment   # Check UDP assignment only
python validate_project.py --streaming    # Check video streaming only
```

### 2. Assignment Testing (UDP Streaming)
```bash
# Navigate to assignment directory
cd assignments/udp_streaming

# Quick validation test
python quick_test.py

# Comprehensive test suite
python test_streaming.py

# Manual testing
python streaming_server.py    # Terminal 1
python streaming_client.py    # Terminal 2
```

### 3. Video Streaming System Testing
```bash
# Navigate to video streaming directory
cd src/video_streaming

# Run comprehensive project tests
python run_project_tests.py

# Run with live server-client testing
python run_project_tests.py --with-live

# Run unit tests only
python tests/test_video_streaming.py

# Quick system startup
python start_streaming.py all
```

## 📋 Test Categories

### Basic Validation Tests
- **Project Structure**: Verify all required files and directories exist
- **Dependencies**: Check Python version and required modules
- **Network**: Test socket creation and port binding
- **Imports**: Validate all modules can be imported

### Assignment Tests (UDP Streaming)
- **Server Functionality**: UDP server starts and accepts connections
- **Client Functionality**: UDP client connects and receives data
- **Streaming Protocol**: Packet chunking (1000-2000 bytes) works correctly
- **Media Integration**: External media player launches successfully
- **Error Handling**: Network errors handled gracefully

### Video Streaming Tests
- **Protocol Tests**: RTSP and RTP implementation validation
- **Server Tests**: Video server initialization and session management
- **Client Tests**: GUI client functionality and controls
- **Integration Tests**: End-to-end client-server communication
- **Performance Tests**: Streaming throughput and latency
- **Live Tests**: Actual server-client interaction

## 🚀 Quick Start Testing

### 1. Complete System Validation
```bash
# From project root
python validate_project.py
```
**Expected Output:**
```
🔍 Socket Programming Project Validation
==================================================

📋 Project Structure
------------------------------
   ✅ Directory: src/python/simple_socket
   ✅ Directory: src/video_streaming/server
   ✅ Directory: src/video_streaming/client
   ✅ Directory: assignments/udp_streaming

📋 Python Dependencies
------------------------------
   ✅ Python 3.7+
      Found: Python 3.11
   ✅ Module: socket
   ✅ Module: threading
   ✅ Module: tkinter
   
🏁================================================🏁
  VALIDATION SUMMARY
🏁================================================🏁
📊 Results: 15/15 checks passed
🎉 ALL CHECKS PASSED!
```

### 2. UDP Assignment Quick Test
```bash
cd assignments/udp_streaming
python quick_test.py
```
**Expected Output:**
```
🎬 UDP Streaming Assignment - Quick Test
========================================

🔍 Testing Components...
   ✅ Server file exists
   ✅ Client file exists
   ✅ Media file created (1.0 MB)

🚀 Running Streaming Test...
   ✅ Server started on port 12000
   ✅ Client connected successfully
   ✅ Streaming completed: 694 packets
   ✅ Chunk sizes randomized (1000-2000 bytes)
   ✅ All packets received correctly

📊 Test Results:
   File size: 1048576 bytes
   Packets sent: 694
   Average chunk size: 1511 bytes
   Streaming time: 2.3 seconds

🎉 UDP STREAMING ASSIGNMENT WORKING CORRECTLY! 🎉
```

### 3. Video Streaming System Test
```bash
cd src/video_streaming
python run_project_tests.py
```
**Expected Output:**
```
🎬========================================================🎬
  Professional Video Streaming System - Project Tests
  Complete System Validation and Integration Testing
🎬========================================================🎬

🧪 Protocol Tests
--------------------------------------------------
   ✅ RTSP Request Parsing
   ✅ RTSP Response Formatting
   ✅ RTP Packet Creation
   ✅ RTP Packet Serialization
   ✅ RTP Receiver Functionality

🧪 Server Tests
--------------------------------------------------
   ✅ Server Initialization
   ✅ Server Port Binding
   ✅ RTSP Handler

🧪 Performance Tests
--------------------------------------------------
   ✅ RTP Packet Performance: 0.043s for 100 packets
   ✅ RTSP Parsing Performance: 0.012s for 100 requests

🏁========================================================🏁
  FINAL TEST RESULTS
🏁========================================================🏁
📊 Test Summary:
   Total Tests: 25
   ✅ Passed: 25
   ❌ Failed: 0
   📈 Success Rate: 100.0%

🎉 ALL TESTS PASSED! 🎉
```

## 🔧 Troubleshooting Test Issues

### Common Issues and Solutions

#### 1. Import Errors
```
❌ ImportError: No module named 'protocols.rtsp_protocol'
```
**Solution:**
```bash
# Ensure you're running from the correct directory
cd src/video_streaming
python run_project_tests.py
```

#### 2. Port Already in Use
```
❌ OSError: [WinError 10048] Only one usage of each socket address
```
**Solution:**
```bash
# Wait a few seconds and retry, or use different ports
# Kill any running servers:
# Windows: netstat -ano | findstr :554
# Linux/Mac: lsof -i :554
```

#### 3. Permission Issues
```
❌ PermissionError: [WinError 5] Access is denied
```
**Solution:**
```bash
# Run as administrator (Windows) or with sudo (Linux/Mac)
# Or use ports > 1024:
python video_server.py --port 8554
```

#### 4. GUI/tkinter Issues
```
❌ ImportError: No module named '_tkinter'
```
**Solution:**
```bash
# Windows: Install Python with tkinter option
# Linux: sudo apt-get install python3-tk
# Mac: brew install python-tk
```

#### 5. Missing Sample Files
```
❌ FileNotFoundError: Sample media files not found
```
**Solution:**
```bash
cd src/video_streaming/media
python create_samples.py
```

## 📊 Test Results Interpretation

### Success Indicators
- ✅ **Green checkmarks**: All tests passed
- 📈 **100% success rate**: System is working correctly
- 🎉 **"ALL TESTS PASSED!"**: Ready for use

### Warning Indicators
- ⚠️ **Yellow warnings**: Minor issues, system may still work
- 📝 **Test details**: Check specific test output for details

### Failure Indicators
- ❌ **Red X marks**: Critical failures need attention
- 💥 **Critical errors**: System cannot function properly
- 📋 **Failed test list**: Shows exactly what needs fixing

## 🔬 Advanced Testing

### Performance Benchmarking
```bash
# Run performance-specific tests
cd src/video_streaming
python run_project_tests.py --performance-only

# Benchmark streaming throughput
python -c "
from protocols.rtp_protocol import RTPSession
import time
session = RTPSession()
start = time.time()
for i in range(1000):
    session.create_packet(b'A' * 1400)
print(f'Performance: {(time.time() - start):.3f}s for 1000 packets')
"
```

### Live Integration Testing
```bash
# Start server and client automatically for testing
cd src/video_streaming
python run_project_tests.py --with-live

# Manual live testing
python start_streaming.py server    # Terminal 1
python start_streaming.py client    # Terminal 2
```

### Stress Testing
```bash
# Test with multiple concurrent clients
# Terminal 1: Start server
python start_streaming.py server

# Terminals 2-4: Start multiple clients
python video_client.py localhost 554 5004
python video_client.py localhost 554 5006  
python video_client.py localhost 554 5008
```

## 📁 Test File Locations

```
Socket_Programming/
├── validate_project.py                    # Main validation script
├── assignments/udp_streaming/
│   ├── quick_test.py                      # Quick UDP test
│   └── test_streaming.py                  # Comprehensive UDP tests
└── src/video_streaming/
    ├── run_project_tests.py               # Main video streaming tests
    ├── tests/test_video_streaming.py      # Unit tests
    └── start_streaming.py                 # System launcher
```

## 🎯 Testing Checklist

Before submitting or deploying:

- [ ] **Run full validation**: `python validate_project.py` ✅
- [ ] **Test UDP assignment**: `cd assignments/udp_streaming && python quick_test.py` ✅  
- [ ] **Test video streaming**: `cd src/video_streaming && python run_project_tests.py` ✅
- [ ] **Verify sample files**: Check media files are created ✅
- [ ] **Test network connectivity**: Ensure ports are available ✅
- [ ] **Check cross-platform**: Test on target OS ✅
- [ ] **Performance validation**: Ensure acceptable streaming rates ✅

## 📞 Getting Help

If tests are failing:

1. **Check Dependencies**: Ensure Python 3.7+ and all modules are installed
2. **Verify Structure**: Confirm all required files exist
3. **Network Issues**: Check firewall and port availability  
4. **Run Step-by-Step**: Use individual test scripts to isolate issues
5. **Check Logs**: Review detailed error messages in test output

**Success Criteria:**
- All validation checks pass ✅
- UDP assignment streams video successfully ✅
- Video streaming system starts and connects ✅
- No critical errors in any test ✅

---
*Professional Socket Programming System - Testing Guide*  
*Author: Prosenjit Mondol | Date: October 2025*