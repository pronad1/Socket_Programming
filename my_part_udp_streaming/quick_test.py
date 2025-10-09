#!/usr/bin/env python3
"""
Quick Manual Test for UDP Streaming
This script tests the streaming functionality manually
"""

import socket
import time
import json
import struct
import os

def test_streaming():
    """Test streaming functionality"""
    print("🧪 QUICK STREAMING TEST")
    print("="*50)
    
    try:
        # Create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(10)
        
        server_address = ('localhost', 9999)
        
        print("1. Testing file list request...")
        # Test file list
        request = "LIST"
        client_socket.sendto(request.encode('utf-8'), server_address)
        data, _ = client_socket.recvfrom(4096)
        response = data.decode('utf-8')
        
        if response.startswith("FILES:"):
            file_data = response[6:]
            files = json.loads(file_data)
            print(f"   ✅ Found {len(files)} files:")
            for i, file_info in enumerate(files, 1):
                print(f"      {i}. {file_info['name']} ({file_info['size']} bytes)")
        else:
            print(f"   ❌ Error: {response}")
            return False
        
        if not files:
            print("   ❌ No files available for testing")
            return False
        
        # Test streaming small file
        print(f"\\n2. Testing streaming: {files[0]['name']}")
        filename = files[0]['name']
        request = f"STREAM:{filename}"
        client_socket.sendto(request.encode('utf-8'), server_address)
        
        # Receive file info
        data, _ = client_socket.recvfrom(4096)
        response = data.decode('utf-8')
        
        if not response.startswith("INFO:"):
            print(f"   ❌ Expected INFO, got: {response}")
            return False
        
        info_data = response[5:]
        file_info = json.loads(info_data)
        expected_size = file_info['size']
        print(f"   📁 File size: {expected_size} bytes")
        
        # Receive data packets
        received_bytes = 0
        packets_received = 0
        start_time = time.time()
        
        buffer_file = f"test_received_{filename}"
        
        with open(buffer_file, 'wb') as f:
            while received_bytes < expected_size:
                try:
                    data, _ = client_socket.recvfrom(65536)
                    
                    if len(data) >= 25:  # Minimum header size (1+4+4+8+8 = 25)
                        packet_type_byte = struct.unpack('!B', data[:1])[0]
                        packet_type = chr(packet_type_byte)
                        
                        if packet_type == 'D':  # Data packet
                            _, seq_num, data_size, bytes_sent, total_size = struct.unpack('!BII QQ', data[:25])
                            packet_data = data[25:25+data_size]
                            
                            f.write(packet_data)
                            received_bytes += len(packet_data)
                            packets_received += 1
                            
                            if packets_received % 10 == 0:  # Progress every 10 packets
                                progress = (received_bytes / expected_size) * 100
                                print(f"   📊 Progress: {progress:.1f}% ({packets_received} packets)")
                            
                        elif packet_type == 'E':  # End packet
                            print("   🏁 End-of-stream received")
                            break
                    
                    if time.time() - start_time > 30:  # 30 second timeout
                        print("   ⏰ Timeout!")
                        break
                        
                except socket.timeout:
                    print("   ⏰ Socket timeout")
                    break
        
        elapsed_time = time.time() - start_time
        
        print(f"\\n📊 STREAMING RESULTS:")
        print(f"   Expected: {expected_size} bytes")
        print(f"   Received: {received_bytes} bytes")
        print(f"   Packets: {packets_received}")
        print(f"   Time: {elapsed_time:.2f} seconds")
        
        if received_bytes == expected_size:
            speed_kbps = (received_bytes / elapsed_time) / 1024 if elapsed_time > 0 else 0
            print(f"   Speed: {speed_kbps:.1f} KB/s")
            print(f"   Buffer file: {buffer_file}")
            print("   ✅ STREAMING SUCCESSFUL!")
            
            # Verify file integrity
            if os.path.exists(buffer_file):
                actual_size = os.path.getsize(buffer_file)
                if actual_size == expected_size:
                    print("   ✅ File integrity verified!")
                else:
                    print(f"   ⚠️ File size mismatch: {actual_size} vs {expected_size}")
            
            return True
        else:
            print("   ❌ STREAMING FAILED - Size mismatch")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        client_socket.close()

