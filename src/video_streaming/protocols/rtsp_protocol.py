#!/usr/bin/env python3
"""
RTSP Protocol Implementation
Real Time Streaming Protocol utilities and handlers

This module provides:
- RTSP message parsing and creation
- RTSP method handlers (DESCRIBE, SETUP, PLAY, PAUSE, TEARDOWN)
- RTSP response generation
- Session management
- Transport parameter handling

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RTSPMethod(Enum):
    """RTSP method types"""
    DESCRIBE = "DESCRIBE"
    SETUP = "SETUP"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    TEARDOWN = "TEARDOWN"
    GET_PARAMETER = "GET_PARAMETER"
    SET_PARAMETER = "SET_PARAMETER"
    OPTIONS = "OPTIONS"
    ANNOUNCE = "ANNOUNCE"
    RECORD = "RECORD"
    REDIRECT = "REDIRECT"
    GET_VIDEOS = "GET_VIDEOS"  # Custom method for video library


class RTSPStatus(Enum):
    """RTSP status codes"""
    OK = (200, "OK")
    CREATED = (201, "Created")
    LOW_ON_STORAGE = (250, "Low on Storage Space")
    MULTIPLE_CHOICES = (300, "Multiple Choices")
    MOVED_PERMANENTLY = (301, "Moved Permanently")
    MOVED_TEMPORARILY = (302, "Moved Temporarily")
    SEE_OTHER = (303, "See Other")
    NOT_MODIFIED = (304, "Not Modified")
    USE_PROXY = (305, "Use Proxy")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    PAYMENT_REQUIRED = (402, "Payment Required")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    METHOD_NOT_ALLOWED = (405, "Method Not Allowed")
    NOT_ACCEPTABLE = (406, "Not Acceptable")
    PROXY_AUTH_REQUIRED = (407, "Proxy Authentication Required")
    REQUEST_TIMEOUT = (408, "Request Time-out")
    GONE = (410, "Gone")
    LENGTH_REQUIRED = (411, "Length Required")
    PRECONDITION_FAILED = (412, "Precondition Failed")
    REQUEST_ENTITY_TOO_LARGE = (413, "Request Entity Too Large")
    REQUEST_URI_TOO_LARGE = (414, "Request-URI Too Large")
    UNSUPPORTED_MEDIA_TYPE = (415, "Unsupported Media Type")
    PARAMETER_NOT_UNDERSTOOD = (451, "Parameter Not Understood")
    CONFERENCE_NOT_FOUND = (452, "Conference Not Found")
    NOT_ENOUGH_BANDWIDTH = (453, "Not Enough Bandwidth")
    SESSION_NOT_FOUND = (454, "Session Not Found")
    METHOD_NOT_VALID = (455, "Method Not Valid in This State")
    HEADER_FIELD_NOT_VALID = (456, "Header Field Not Valid for Resource")
    INVALID_RANGE = (457, "Invalid Range")
    PARAMETER_IS_READONLY = (458, "Parameter Is Read-Only")
    AGGREGATE_OP_NOT_ALLOWED = (459, "Aggregate operation not allowed")
    ONLY_AGGREGATE_OP_ALLOWED = (460, "Only aggregate operation allowed")
    UNSUPPORTED_TRANSPORT = (461, "Unsupported transport")
    DESTINATION_UNREACHABLE = (462, "Destination unreachable")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    NOT_IMPLEMENTED = (501, "Not Implemented")
    BAD_GATEWAY = (502, "Bad Gateway")
    SERVICE_UNAVAILABLE = (503, "Service Unavailable")
    GATEWAY_TIMEOUT = (504, "Gateway Time-out")
    RTSP_VERSION_NOT_SUPPORTED = (505, "RTSP Version not supported")
    OPTION_NOT_SUPPORTED = (551, "Option not supported")


@dataclass
class RTSPRequest:
    """RTSP request message"""
    method: RTSPMethod
    uri: str
    version: str = "RTSP/1.0"
    headers: Dict[str, str] = None
    body: str = ""
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class RTSPResponse:
    """RTSP response message"""
    version: str = "RTSP/1.0"
    status_code: int = 200
    status_text: str = "OK"
    headers: Dict[str, str] = None
    body: str = ""
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class TransportParams:
    """RTP transport parameters"""
    protocol: str = "RTP/UDP"
    cast_type: str = "unicast"
    client_port: Tuple[int, int] = None
    server_port: Tuple[int, int] = None
    ttl: int = None
    destination: str = None
    source: str = None
    mode: str = None
    ssrc: str = None


class RTSPParser:
    """RTSP message parser"""
    
    @staticmethod
    def parse_request(data: str) -> RTSPRequest:
        """Parse RTSP request from string"""
        lines = data.strip().split('\\n')
        if not lines:
            raise ValueError("Empty RTSP request")
        
        # Parse request line
        request_line = lines[0].strip()
        parts = request_line.split()
        if len(parts) != 3:
            raise ValueError(f"Invalid request line: {request_line}")
        
        method_str, uri, version = parts
        try:
            method = RTSPMethod(method_str)
        except ValueError:
            raise ValueError(f"Unknown RTSP method: {method_str}")
        
        # Parse headers
        headers = {}
        body_start = len(lines)
        
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                body_start = i + 1
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Parse body
        body = '\\n'.join(lines[body_start:]) if body_start < len(lines) else ""
        
        return RTSPRequest(method, uri, version, headers, body)
    
    @staticmethod
    def parse_response(data: str) -> RTSPResponse:
        """Parse RTSP response from string"""
        lines = data.strip().split('\\n')
        if not lines:
            raise ValueError("Empty RTSP response")
        
        # Parse status line
        status_line = lines[0].strip()
        parts = status_line.split(None, 2)
        if len(parts) < 2:
            raise ValueError(f"Invalid status line: {status_line}")
        
        version = parts[0]
        status_code = int(parts[1])
        status_text = parts[2] if len(parts) > 2 else ""
        
        # Parse headers
        headers = {}
        body_start = len(lines)
        
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                body_start = i + 1
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Parse body
        body = '\\n'.join(lines[body_start:]) if body_start < len(lines) else ""
        
        return RTSPResponse(version, status_code, status_text, headers, body)
    
    @staticmethod
    def parse_transport(transport_header: str) -> TransportParams:
        """Parse Transport header"""
        params = TransportParams()
        
        # Split by semicolons
        parts = transport_header.split(';')
        
        # First part is the protocol
        if parts:
            protocol_part = parts[0].strip()
            if '/' in protocol_part:
                params.protocol, params.cast_type = protocol_part.split('/', 1)
            else:
                params.protocol = protocol_part
        
        # Parse remaining parameters
        for part in parts[1:]:
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "client_port":
                    if '-' in value:
                        port1, port2 = map(int, value.split('-'))
                        params.client_port = (port1, port2)
                    else:
                        port = int(value)
                        params.client_port = (port, port + 1)
                
                elif key == "server_port":
                    if '-' in value:
                        port1, port2 = map(int, value.split('-'))
                        params.server_port = (port1, port2)
                    else:
                        port = int(value)
                        params.server_port = (port, port + 1)
                
                elif key == "ttl":
                    params.ttl = int(value)
                
                elif key == "destination":
                    params.destination = value
                
                elif key == "source":
                    params.source = value
                
                elif key == "mode":
                    params.mode = value
                
                elif key == "ssrc":
                    params.ssrc = value
            
            else:
                # Boolean parameters
                if part == "unicast":
                    params.cast_type = "unicast"
                elif part == "multicast":
                    params.cast_type = "multicast"
        
        return params


class RTSPFormatter:
    """RTSP message formatter"""
    
    @staticmethod
    def format_request(request: RTSPRequest) -> str:
        """Format RTSP request to string"""
        lines = []
        
        # Request line
        lines.append(f"{request.method.value} {request.uri} {request.version}")
        
        # Headers
        for key, value in request.headers.items():
            lines.append(f"{key}: {value}")
        
        # Empty line before body
        lines.append("")
        
        # Body
        if request.body:
            lines.append(request.body)
        
        return '\\n'.join(lines)
    
    @staticmethod
    def format_response(response: RTSPResponse) -> str:
        """Format RTSP response to string"""
        lines = []
        
        # Status line
        lines.append(f"{response.version} {response.status_code} {response.status_text}")
        
        # Headers
        for key, value in response.headers.items():
            lines.append(f"{key}: {value}")
        
        # Empty line before body
        lines.append("")
        
        # Body
        if response.body:
            lines.append(response.body)
        
        return '\\n'.join(lines)
    
    @staticmethod
    def format_transport(params: TransportParams) -> str:
        """Format transport parameters"""
        parts = []
        
        # Protocol
        if params.cast_type:
            parts.append(f"{params.protocol}/{params.cast_type}")
        else:
            parts.append(params.protocol)
        
        # Client port
        if params.client_port:
            if params.client_port[0] == params.client_port[1]:
                parts.append(f"client_port={params.client_port[0]}")
            else:
                parts.append(f"client_port={params.client_port[0]}-{params.client_port[1]}")
        
        # Server port
        if params.server_port:
            if params.server_port[0] == params.server_port[1]:
                parts.append(f"server_port={params.server_port[0]}")
            else:
                parts.append(f"server_port={params.server_port[0]}-{params.server_port[1]}")
        
        # Other parameters
        if params.ttl is not None:
            parts.append(f"ttl={params.ttl}")
        
        if params.destination:
            parts.append(f"destination={params.destination}")
        
        if params.source:
            parts.append(f"source={params.source}")
        
        if params.mode:
            parts.append(f"mode={params.mode}")
        
        if params.ssrc:
            parts.append(f"ssrc={params.ssrc}")
        
        return ';'.join(parts)


class RTSPSession:
    """RTSP session management"""
    
    def __init__(self, session_id: str, client_address: Tuple[str, int]):
        self.session_id = session_id
        self.client_address = client_address
        self.state = "INIT"
        self.cseq = 0
        self.video_uri = None
        self.transport_params = None
        self.created_time = time.time()
        self.last_activity = time.time()
        
        # Session states: INIT -> READY -> PLAYING -> READY -> INIT
        self.valid_transitions = {
            "INIT": ["READY"],
            "READY": ["PLAYING", "INIT"],
            "PLAYING": ["READY"]
        }
    
    def can_transition_to(self, new_state: str) -> bool:
        """Check if state transition is valid"""
        return new_state in self.valid_transitions.get(self.state, [])
    
    def transition_to(self, new_state: str) -> bool:
        """Transition to new state"""
        if self.can_transition_to(new_state):
            self.state = new_state
            self.last_activity = time.time()
            return True
        return False
    
    def update_activity(self):
        """Update last activity time"""
        self.last_activity = time.time()
    
    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if session is expired"""
        return time.time() - self.last_activity > timeout_seconds


