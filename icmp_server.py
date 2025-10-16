"""
ICMP Echo Server (Simplified for Windows compatibility)
"""

import threading
import time
import random
import logging
from datetime import datetime
import os

class ICMPServer:
    def __init__(self, delay_range: tuple = (0, 0.05)):
        self.delay_range = delay_range
        self.running = False
        self.stats = {"requests": 0, "bytes": 0}
        self.monitor_thread = None
        self._stats_callback = None  # Callback to report stats
        
    def set_stats_callback(self, callback):
        """Set the callback function to report stats"""
        self._stats_callback = callback
    
    def start(self):
        """Start server monitoring (simulated)"""
        try:
            self.running = True
            logging.info("ICMP Server simulation started")
            
            self.monitor_thread = threading.Thread(target=self._simulate_activity)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            return True
        except Exception as e:
            logging.error(f"Server start failed: {e}")
            return False
    
    def _simulate_activity(self):
        """Simulate server activity for demo purposes"""
        while self.running:
            if random.random() < 0.5:  # 50% chance for activity
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                self.stats["requests"] += 1
                self.stats["bytes"] += random.randint(64, 1500)
                timestamp = datetime.now().strftime("%H:%M:%S")
                logging.info(f"Simulated echo reply, delay={delay*1000:.1f}ms")
                # Notify callback with updated stats
                if self._stats_callback:
                    self._stats_callback(timestamp, self.stats.copy())
            time.sleep(1)  # Check every 1 second
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        logging.info("ICMP Server stopped")
    
    def get_stats(self) -> dict:
        """Get server statistics"""
        return self.stats.copy()
    
    def handle_packet(self, packet):
        """Placeholder for real packet handling (requires admin)"""
        pass