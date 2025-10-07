# Socket Programming Laboratory

A comprehensive collection of network programming assignments implementing various socket-based applications and protocols. This project demonstrates fundamental networking concepts through practical implementations using TCP and UDP sockets.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Available Programs](#available-programs)
- [Testing](#testing)
- [Implementation Details](#implementation-details)
- [Learning Objectives](#learning-objectives)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

This repository contains implementations of various socket programming assignments designed to provide hands-on experience with network programming concepts. The projects cover client-server architectures, protocol implementations, and network application development.

### Key Concepts Covered:
- TCP and UDP socket programming
- Client-server communication
- Protocol design and implementation
- Network application development
- Error handling and reliability
- Performance optimization

## Features

- **Multi-language Support**: Implementations available in Python, Java, and C
- **Comprehensive Examples**: Complete client-server applications
- **Protocol Implementations**: Custom protocols for various network services
- **Error Handling**: Robust error detection and recovery mechanisms
- **Documentation**: Detailed code documentation and usage examples
- **Testing Tools**: Built-in testing utilities and performance benchmarks

## Prerequisites

### Software Requirements:
- **Python 3.7+** (for Python implementations)
- **Java 8+** (for Java implementations)
- **GCC Compiler** (for C implementations)
- **Git** (for version control)

### Network Requirements:
- Access to localhost for testing
- Optional: Multiple machines for distributed testing
- Firewall permissions for socket communication

### Knowledge Prerequisites:
- Basic understanding of networking concepts
- Familiarity with chosen programming language
- Understanding of client-server architecture

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pronad1/Socket_Programming.git
cd Socket_Programming
```

### 2. Set Up Python Environment (if using Python)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install required packages (if any)
pip install -r requirements.txt
```

### 3. Compile C Programs (if using C)
```bash
# Navigate to C source directory
cd src/c/

# Compile server and client
gcc -o server server.c
gcc -o client client.c
```

### 4. Compile Java Programs (if using Java)
```bash
# Navigate to Java source directory
cd src/java/

# Compile Java files
javac *.java
```

## Project Structure

```
Socket_Programming/
├── README.md                          # This comprehensive guide
├── requirements.txt                   # Python dependencies
├── src/                              # Source code directory
│   ├── python/                       # Python implementations
│   │   ├── simple_socket/           # Basic socket examples
│   │   │   ├── server.py           # TCP server implementation
│   │   │   └── client.py           # TCP client implementation
│   │   ├── web_server/             # HTTP server implementation
│   │   │   └── webserver.py        # Basic HTTP web server
│   │   ├── udp_pinger/             # UDP ping implementation
│   │   │   ├── udp_pinger_server.py
│   │   │   └── udp_pinger_client.py
│   │   └── smtp_client/            # SMTP client implementation
│   │       └── smtp_client.py
│   ├── java/                        # Java implementations
│   │   ├── SimpleSocket/           # Basic socket examples
│   │   ├── UDPPinger/             # UDP ping implementation
│   │   └── WebProxy/              # Web proxy server
│   ├── c/                          # C implementations
│   │   ├── simple_socket/         # Basic socket examples
│   │   ├── rdt_protocol/          # Reliable data transfer
│   │   └── distance_vector/       # Distance vector routing
│   └── video_streaming/            # 🎬 Professional Video Streaming System
│       ├── server/                 # RTSP/RTP streaming server
│       │   └── video_server.py    # Main video streaming server
│       ├── client/                 # GUI video streaming client
│       │   └── video_client.py    # Professional video client
│       ├── protocols/              # Protocol implementations
│       │   ├── rtsp_protocol.py   # RTSP protocol handling
│       │   └── rtp_protocol.py    # RTP packet management
│       ├── utils/                  # Video streaming utilities
│       │   └── video_utils.py     # Video processing utilities
│       ├── media/                  # Sample media files
│       │   └── create_samples.py  # Media file generator
│       ├── tests/                  # Comprehensive test suite
│       │   └── test_video_streaming.py
│       └── README.md               # Video streaming documentation
├── assignments/                      # Programming assignments
│   ├── udp_streaming/               # UDP streaming assignment
│   │   ├── streaming_server.py     # UDP streaming server
│   │   ├── streaming_client.py     # UDP streaming client
│   │   ├── test_streaming.py       # Automated test suite
│   │   └── quick_test.py           # Quick validation tool
│   ├── tcp_file_transfer/          # File transfer assignment
│   ├── multi_threading/            # Multi-threading exercises
│   └── network_protocols/          # Protocol implementation
├── docs/                            # Documentation and guides
│   ├── protocol_specifications.md  # Protocol documentation
│   ├── testing_guide.md           # Testing procedures
│   └── performance_analysis.md    # Performance metrics
├── tests/                          # Test files and scripts
│   ├── unit_tests/                 # Unit test cases
│   ├── integration_tests/          # Integration test cases
│   └── performance_tests/          # Performance benchmarks
└── examples/                       # Example configurations
    ├── sample_configs/             # Sample configuration files
    └── demo_scripts/              # Demonstration scripts
```

## Usage

### Basic Client-Server Example

#### Running the Python TCP Server:
```bash
cd src/python/simple_socket/
python server.py [port_number]
```

#### Running the Python TCP Client:
```bash
cd src/python/simple_socket/
python client.py [server_host] [server_port]
```

#### Example Session:
```bash
# Terminal 1 (Server)
python server.py 12000
Server listening on port 12000...

# Terminal 2 (Client)
python client.py localhost 12000
Connected to server at localhost:12000
Enter message: Hello, Server!
Server response: HELLO, SERVER!
```

## Available Programs

### 1. Simple Client-Server Socket Program
- **Languages**: Python, Java, C
- **Protocol**: TCP
- **Description**: Basic client-server communication with message exchange
- **Location**: `src/[language]/simple_socket/`

### 2. Web Server Implementation
- **Language**: Python
- **Protocol**: HTTP
- **Description**: Basic HTTP web server serving static files
- **Location**: `src/python/web_server/`

### 3. UDP Pinger Lab
- **Languages**: Python, Java
- **Protocol**: UDP
- **Description**: Ping client using UDP sockets with packet loss simulation
- **Location**: `src/[language]/udp_pinger/`

### 4. SMTP Client
- **Languages**: Python, Java
- **Protocol**: SMTP over TCP
- **Description**: Email client implementation using SMTP protocol
- **Location**: `src/[language]/smtp_client/`

### 5. Professional Video Streaming System 🎬
- **Language**: Python
- **Protocols**: RTSP/RTP
- **Description**: Complete video streaming solution with GUI client and RTSP/RTP server
- **Features**:
  - RTSP control protocol implementation
  - RTP real-time video streaming
  - GUI client with playback controls
  - Multiple quality profiles (480p-4K)
  - Video library management
  - Cross-platform media player integration
- **Location**: `src/video_streaming/`
- **Quick Start**:
  ```bash
  # Start server
  cd src/video_streaming/server
  python video_server.py
  
  # Launch client (in new terminal)
  cd src/video_streaming/client
  python video_client.py
  ```

### 6. HTTP Web Proxy Server
- **Languages**: Python, Java
- **Protocol**: HTTP over TCP
- **Description**: Proxy server implementation with caching capabilities
- **Location**: `src/[language]/web_proxy/`

## Testing

### Quick Testing Options

**🚀 Automated Test Runner (Recommended)**
```bash
# Windows
run_tests.bat

# Linux/Mac  
chmod +x run_tests.sh
./run_tests.sh
```

**⚡ Quick Validation**
```bash
# Check if everything is working
python validate_project.py

# Quick health check only
python validate_project.py --quick
```

**📋 Component-Specific Testing**
```bash
# Test UDP streaming assignment
cd assignments/udp_streaming
python quick_test.py

# Test video streaming system
cd src/video_streaming
python run_project_tests.py

# Start complete video streaming system
cd src/video_streaming  
python start_streaming.py all
```

### Test Categories
- **Project Structure**: Verify all files and directories exist
- **Dependencies**: Check Python version and required modules  
- **Network Connectivity**: Test socket creation and port binding
- **Assignment Functionality**: UDP streaming with 1000-2000 byte chunks
- **Video Streaming System**: RTSP/RTP protocols, GUI client, server functionality
- **Integration**: End-to-end client-server communication
- **Performance**: Streaming throughput and latency benchmarks

📖 **Detailed Testing Guide**: See [TESTING.md](TESTING.md) for comprehensive testing instructions.

### Legacy Unit Tests
```bash
# Run Python tests
python -m pytest tests/unit_tests/

# Run Java tests
cd tests/java/
javac -cp .:junit-4.12.jar *.java
java -cp .:junit-4.12.jar org.junit.runner.JUnitCore TestSuite
```

### Integration Tests
```bash
# Run integration test suite
cd tests/integration_tests/
python test_client_server_integration.py
```

### Performance Testing
```bash
# Run performance benchmarks
cd tests/performance_tests/
python benchmark_throughput.py
python benchmark_latency.py
```

## Implementation Details

### Socket Programming Concepts Demonstrated:

1. **TCP Sockets**:
   - Reliable connection-oriented communication
   - Error detection and correction
   - Flow control mechanisms

2. **UDP Sockets**:
   - Connectionless communication
   - Low-latency applications
   - Packet loss handling

3. **Protocol Design**:
   - Custom message formats
   - State management
   - Error handling strategies

4. **Concurrency**:
   - Multi-threaded servers
   - Asynchronous I/O
   - Connection pooling

### Error Handling:
- Connection timeouts
- Network unreachability
- Malformed packets
- Resource exhaustion

## Learning Objectives

After completing these assignments, students will understand:

- Socket API and system calls
- Network protocol implementation
- Client-server architecture patterns
- Error handling in distributed systems
- Performance considerations in network programming
- Security implications of network applications

## Troubleshooting

### Common Issues:

1. **Port Already in Use**:
   ```bash
   # Find process using the port
   netstat -ano | findstr :12000
   # Kill the process
   taskkill /PID [process_id] /F
   ```

2. **Firewall Blocking Connections**:
   - Add exception for your application
   - Check Windows Defender Firewall settings

3. **Permission Denied (Ports < 1024)**:
   - Use ports above 1024 for testing
   - Run as administrator if necessary

4. **Module Import Errors**:
   ```bash
   # Ensure virtual environment is activated
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Commit your changes (`git commit -am 'Add new protocol implementation'`)
4. Push to the branch (`git push origin feature/new-protocol`)
5. Create a Pull Request

### Contribution Guidelines:
- Follow existing code style and conventions
- Add comprehensive documentation
- Include unit tests for new features
- Update README.md if adding new programs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Academic Use Notice:
These programming assignments are adapted from materials by J.F. Kurose and K.W. Ross. 
Original assignments copyright 1993-2025, J.F. Kurose, K.W. Ross, All Rights Reserved.

## Contact

**Project Maintainer**: [Your Name]
- GitHub: [@pronad1](https://github.com/pronad1)
- Email: [prosenjit1156@gmail.com]

**Course Information**:
- Course: Computer Networks / Socket Programming
- Institution: [Patuakhali Science & Technology University]
- Semester: [5th]

**Resources**:
- [Official Course Website](https://gaia.cs.umass.edu/kurose_ross/programming.php)
- [Textbook: Computer Networking: A Top-Down Approach](https://www.pearson.com/us/higher-education/program/Kurose-Computer-Networking-A-Top-Down-Approach-8th-Edition/PGM2877610.html)

---

**Note**: This project is for educational purposes. Please ensure you understand your institution's academic integrity policies regarding programming assignments.