class RTSPHandler:
    """RTSP request handler"""
    
    def __init__(self):
        self.sessions: Dict[str, RTSPSession] = {}
        self.session_counter = 0
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        self.session_counter += 1
        return f"SESSION_{int(time.time())}_{self.session_counter}"
    
    def create_session(self, client_address: Tuple[str, int]) -> RTSPSession:
        """Create new RTSP session"""
        session_id = self.generate_session_id()
        session = RTSPSession(session_id, client_address)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[RTSPSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """Remove session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self, timeout_seconds: int = 300):
        """Remove expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired(timeout_seconds)
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def handle_options(self, request: RTSPRequest) -> RTSPResponse:
        """Handle OPTIONS request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        response.headers["Public"] = "DESCRIBE, SETUP, TEARDOWN, PLAY, PAUSE, GET_VIDEOS"
        response.headers["Server"] = "Professional Video Streaming Server/1.0"
        return response
    
    def handle_describe(self, request: RTSPRequest, video_info: Dict) -> RTSPResponse:
        """Handle DESCRIBE request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        response.headers["Content-Type"] = "application/sdp"
        
        # Generate SDP content
        sdp_content = self.generate_sdp(video_info)
        response.body = sdp_content
        response.headers["Content-Length"] = str(len(response.body))
        
        return response
    
    def handle_setup(self, request: RTSPRequest, client_address: Tuple[str, int]) -> RTSPResponse:
        """Handle SETUP request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        
        # Parse transport header
        transport_header = request.headers.get("Transport", "")
        if not transport_header:
            response.status_code = RTSPStatus.BAD_REQUEST.value[0]
            response.status_text = RTSPStatus.BAD_REQUEST.value[1]
            return response
        
        try:
            transport_params = RTSPParser.parse_transport(transport_header)
            
            # Create session
            session = self.create_session(client_address)
            session.video_uri = request.uri
            session.transport_params = transport_params
            session.transition_to("READY")
            
            # Set server port (use client port + 1000 for server)
            if transport_params.client_port:
                server_port = (transport_params.client_port[0] + 1000, 
                             transport_params.client_port[1] + 1000)
                transport_params.server_port = server_port
            
            # Format transport response
            transport_response = RTSPFormatter.format_transport(transport_params)
            response.headers["Transport"] = transport_response
            response.headers["Session"] = session.session_id
            
        except Exception as e:
            response.status_code = RTSPStatus.UNSUPPORTED_TRANSPORT.value[0]
            response.status_text = RTSPStatus.UNSUPPORTED_TRANSPORT.value[1]
        
        return response
    
    def handle_play(self, request: RTSPRequest) -> RTSPResponse:
        """Handle PLAY request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        
        session_id = request.headers.get("Session", "")
        session = self.get_session(session_id)
        
        if not session:
            response.status_code = RTSPStatus.SESSION_NOT_FOUND.value[0]
            response.status_text = RTSPStatus.SESSION_NOT_FOUND.value[1]
            return response
        
        if not session.can_transition_to("PLAYING"):
            response.status_code = RTSPStatus.METHOD_NOT_VALID.value[0]
            response.status_text = RTSPStatus.METHOD_NOT_VALID.value[1]
            return response
        
        session.transition_to("PLAYING")
        response.headers["Session"] = session_id
        response.headers["RTP-Info"] = f"url={request.uri};seq=1;rtptime=0"
        
        return response
    
    def handle_pause(self, request: RTSPRequest) -> RTSPResponse:
        """Handle PAUSE request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        
        session_id = request.headers.get("Session", "")
        session = self.get_session(session_id)
        
        if not session:
            response.status_code = RTSPStatus.SESSION_NOT_FOUND.value[0]
            response.status_text = RTSPStatus.SESSION_NOT_FOUND.value[1]
            return response
        
        if not session.can_transition_to("READY"):
            response.status_code = RTSPStatus.METHOD_NOT_VALID.value[0]
            response.status_text = RTSPStatus.METHOD_NOT_VALID.value[1]
            return response
        
        session.transition_to("READY")
        response.headers["Session"] = session_id
        
        return response
    
    def handle_teardown(self, request: RTSPRequest) -> RTSPResponse:
        """Handle TEARDOWN request"""
        response = RTSPResponse()
        response.headers["CSeq"] = request.headers.get("CSeq", "0")
        
        session_id = request.headers.get("Session", "")
        session = self.get_session(session_id)
        
        if session:
            session.transition_to("INIT")
            self.remove_session(session_id)
        
        response.headers["Session"] = session_id
        return response
    
    def generate_sdp(self, video_info: Dict) -> str:
        """Generate SDP (Session Description Protocol) content"""
        sdp_lines = [
            "v=0",  # Version
            f"o=- {int(time.time())} {int(time.time())} IN IP4 127.0.0.1",  # Origin
            "s=Video Stream",  # Session name
            "c=IN IP4 0.0.0.0",  # Connection info
            "t=0 0",  # Time
            "m=video 0 RTP/AVP 96",  # Media description
            "a=rtpmap:96 H264/90000",  # RTP map
            f"a=fmtp:96 profile-level-id=428014; config={video_info.get('config', '')}"  # Format parameters
        ]
        
        return '\\n'.join(sdp_lines)


# Utility functions
def create_rtsp_response(status: RTSPStatus, cseq: str = "0", 
                        headers: Dict[str, str] = None, body: str = "") -> RTSPResponse:
    """Create standard RTSP response"""
    response = RTSPResponse()
    response.status_code = status.value[0]
    response.status_text = status.value[1]
    response.headers["CSeq"] = cseq
    response.headers["Server"] = "Professional Video Streaming Server/1.0"
    response.headers["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    
    if headers:
        response.headers.update(headers)
    
    if body:
        response.body = body
        response.headers["Content-Length"] = str(len(body))
    
    return response


def validate_rtsp_version(version: str) -> bool:
    """Validate RTSP version"""
    return version == "RTSP/1.0"


def extract_video_name_from_uri(uri: str) -> Optional[str]:
    """Extract video name from RTSP URI"""
    # Expected format: rtsp://server/video_name or rtsp://server:port/video_name
    if uri.startswith("rtsp://"):
        # Remove rtsp://
        uri = uri[7:]
        
        # Find first slash after server
        slash_index = uri.find('/')
        if slash_index != -1:
            return uri[slash_index + 1:]
    
    return None


if __name__ == "__main__":
    # Example usage
    print("🔧 RTSP Protocol Implementation")
    print("   📡 Real Time Streaming Protocol utilities")
    
    # Test parser
    test_request = """DESCRIBE rtsp://server/video.mp4 RTSP/1.0
CSeq: 1
User-Agent: Professional Video Client

"""
    
    request = RTSPParser.parse_request(test_request)
    print(f"   ✅ Parsed method: {request.method}")
    print(f"   ✅ Parsed URI: {request.uri}")
    
    # Test formatter
    response = RTSPResponse()
    response.headers["CSeq"] = "1"
    response.headers["Content-Type"] = "application/sdp"
    response.body = "v=0\\no=- 123456 123456 IN IP4 127.0.0.1"
    
    formatted = RTSPFormatter.format_response(response)
    print(f"   ✅ Formatted response: {len(formatted)} bytes")