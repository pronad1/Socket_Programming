"""
ICMP Ping Client Implementation using Scapy
Updated for reliability and error handling
"""

import time
from datetime import datetime
import logging
import threading
from scapy.all import sr1, IP, ICMP, conf
import os

class ICMPPinger:
    def __init__(self, timeout=10.0):
        self.timeout = timeout  # Increased to 10s for slower networks
        self.running = False
        self.results = []
        self.stop_event = threading.Event()
        
        # Configure Scapy to use Npcap if available
        if os.name == 'nt':
            conf.use_pcap = True  # Force Npcap usage on Windows
        
        logging.info("ICMP Pinger initialized with timeout %.1f seconds", self.timeout)

    def ping(self, host, count=4, interval=1.0):
        """Send ICMP Echo Requests to a host and return results"""
        self.results = []
        for i in range(count):
            if self.stop_event.is_set():
                break
                
            try:
                # Construct and send ICMP Echo Request
                packet = IP(dst=host) / ICMP(type=8, code=0)
                start_time = time.time()
                
                # Send packet and wait for reply
                response = sr1(packet, timeout=self.timeout, verbose=False)
                end_time = time.time()
                
                rtt = (end_time - start_time) * 1000 if response else 0.0
                success = response is not None and response.getlayer(ICMP).type == 0
                
                self.results.append((rtt, success))
                logging.info("Ping %d to %s: RTT=%.2fms, Success=%s", i+1, host, rtt, success)
                
            except Exception as e:
                logging.error("Ping failed: %s", e)
                self.results.append((0.0, False))  # Timeout case
            
            if i < count - 1:
                time.sleep(interval)
        
        return self.results

    def start_ping_thread(self, host, count, interval, callback):
        """Start pinging in a separate thread with callback"""
        self.running = True
        self.stop_event.clear()
        
        def ping_thread():
            try:
                results = self.ping(host, count, interval)
                if self.running and callback:
                    callback(results)
            except Exception as e:
                logging.error("Ping thread error: %s", e)
                if callback:
                    callback([])
            finally:
                self.running = False
        
        thread = threading.Thread(target=ping_thread, daemon=True)
        thread.start()

    def stop(self):
        """Stop the current ping operation"""
        self.stop_event.set()
        self.running = False
        logging.info("Ping operation stopped")

if __name__ == "__main__":
    pinger = ICMPPinger()
    results = pinger.ping("8.8.8.8", count=5, interval=1.0)
    for rtt, success in results:
        print(f"RTT: {rtt:.2f}ms, Success: {success}")