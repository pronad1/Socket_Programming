#!/usr/bin/env python3
"""
RTP Protocol Implementation
Real-time Transport Protocol for video streaming

This module provides:
- RTP packet creation and parsing
- RTP header management
- Payload type handling
- Sequence number tracking
- Timestamp management
- SSRC (Synchronization Source) handling

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import struct
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RTPPayloadType(Enum):
    """RTP payload types for different media formats"""
    PCMU = 0        # G.711 μ-law
    RESERVED_1 = 1
    RESERVED_2 = 2
    GSM = 3         # GSM
    G723 = 4        # G.723.1
    DVI4_8000 = 5   # DVI4 8000 Hz
    DVI4_16000 = 6  # DVI4 16000 Hz
    LPC = 7         # LPC
    PCMA = 8        # G.711 A-law
    G722 = 9        # G.722
    L16_2CH = 10    # Linear 16-bit stereo
    L16_1CH = 11    # Linear 16-bit mono
    QCELP = 12      # QCELP
    CN = 13         # Comfort noise
    MPA = 14        # MPEG Audio
    G728 = 15       # G.728
    DVI4_11025 = 16 # DVI4 11025 Hz
    DVI4_22050 = 17 # DVI4 22050 Hz
    G729 = 18       # G.729
    
    # Video payload types (dynamic)
    H264 = 96       # H.264 video
    H265 = 97       # H.265/HEVC video
    VP8 = 98        # VP8 video
    VP9 = 99        # VP9 video
    AV1 = 100       # AV1 video


@dataclass
class RTPHeader:
    """RTP packet header structure"""
    version: int = 2            # RTP version (2)
    padding: bool = False       # Padding flag
    extension: bool = False     # Extension flag
    cc: int = 0                # CSRC count
    marker: bool = False        # Marker bit
    payload_type: int = 96      # Payload type (96 for H.264)
    sequence_number: int = 0    # Sequence number
    timestamp: int = 0          # Timestamp
    ssrc: int = 0              # Synchronization source identifier
    csrc: List[int] = None     # Contributing source identifiers
    
    def __post_init__(self):
        if self.csrc is None:
            self.csrc = []


@dataclass
class RTPPacket:
    """Complete RTP packet"""
    header: RTPHeader
    payload: bytes
    
    def to_bytes(self) -> bytes:
        """Convert RTP packet to bytes"""
        return RTPPacketBuilder.build_packet(self.header, self.payload)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'RTPPacket':
        """Create RTP packet from bytes"""
        header, payload = RTPPacketParser.parse_packet(data)
        return cls(header, payload)


class RTPPacketBuilder:
    """RTP packet construction utilities"""
    
    @staticmethod
    def build_packet(header: RTPHeader, payload: bytes) -> bytes:
        """Build RTP packet from header and payload"""
        # Build fixed header (12 bytes)
        byte1 = (header.version << 6) | (int(header.padding) << 5) | \
                (int(header.extension) << 4) | (header.cc & 0x0F)
        
        byte2 = (int(header.marker) << 7) | (header.payload_type & 0x7F)
        
        packet_data = struct.pack('!BBHII',
                                 byte1,
                                 byte2,
                                 header.sequence_number & 0xFFFF,
                                 header.timestamp & 0xFFFFFFFF,
                                 header.ssrc & 0xFFFFFFFF)
        
        # Add CSRC identifiers if any
        for csrc in header.csrc:
            packet_data += struct.pack('!I', csrc & 0xFFFFFFFF)
        
        # Add payload
        packet_data += payload
        
        return packet_data
    
    @staticmethod
    def build_header(version: int = 2, padding: bool = False, extension: bool = False,
                    cc: int = 0, marker: bool = False, payload_type: int = 96,
                    sequence_number: int = 0, timestamp: int = 0, ssrc: int = 0,
                    csrc: List[int] = None) -> RTPHeader:
        """Build RTP header with specified parameters"""
        return RTPHeader(
            version=version,
            padding=padding,
            extension=extension,
            cc=cc,
            marker=marker,
            payload_type=payload_type,
            sequence_number=sequence_number,
            timestamp=timestamp,
            ssrc=ssrc,
            csrc=csrc or []
        )


class RTPPacketParser:
    """RTP packet parsing utilities"""
    
    @staticmethod
    def parse_packet(data: bytes) -> Tuple[RTPHeader, bytes]:
        """Parse RTP packet from bytes"""
        if len(data) < 12:
            raise ValueError("RTP packet too short (minimum 12 bytes required)")
        
        # Parse fixed header
        byte1, byte2, seq_num, timestamp, ssrc = struct.unpack('!BBHII', data[:12])
        
        # Extract header fields
        version = (byte1 >> 6) & 0x03
        padding = bool((byte1 >> 5) & 0x01)
        extension = bool((byte1 >> 4) & 0x01)
        cc = byte1 & 0x0F
        
        marker = bool((byte2 >> 7) & 0x01)
        payload_type = byte2 & 0x7F
        
        # Parse CSRC identifiers
        csrc = []
        csrc_offset = 12
        for i in range(cc):
            if csrc_offset + 4 > len(data):
                raise ValueError("Invalid CSRC count in RTP header")
            
            csrc_id = struct.unpack('!I', data[csrc_offset:csrc_offset + 4])[0]
            csrc.append(csrc_id)
            csrc_offset += 4
        
        # Create header
        header = RTPHeader(
            version=version,
            padding=padding,
            extension=extension,
            cc=cc,
            marker=marker,
            payload_type=payload_type,
            sequence_number=seq_num,
            timestamp=timestamp,
            ssrc=ssrc,
            csrc=csrc
        )
        
        # Extract payload
        payload = data[csrc_offset:]
        
        # Handle padding if present
        if padding and len(payload) > 0:
            padding_count = payload[-1]
            if padding_count <= len(payload):
                payload = payload[:-padding_count]
        
        return header, payload
    
    @staticmethod
    def validate_header(header: RTPHeader) -> bool:
        """Validate RTP header fields"""
        if header.version != 2:
            return False
        
        if header.cc > 15:
            return False
        
        if header.payload_type > 127:
            return False
        
        if len(header.csrc) != header.cc:
            return False
        
        return True


class RTPSession:
    """RTP session management"""
    
    def __init__(self, ssrc: int = None, payload_type: int = 96):
        """
        Initialize RTP session
        
        Args:
            ssrc: Synchronization source identifier
            payload_type: RTP payload type
        """
        self.ssrc = ssrc or random.randint(1, 0xFFFFFFFF)
        self.payload_type = payload_type
        self.sequence_number = random.randint(1, 0xFFFF)
        self.timestamp_base = random.randint(1, 0xFFFFFFFF)
        self.timestamp_offset = 0
        self.clock_rate = 90000  # Default clock rate for video (90 kHz)
        
        # Session statistics
        self.packets_sent = 0
        self.bytes_sent = 0
        self.start_time = time.time()
        
    def get_next_sequence_number(self) -> int:
        """Get next sequence number"""
        seq_num = self.sequence_number
        self.sequence_number = (self.sequence_number + 1) & 0xFFFF
        return seq_num
    
    def get_timestamp(self, time_offset: float = None) -> int:
        """Get RTP timestamp for current time or specified offset"""
        if time_offset is None:
            time_offset = time.time() - self.start_time
        
        # Convert time to RTP timestamp units
        timestamp_units = int(time_offset * self.clock_rate)
        return (self.timestamp_base + timestamp_units) & 0xFFFFFFFF
    
    def create_packet(self, payload: bytes, marker: bool = False, 
                     timestamp: int = None) -> RTPPacket:
        """Create RTP packet with session parameters"""
        if timestamp is None:
            timestamp = self.get_timestamp()
        
        header = RTPHeader(
            version=2,
            padding=False,
            extension=False,
            cc=0,
            marker=marker,
            payload_type=self.payload_type,
            sequence_number=self.get_next_sequence_number(),
            timestamp=timestamp,
            ssrc=self.ssrc
        )
        
        packet = RTPPacket(header, payload)
        
        # Update statistics
        self.packets_sent += 1
        self.bytes_sent += len(payload)
        
        return packet
    
    def get_statistics(self) -> Dict:
        """Get session statistics"""
        elapsed_time = time.time() - self.start_time
        
        return {
            'packets_sent': self.packets_sent,
            'bytes_sent': self.bytes_sent,
            'elapsed_time': elapsed_time,
            'packet_rate': self.packets_sent / elapsed_time if elapsed_time > 0 else 0,
            'bitrate': (self.bytes_sent * 8) / elapsed_time if elapsed_time > 0 else 0,
            'ssrc': self.ssrc,
            'current_sequence': self.sequence_number,
            'current_timestamp': self.get_timestamp()
        }


class RTPReceiver:
    """RTP packet receiver with jitter buffer"""
    
    def __init__(self, buffer_size: int = 50):
        """
        Initialize RTP receiver
        
        Args:
            buffer_size: Size of jitter buffer
        """
        self.buffer_size = buffer_size
        self.buffer: Dict[int, RTPPacket] = {}
        self.expected_sequence = None
        self.highest_sequence = None
        
        # Statistics
        self.packets_received = 0
        self.packets_lost = 0
        self.bytes_received = 0
        self.duplicate_packets = 0
        self.out_of_order_packets = 0
        
    def receive_packet(self, packet: RTPPacket) -> Optional[List[RTPPacket]]:
        """
        Receive RTP packet and return ready packets from buffer
        
        Returns:
            List of packets ready for playback (in sequence order)
        """
        seq_num = packet.header.sequence_number
        
        # Check for duplicate
        if seq_num in self.buffer:
            self.duplicate_packets += 1
            return []
        
        # Initialize expected sequence if first packet
        if self.expected_sequence is None:
            self.expected_sequence = seq_num
        
        # Update highest sequence seen
        if self.highest_sequence is None or self._sequence_greater(seq_num, self.highest_sequence):
            self.highest_sequence = seq_num
        
        # Check if packet is out of order
        if not self._sequence_greater_equal(seq_num, self.expected_sequence):
            self.out_of_order_packets += 1
        
        # Add packet to buffer
        self.buffer[seq_num] = packet
        self.packets_received += 1
        self.bytes_received += len(packet.payload)
        
        # Extract ready packets
        ready_packets = []
        while self.expected_sequence in self.buffer:
            ready_packets.append(self.buffer[self.expected_sequence])
            del self.buffer[self.expected_sequence]
            self.expected_sequence = (self.expected_sequence + 1) & 0xFFFF
        
        # Clean old packets from buffer
        self._clean_buffer()
        
        return ready_packets
    
    def _sequence_greater(self, seq1: int, seq2: int) -> bool:
        """Check if seq1 > seq2 considering wraparound"""
        return ((seq1 > seq2) and (seq1 - seq2 < 32768)) or \
               ((seq1 < seq2) and (seq2 - seq1 > 32768))
    
    def _sequence_greater_equal(self, seq1: int, seq2: int) -> bool:
        """Check if seq1 >= seq2 considering wraparound"""
        return seq1 == seq2 or self._sequence_greater(seq1, seq2)
    
    def _clean_buffer(self):
        """Remove old packets from buffer"""
        if len(self.buffer) > self.buffer_size:
            # Remove packets that are too old
            min_sequence = (self.expected_sequence - self.buffer_size // 2) & 0xFFFF
            
            to_remove = []
            for seq_num in self.buffer:
                if not self._sequence_greater_equal(seq_num, min_sequence):
                    to_remove.append(seq_num)
            
            for seq_num in to_remove:
                del self.buffer[seq_num]
                self.packets_lost += 1
    
    def get_statistics(self) -> Dict:
        """Get receiver statistics"""
        total_expected = 0
        if self.highest_sequence is not None and self.expected_sequence is not None:
            total_expected = (self.highest_sequence - self.expected_sequence + 1) & 0xFFFF
        
        loss_rate = 0
        if total_expected > 0:
            loss_rate = self.packets_lost / (self.packets_received + self.packets_lost)
        
        return {
            'packets_received': self.packets_received,
            'packets_lost': self.packets_lost,
            'bytes_received': self.bytes_received,
            'duplicate_packets': self.duplicate_packets,
            'out_of_order_packets': self.out_of_order_packets,
            'buffer_size': len(self.buffer),
            'loss_rate': loss_rate,
            'expected_sequence': self.expected_sequence,
            'highest_sequence': self.highest_sequence
        }


class RTPUtils:
    """RTP utility functions"""
    
    @staticmethod
    def generate_ssrc() -> int:
        """Generate random SSRC identifier"""
        return random.randint(1, 0xFFFFFFFF)
    
    @staticmethod
    def time_to_rtp_timestamp(time_seconds: float, clock_rate: int = 90000) -> int:
        """Convert time in seconds to RTP timestamp"""
        return int(time_seconds * clock_rate) & 0xFFFFFFFF
    
    @staticmethod
    def rtp_timestamp_to_time(timestamp: int, clock_rate: int = 90000) -> float:
        """Convert RTP timestamp to time in seconds"""
        return timestamp / clock_rate
    
    @staticmethod
    def calculate_jitter(timestamps: List[int], clock_rate: int = 90000) -> float:
        """Calculate jitter from timestamp sequence"""
        if len(timestamps) < 2:
            return 0.0
        
        # Calculate interarrival jitter (RFC 3550)
        jitter = 0.0
        for i in range(1, len(timestamps)):
            transit_time = timestamps[i] - timestamps[i-1]
            if i > 1:
                jitter += abs(transit_time - (timestamps[i-1] - timestamps[i-2])) / 16.0
        
        return jitter / clock_rate
    
    @staticmethod
    def format_payload_info(payload_type: int) -> str:
        """Format payload type information"""
        try:
            pt_enum = RTPPayloadType(payload_type)
            return f"{payload_type} ({pt_enum.name})"
        except ValueError:
            if payload_type < 96:
                return f"{payload_type} (Static)"
            else:
                return f"{payload_type} (Dynamic)"


# H.264 specific utilities
class H264RTPUtils:
    """H.264 specific RTP utilities"""
    
    @staticmethod
    def create_fu_a_packets(nalu: bytes, max_payload_size: int = 1400, 
                           session: RTPSession = None) -> List[RTPPacket]:
        """
        Create Fragmentation Unit Type A (FU-A) packets for H.264 NALU
        
        Args:
            nalu: H.264 NALU (including start code)
            max_payload_size: Maximum RTP payload size
            session: RTP session for packet creation
        
        Returns:
            List of RTP packets containing fragmented NALU
        """
        if not session:
            session = RTPSession(payload_type=RTPPayloadType.H264.value)
        
        # Remove start code if present
        if nalu.startswith(b'\\x00\\x00\\x00\\x01'):
            nalu = nalu[4:]
        elif nalu.startswith(b'\\x00\\x00\\x01'):
            nalu = nalu[3:]
        
        if len(nalu) == 0:
            return []
        
        # Extract NALU header
        nalu_header = nalu[0]
        nalu_payload = nalu[1:]
        
        # If NALU fits in single packet, send as single NALU unit
        if len(nalu) <= max_payload_size:
            packet = session.create_packet(nalu, marker=True)
            return [packet]
        
        # Fragment NALU using FU-A
        packets = []
        f_bit = (nalu_header >> 7) & 0x01
        nri = (nalu_header >> 5) & 0x03
        nalu_type = nalu_header & 0x1F
        
        # FU indicator: F=f_bit, NRI=nri, Type=28 (FU-A)
        fu_indicator = (f_bit << 7) | (nri << 5) | 28
        
        offset = 0
        fragment_number = 0
        
        while offset < len(nalu_payload):
            # Calculate fragment size
            remaining = len(nalu_payload) - offset
            fragment_size = min(max_payload_size - 2, remaining)  # -2 for FU headers
            
            # FU header: S=start, E=end, R=0, Type=nalu_type
            is_start = (fragment_number == 0)
            is_end = (offset + fragment_size >= len(nalu_payload))
            
            fu_header = (int(is_start) << 7) | (int(is_end) << 6) | nalu_type
            
            # Create payload: FU indicator + FU header + fragment
            payload = bytes([fu_indicator, fu_header]) + nalu_payload[offset:offset + fragment_size]
            
            # Create RTP packet
            packet = session.create_packet(payload, marker=is_end)
            packets.append(packet)
            
            offset += fragment_size
            fragment_number += 1
        
        return packets


if __name__ == "__main__":
    # Example usage
    print("📡 RTP Protocol Implementation")
    print("   🎬 Real-time Transport Protocol for video streaming")
    
    # Create RTP session
    session = RTPSession(payload_type=RTPPayloadType.H264.value)
    print(f"   ✅ Created session with SSRC: {session.ssrc}")
    
    # Create test packet
    test_payload = b"\\x00\\x00\\x00\\x01\\x67\\x42\\x00\\x1e"  # Sample H.264 data
    packet = session.create_packet(test_payload, marker=True)
    
    print(f"   ✅ Created packet: seq={packet.header.sequence_number}, "
          f"ts={packet.header.timestamp}, payload={len(packet.payload)} bytes")
    
    # Test packet serialization
    packet_bytes = packet.to_bytes()
    print(f"   ✅ Serialized packet: {len(packet_bytes)} bytes")
    
    # Test packet parsing
    parsed_packet = RTPPacket.from_bytes(packet_bytes)
    print(f"   ✅ Parsed packet: seq={parsed_packet.header.sequence_number}, "
          f"payload={len(parsed_packet.payload)} bytes")
    
    # Test receiver
    receiver = RTPReceiver()
    ready_packets = receiver.receive_packet(packet)
    print(f"   ✅ Receiver processed packet: {len(ready_packets)} ready")
    
    stats = session.get_statistics()
    print(f"   📊 Session stats: {stats['packets_sent']} packets sent, "
          f"{stats['bytes_sent']} bytes")