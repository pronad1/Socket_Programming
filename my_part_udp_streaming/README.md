# Assignment 4: UDP Multimedia Streaming

## Overview
This assignment implements a streaming client-server application using UDP (connectionless) sockets. The server streams multimedia files in chunks of 1000-2000 bytes to clients, allowing real-time playback during download.

## Features Implemented

### Server Features:
- ✅ UDP connectionless socket communication
- ✅ Random chunk sizes between 1000-2000 bytes
- ✅ Last packet handling (can be < 1000 bytes)
- ✅ Multiple client support with threading
- ✅ File listing and streaming capabilities
- ✅ Packet sequencing for ordered delivery
- ✅ Error handling and robust communication

### Client Features:
- ✅ UDP socket communication with server
- ✅ File listing and selection interface
- ✅ Real-time data buffering during streaming
- ✅ Automatic media player launch when sufficient data is received
- ✅ Progress monitoring and statistics
- ✅ Out-of-order packet handling
- ✅ Cross-platform media player support

## Project Structure
```
udp_streaming/
├── streaming_server.py      # UDP streaming server implementation
├── streaming_client.py      # UDP streaming client implementation
├── test_streaming.py        # Automated test script
├── media_files/            # Server media files directory
│   └── sample_media.txt    # Sample file for testing
├── client_buffer/          # Client buffer directory
└── README.md              # This documentation
```

## Testing Instructions

### Prerequisites
1. Python 3.7+ installed
2. Network access between client and server
3. Media player installed (VLC, Windows Media Player, etc.)

### Quick Test
1. **Start the server:**
   ```bash
   cd my_part_udp_streaming
   python streaming_server.py
   ```

2. **Start the client (in another terminal):**
   ```bash
   python streaming_client.py
   ```

3. **Test the streaming:**
   - Select option 1 to list available files
   - Select option 2 to stream a file
   - Choose file number or enter filename
   - Watch the streaming progress and media player launch

### Advanced Testing
Run the automated test script:
```bash
python test_streaming.py
```

## Technical Implementation Details

### UDP Protocol Design
- **Packet Format**: `[TYPE:1][SEQ:4][DATA_SIZE:4][BYTES_SENT:8][TOTAL_SIZE:8][DATA:variable]`
- **Packet Types**:
  - `D`: Data packet containing file chunk
  - `E`: End-of-stream marker
  - `INFO`: File information packet
  - `ERROR`: Error message packet

### Communication Flow
1. Client requests file list from server
2. Server responds with available media files
3. Client selects and requests specific file
4. Server sends file info and starts streaming
5. Server reads file in random chunks (1000-2000 bytes)
6. Each chunk sent as UDP datagram with sequence number
7. Client receives packets, handles out-of-order delivery
8. Client buffers data and launches media player when threshold reached
9. Streaming continues until complete file is transferred

### Buffer Management
- **Client Buffer Threshold**: 50KB before launching media player
- **Out-of-order Handling**: Packets buffered until sequence is complete
- **Real-time Playback**: Media player starts while download continues

### Error Handling
- Connection timeouts (30 seconds)
- Network errors and packet loss
- File not found errors
- Invalid requests
- Media player launch failures

## Performance Metrics
The implementation tracks:
- Total bytes transferred
- Number of packets sent/received
- Transfer speed (KB/s)
- Estimated time remaining
- Streaming completion percentage

## Cross-Platform Support
- **Windows**: Uses `os.startfile()` or default file association
- **macOS**: Uses `open` command
- **Linux**: Tries VLC, MPV, MPlayer, Totem, or xdg-open

## Assignment Requirements Compliance

✅ **Requirement 1**: Uses connectionless (UDP) sockets
✅ **Requirement 2**: Client contacts server requesting multimedia file
✅ **Requirement 3**: Server reads file contents in 1000-2000 byte chunks
✅ **Requirement 4**: Random chunk size distribution
✅ **Requirement 5**: Last packet can be less than 1000 bytes
✅ **Requirement 6**: Data sent as datagram packets
✅ **Requirement 7**: Client receives datagram packets
✅ **Requirement 8**: Media player launches when reasonable data received
✅ **Requirement 9**: Playback while downloading continues

## Usage Examples

### Command Line Options
```bash
# Start server on default port (9999)
python streaming_server.py

# Start server on custom port
python streaming_server.py 8888

# Start server on custom host and port
python streaming_server.py 8888 0.0.0.0

# Start client connecting to default server
python streaming_client.py

# Connect to remote server
python streaming_client.py 192.168.1.100 8888
```

### Interactive Client Session
```
UDP MULTIMEDIA STREAMING CLIENT
============================================================

Options:
1. List available media files
2. Stream a media file
3. Exit

Enter your choice (1-3): 1

Available media files:
--------------------------------------------------
 1. sample_media.txt (0.05 MB)
 2. video.mp4 (25.30 MB)
 3. audio.mp3 (4.20 MB)
--------------------------------------------------

Enter your choice (1-3): 2

Enter file number or filename: 2

Requesting media file: video.mp4
Starting to receive: video.mp4 (26533888 bytes)

🎬 Launching media player with 51200 bytes buffered...
✅ Media player launched successfully

Progress: 15.2% (4032512/26533888 bytes) Speed: 245.3 KB/s ETA: 1.5min Packets: 2546

✅ Streaming completed!
📊 Statistics:
   - Total bytes received: 26,533,888
   - Total packets: 16,783
   - Total time: 108.45 seconds
   - Average speed: 244.8 KB/s
   - Buffer file: client_buffer/video.mp4
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Change port number or kill existing process
2. **Firewall blocking**: Add firewall exception for Python
3. **Media player not launching**: Install VLC or check file associations
4. **Permission denied**: Run with appropriate permissions

### Debug Mode
Add print statements or increase logging for debugging:
- Packet sequence numbers
- Buffer states
- Network errors
- File operations

## Future Enhancements
- Packet loss detection and retransmission
- Adaptive bitrate streaming
- Multiple file format support
- GUI interface for client
- Authentication and security
- Compression for better efficiency

## Author
**Prosenjit Mondol**  
Computer Networks - Socket Programming Assignment  
October 2025