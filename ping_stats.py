"""
Ping Statistics Calculator (Renamed to avoid stdlib conflict)
"""

from typing import List, Tuple
import statistics as std_statistics
import numpy as np

class PingStatistics:
    def __init__(self):
        self.results: List[Tuple[float, bool]] = []
        self.packet_loss = 0.0
    
    def add_results(self, results: List[Tuple[float, bool]]):
        """Add ping results"""
        self.results.extend(results)
        successful_pings = sum(1 for rtt, success in results if success)
        total_pings = len(results)
        self.packet_loss = ((total_pings - successful_pings) / total_pings * 100) if total_pings else 0
    
    def get_summary(self) -> dict:
        """Get comprehensive statistics"""
        rtts = [rtt for rtt, success in self.results if success]
        
        if not rtts:
            return {
                'min': 0, 'max': 0, 'avg': 0, 'std': 0, 
                'median': 0, 'packet_loss': self.packet_loss,
                'successful_pings': 0, 'total_pings': len(self.results),
                'jitter': 0
            }
        
        try:
            jitter = float(np.std(np.diff(sorted(rtts))) * 1000) if len(rtts) > 1 else 0
        except:
            jitter = 0
        
        return {
            'min': min(rtts),
            'max': max(rtts),
            'avg': std_statistics.mean(rtts),
            'std': std_statistics.stdev(rtts) if len(rtts) > 1 else 0,
            'median': std_statistics.median(rtts),
            'packet_loss': self.packet_loss,
            'successful_pings': len(rtts),
            'total_pings': len(self.results),
            'jitter': jitter
        }
    
    def clear(self):
        """Clear statistics"""
        self.results = []
        self.packet_loss = 0.0
    
    def get_raw_rtts(self) -> List[float]:
        """Get raw RTT values for plotting"""
        return [rtt for rtt, success in self.results if success]