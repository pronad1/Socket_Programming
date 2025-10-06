# Protocol Specifications

This document outlines the communication protocols used in the Socket Programming Laboratory assignments.

## Simple TCP Client-Server Protocol

### Overview
The simple TCP protocol demonstrates basic client-server communication using reliable TCP connections.

### Message Format
- **Encoding**: UTF-8
- **Maximum Message Size**: 1024 bytes
- **Termination**: Messages are null-terminated

### Protocol Flow

1. **Connection Establishment**
   - Client initiates connection to server
   - Server accepts connection and creates new thread for client
   - Connection remains open until explicitly closed

2. **Message Exchange**
   ```
   Client -> Server: "Hello World"
   Server -> Client: "[timestamp] Echo: HELLO WORLD"
   ```

3. **Special Commands**
   - `time`: Server responds with current timestamp
   - `quit`: Server responds with "Goodbye!" and closes connection

4. **Connection Termination**
   - Client sends "quit" command
   - Server closes connection
   - Client closes socket

### Error Handling
- Connection timeout: 10 seconds
- Automatic reconnection not implemented
- Graceful handling of network errors

## UDP Pinger Protocol

### Overview
Simulates ping functionality using UDP packets with packet loss simulation.

### Packet Format
```
Ping [sequence_number] [timestamp]
```

### Features
- Packet loss simulation (30% default)
- RTT (Round Trip Time) calculation
- Timeout handling (1 second default)

## HTTP Web Server Protocol

### Overview
Basic HTTP/1.1 server implementation supporting GET requests for static files.

### Supported Methods
- `GET`: Retrieve static files

### Response Codes
- `200 OK`: File found and served
- `404 Not Found`: Requested file not available
- `500 Internal Server Error`: Server error

### File Types Supported
- HTML (.html, .htm)
- Text files (.txt)
- Images (.jpg, .png, .gif)
- CSS (.css)
- JavaScript (.js)

## SMTP Client Protocol

### Overview
Implementation of Simple Mail Transfer Protocol (SMTP) client for sending emails.

### Protocol Commands
- `HELO`: Identify client to server
- `MAIL FROM`: Specify sender
- `RCPT TO`: Specify recipient
- `DATA`: Begin message content
- `QUIT`: End session

### Security
- Basic authentication support
- SSL/TLS encryption (optional)

## Error Codes and Handling

### Common Error Scenarios
1. **Connection Refused**: Server not running
2. **Timeout**: Network latency or server overload
3. **Protocol Error**: Invalid message format
4. **Resource Exhaustion**: Too many connections

### Best Practices
- Always close sockets properly
- Implement timeout mechanisms
- Handle exceptions gracefully
- Log errors for debugging