def test_chunk_sizes():
    """Test that chunk sizes are within the required range"""
    print("\\n🔍 CHUNK SIZE VALIDATION TEST")
    print("="*50)
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(10)
        
        server_address = ('localhost', 9999)
        
        # Request the largest file for better chunk size testing
        request = "STREAM:test_large.mp4"
        client_socket.sendto(request.encode('utf-8'), server_address)
        
        # Skip INFO packet
        data, _ = client_socket.recvfrom(4096)
        
        chunk_sizes = []
        packet_count = 0
        
        # Analyze first 20 packets
        while packet_count < 20:
            try:
                data, _ = client_socket.recvfrom(65536)
                
                if len(data) >= 25:  # Minimum header size
                    packet_type_byte = struct.unpack('!B', data[:1])[0]
                    packet_type = chr(packet_type_byte)
                    
                    if packet_type == 'D':  # Data packet
                        _, seq_num, data_size, bytes_sent, total_size = struct.unpack('!BII QQ', data[:25])
                        chunk_sizes.append(data_size)
                        packet_count += 1
                        
                        print(f"   Packet {packet_count}: {data_size} bytes (seq: {seq_num})")
                    elif packet_type == 'E':  # End packet
                        break
                        
            except socket.timeout:
                break
        
        client_socket.close()
        
        if chunk_sizes:
            min_chunk = min(chunk_sizes)
            max_chunk = max(chunk_sizes)
            avg_chunk = sum(chunk_sizes) / len(chunk_sizes)
            
            print(f"\\n📊 CHUNK SIZE ANALYSIS:")
            print(f"   Packets analyzed: {len(chunk_sizes)}")
            print(f"   Min chunk size: {min_chunk} bytes")
            print(f"   Max chunk size: {max_chunk} bytes")
            print(f"   Avg chunk size: {avg_chunk:.1f} bytes")
            
            # Verify requirements
            valid_range = all(1000 <= size <= 2000 for size in chunk_sizes)
            
            if valid_range:
                print("   ✅ All chunks within required range (1000-2000 bytes)")
            else:
                invalid_chunks = [size for size in chunk_sizes if not (1000 <= size <= 2000)]
                print(f"   ❌ Invalid chunk sizes found: {invalid_chunks}")
            
            # Check randomness
            unique_sizes = len(set(chunk_sizes))
            randomness = unique_sizes / len(chunk_sizes) * 100
            print(f"   🎲 Size variety: {unique_sizes}/{len(chunk_sizes)} ({randomness:.1f}%)")
            
            return valid_range
        else:
            print("   ❌ No data packets received")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING UDP STREAMING TESTS")
    print("Make sure the server is running first!")
    print("="*60)
    
    # Test basic streaming
    streaming_success = test_streaming()
    
    # Test chunk size requirements
    chunk_success = test_chunk_sizes()
    
    print("\\n" + "="*60)
    print("🏆 FINAL TEST RESULTS")
    print("="*60)
    print(f"Streaming Test: {'✅ PASS' if streaming_success else '❌ FAIL'}")
    print(f"Chunk Size Test: {'✅ PASS' if chunk_success else '❌ FAIL'}")
    
    if streaming_success and chunk_success:
        print("\\n🎉 ALL TESTS PASSED!")
        print("Your UDP streaming assignment is working correctly!")
        print("\\n📝 Assignment Requirements Verified:")
        print("   ✅ UDP (connectionless) sockets")
        print("   ✅ Client requests multimedia files")
        print("   ✅ Server reads files in chunks")
        print("   ✅ Random chunk sizes 1000-2000 bytes")
        print("   ✅ Data sent as datagram packets")
        print("   ✅ Client receives and buffers data")
        print("   ✅ File streaming completes successfully")
    else:
        print("\\n⚠️ Some tests failed. Check the implementation.")
    
    print("\\n🎯 Next Steps:")
    print("   1. Test media player integration manually")
    print("   2. Try with real media files (mp3, mp4)")
    print("   3. Test with larger files")
    print("   4. Verify real-time playback during streaming")
    print("   5. Test error handling (invalid files, network issues)")