"""
GUI Components with Modern Dark Theme
Updated for thread-safe plotting and optimized RTT visualization
"""

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')  # Ensure Tk backend for Windows
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import logging

class ModernTheme:
    """Modern dark theme colors"""
    BG_COLOR = "#1e1e1e"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#00d4aa"
    SECONDARY_COLOR = "#2d2d2d"
    WARNING_COLOR = "#ff6b6b"
    SUCCESS_COLOR = "#51cf66"
    
    @classmethod
    def apply_theme(cls, root):
        """Apply dark theme to tkinter"""
        style = ttk.Style()
        style.theme_use('clam')
        
        root.configure(bg=cls.BG_COLOR)
        root.option_add('*Background', cls.BG_COLOR)
        root.option_add('*Foreground', cls.FG_COLOR)
        
        style.configure('TFrame', background=cls.BG_COLOR)
        style.configure('TLabel', background=cls.BG_COLOR, foreground=cls.FG_COLOR)
        style.configure('TButton', background=cls.SECONDARY_COLOR, foreground=cls.FG_COLOR)
        style.configure('TEntry', fieldbackground=cls.SECONDARY_COLOR, foreground=cls.FG_COLOR)
        style.configure('TNotebook', background=cls.BG_COLOR)
        style.configure('TNotebook.Tab', background=cls.SECONDARY_COLOR, foreground=cls.FG_COLOR)

class RTTGraph:
    """Real-time RTT visualization widget with thread-safe updates"""
    
    def __init__(self, parent, width=10, height=4):
        self.parent = parent
        self.figure = Figure(figsize=(width, height), facecolor='black')
        self.ax = self.figure.add_subplot(111, facecolor='#1e1e1e')
        
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.ax.set_ylabel('RTT (ms)', color='white', fontsize=10)
        self.ax.set_title('Real-time Ping Latency', color='white', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.rtt_data = []
        self.timestamps = []
        self.max_points = 50
        self.line, = self.ax.plot([], [], color=ModernTheme.ACCENT_COLOR, linewidth=2,
                                 marker='o', markersize=3, alpha=0.8)  # Initialize empty line
        
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.figure.autofmt_xdate()
    
    def update_plot(self, rtt: float, timestamp: datetime):
        """Update plot with new RTT data in a thread-safe manner"""
        try:
            self.rtt_data.append(rtt)
            self.timestamps.append(timestamp)
            
            if len(self.rtt_data) > self.max_points:
                self.rtt_data = self.rtt_data[-self.max_points:]
                self.timestamps = self.timestamps[-self.max_points:]
            
            # Update line data
            self.line.set_data(self.timestamps, self.rtt_data)
            
            # Adjust axes limits
            if self.rtt_data:
                self.ax.set_xlim(min(self.timestamps), max(self.timestamps))
                self.ax.set_ylim(0, max(max(self.rtt_data) * 1.1, 10))  # Dynamic y-limit with min 10ms
            
            # Redraw in Tkinter main thread if not already scheduled
            self.canvas.draw_idle()  # Use draw_idle for smoother updates
        except Exception as e:
            logging.error(f"Plot update error: {e}")

class StatsDisplay:
    """Advanced statistics display"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.labels = {}
        self.create_stats_display()
    
    def create_stats_display(self):
        """Create organized statistics layout"""
        title = ttk.Label(self.frame, text="📊 Ping Statistics", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 10))
        
        metrics_frame = ttk.Frame(self.frame)
        metrics_frame.pack(fill=tk.BOTH, expand=True)
        
        metrics = [
            ('Min RTT', 'ms'), ('Max RTT', 'ms'), 
            ('Avg RTT', 'ms'), ('Jitter', 'ms'),
            ('Packet Loss', '%'), ('Success Rate', '%')
        ]
        
        for i, (metric, unit) in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            metric_frame = ttk.Frame(metrics_frame)
            metric_frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            ttk.Label(metric_frame, text=f"{metric}:", 
                     font=('Arial', 10, 'bold')).pack(anchor='w')
            value_label = ttk.Label(metric_frame, text="--", 
                                   font=('Arial', 12), foreground=ModernTheme.ACCENT_COLOR)
            value_label.pack(anchor='w')
            self.labels[metric] = value_label
        
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
    
    def update_stats(self, stats: dict):
        """Update statistics display"""
        try:
            self.labels['Min RTT'].config(text=f"{stats['min']:.2f}")
            self.labels['Max RTT'].config(text=f"{stats['max']:.2f}")
            self.labels['Avg RTT'].config(text=f"{stats['avg']:.2f}")
            self.labels['Jitter'].config(text=f"{stats['jitter']:.2f}")
            self.labels['Packet Loss'].config(text=f"{stats['packet_loss']:.1f}")
            
            success_rate = ((stats['successful_pings'] / stats['total_pings']) * 100) if stats['total_pings'] else 0
            self.labels['Success Rate'].config(text=f"{success_rate:.1f}")
        except Exception as e:
            logging.error(f"Stats update error: {e}")