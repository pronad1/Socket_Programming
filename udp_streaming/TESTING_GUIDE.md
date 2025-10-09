# Manual Testing Guide

## Quick Test Instructions

### Step 1: Navigate to Assignment Directory
```powershell
cd d:\Languages\Socket_Programming\assignments\udp_streaming
```

### Step 2: Test Server Startup
```powershell
python streaming_server.py
```
**Expected Output:**
```
UDP STREAMING SERVER
============================================================
Server Configuration:
  Host: localhost
  Port: 9999
  Media Directory: d:\Languages\Socket_Programming\assignments\udp_streaming\media_files
============================================================
UDP Streaming Server started on localhost:9999
Media directory: d:\Languages\Socket_Programming\assignments\udp_streaming\media_files
Available media files:
  - sample_media.txt (0.05 MB)

Waiting for client requests...
Press Ctrl+C to stop the server
```

### Step 3: Test Client Connection (New Terminal)
```powershell
# Open new PowerShell terminal
cd d:\Languages\Socket_Programming\assignments\udp_streaming
python streaming_client.py
```

**Expected Output:**
```
Connected to streaming server at localhost:9999

============================================================
UDP MULTIMEDIA STREAMING CLIENT
============================================================

Options:
1. List available media files
2. Stream a media file  
3. Exit

Enter your choice (1-3):
```

### Step 4: Test File Listing
- Enter `1` to list files
- Should show available media files

### Step 5: Test File Streaming
- Enter `2` to stream a file
- Select file number or enter filename
- Watch streaming progress
- Media player should launch automatically

## Automated Testing

### Run Full Test Suite
```powershell
python test_streaming.py
```

This will automatically:
- ✅ Test environment setup
- ✅ Test server startup  
- ✅ Test client-server communication
- ✅ Test file listing
- ✅ Test small file streaming
- ✅ Test medium file streaming
- ✅ Test packet structure validation
- ✅ Test error handling
- ✅ Generate detailed report

## Troubleshooting

### Common Issues:

1. **"Address already in use"**
   ```powershell
   netstat -ano | findstr :9999
   taskkill /PID <process_id> /F
   ```

2. **"No module named ..."**
   ```powershell
   python --version  # Check Python version
   pip install --upgrade pip
   ```

3. **Permission denied**
   - Run PowerShell as Administrator
   - Check firewall settings

4. **Media player not launching**
   - Install VLC Media Player
   - Check file associations
   - Test with .txt files first

### Expected Test Results:
```
============================================================
TEST SUMMARY
============================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%

🎉 ALL TESTS PASSED! Your UDP streaming assignment is working correctly!
```

## Performance Benchmarks

### Expected Performance:
- **Small files (< 5KB)**: < 1 second
- **Medium files (50KB)**: 2-5 seconds  
- **Large files (1MB+)**: 10-30 seconds
- **Throughput**: 100-500 KB/s (depending on system)
- **Packet loss**: Should handle gracefully

### File Size Limits:
- **Minimum chunk**: 1000 bytes
- **Maximum chunk**: 2000 bytes
- **Last chunk**: Can be < 1000 bytes
- **Maximum file**: Limited by available disk space

## Manual Verification Checklist

- [ ] Server starts without errors
- [ ] Client connects successfully  
- [ ] File list displays correctly
- [ ] Small files stream completely
- [ ] Large files stream with progress updates
- [ ] Media player launches automatically
- [ ] Streaming works while media plays
- [ ] Proper error handling for invalid requests
- [ ] Graceful shutdown with Ctrl+C
- [ ] Buffer files created in client_buffer/
- [ ] Packet sequencing works correctly
- [ ] Cross-platform compatibility (if testing on different OS)

## Assignment Grading Criteria

✅ **Technical Implementation (40%)**
- UDP socket usage
- Connectionless communication
- Random chunk sizes (1000-2000 bytes)
- Proper packet handling

✅ **Functionality (30%)**  
- File listing works
- Streaming completes successfully
- Media player integration
- Real-time playback during download

✅ **Code Quality (20%)**
- Clear documentation
- Error handling
- Modular design
- Professional structure

✅ **Testing & Demonstration (10%)**
- Comprehensive testing
- Working demo
- Performance metrics
- Problem-solving approach