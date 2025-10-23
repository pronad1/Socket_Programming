"""
🔍 ICMP Pinger Lab - Complete GUI Application
Updated with visual feedback, timeout fixes, enhanced Echo Server, and fixed plotting
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
from datetime import datetime
import logging
import os
import sys
import csv
import platform
import subprocess
import socket

# Fallbacks for external modules to make this file self-contained
try:
    from ping_stats import PingStatistics  # type: ignore
    from icmp_client import ICMPPinger     # type: ignore
    from icmp_server import ICMPServer     # type: ignore
    from gui_components import ModernTheme, RTTGraph, StatsDisplay  # type: ignore
except Exception:
    # ---- Minimal ModernTheme ----
    class ModernTheme:
        BG_COLOR = "#0f111a"
        FG_COLOR = "#e6e6e6"
        SUCCESS_COLOR = "#19c37d"
        WARNING_COLOR = "#ff6b6b"
        ACCENT_COLOR = "#4f46e5"

        @staticmethod
        def apply_theme(root):
            style = ttk.Style()
            try:
                style.theme_use('clam')
            except Exception:
                pass
            style.configure("TFrame", background=ModernTheme.BG_COLOR)
            style.configure("TLabel", background=ModernTheme.BG_COLOR, foreground=ModernTheme.FG_COLOR)
            style.configure("TButton", padding=6)
            root.configure(bg=ModernTheme.BG_COLOR)

    # ---- Minimal PingStatistics ----
    class PingStatistics:
        def __init__(self):
            self.results = []  # list of (rtt_ms: float, success: bool)

        def clear(self):
            self.results = []

        def add_results(self, results):
            self.results = results[:]  # overwrite with current series

        def get_raw_rtts(self):
            return [rtt for rtt, ok in self.results if ok]

        def get_summary(self):
            total = len(self.results)
            successes = sum(1 for _, ok in self.results if ok)
            rtts = self.get_raw_rtts()
            if rtts:
                mn = min(rtts)
                mx = max(rtts)
                avg = sum(rtts) / len(rtts)
                # jitter: mean absolute delta between consecutive RTTs
                if len(rtts) > 1:
                    deltas = [abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))]
                    jitter = sum(deltas) / len(deltas)
                else:
                    jitter = 0.0
            else:
                mn = mx = avg = jitter = 0.0
            loss = ((total - successes) / total * 100.0) if total else 0.0
            return {
                "total_pings": total,
                "successful_pings": successes,
                "min": mn,
                "max": mx,
                "avg": avg,
                "jitter": jitter,
                "packet_loss": loss,
            }

    # ---- Minimal ICMPPinger using scapy ----
    class ICMPPinger:
        def __init__(self, timeout=2.0):
            self.timeout = timeout
            self._stop = threading.Event()
            self._thread = None

        def stop(self):
            self._stop.set()

        def start_ping_thread(self, host, count, interval, callback):
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._worker, args=(host, count, interval, callback), daemon=True
            )
            self._thread.start()

        def _worker(self, host, count, interval, callback):
            """Prefer platform-native ICMP on Windows (no admin), else Scapy, else subprocess ping."""
            # Try Scapy first if not Windows without admin
            use_windows_icmp = (os.name == 'nt' and not self._is_admin_windows())
            if use_windows_icmp:
                # Windows ICMP API path (no admin needed)
                for _ in range(count):
                    if self._stop.is_set():
                        break
                    rtt_ms, success = self._ping_windows_icmp(host, int(self.timeout * 1000))
                    callback([(float(rtt_ms), bool(success))])
                    time.sleep(max(0.0, interval))
                return

            # Attempt Scapy (may require admin)
            scapy_ok = False
            try:
                from scapy.all import IP, ICMP, sr1, conf
                conf.verb = 0
                scapy_ok = True
            except Exception:
                scapy_ok = False

            for seq in range(1, count + 1):
                if self._stop.is_set():
                    break
                rtt_ms = 0.0
                success = False
                if scapy_ok:
                    try:
                        # Resolve hostname early to avoid repeated DNS lookups
                        dst = socket.gethostbyname(host)
                        pkt = IP(dst=dst) / ICMP(seq=seq)
                        t0 = time.monotonic()
                        reply = sr1(pkt, timeout=self.timeout)
                        t1 = time.monotonic()
                        if reply is not None and reply.haslayer(ICMP) and reply.getlayer(ICMP).type == 0:
                            rtt_ms = (t1 - t0) * 1000.0
                            success = True
                    except PermissionError:
                        # No raw socket permission -> fallback
                        success = False
                    except Exception:
                        success = False

                if not success:
                    # Final fallback: subprocess ping (cross-platform)
                    rtt_sub, ok_sub = self._ping_subprocess(host, int(self.timeout * 1000))
                    if ok_sub:
                        rtt_ms, success = rtt_sub, True

                callback([(rtt_ms, success)])
                time.sleep(max(0.0, interval))

        def _is_admin_windows(self):
            if os.name != 'nt':
                return False
            try:
                import ctypes
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception:
                return False

        def _ping_windows_icmp(self, host, timeout_ms):
            """Use Windows IP Helper API (IcmpSendEcho). Returns (rtt_ms, success)."""
            try:
                import ctypes
                from ctypes import wintypes

                iphlpapi = ctypes.windll.iphlpapi
                ws2_32 = ctypes.windll.ws2_32

                class IP_OPTION_INFORMATION(ctypes.Structure):
                    _fields_ = [
                        ("Ttl", ctypes.c_ubyte),
                        ("Tos", ctypes.c_ubyte),
                        ("Flags", ctypes.c_ubyte),
                        ("OptionsSize", ctypes.c_ubyte),
                        ("OptionsData", ctypes.c_void_p),
                    ]

                class ICMP_ECHO_REPLY(ctypes.Structure):
                    _fields_ = [
                        ("Address", wintypes.DWORD),
                        ("Status", wintypes.DWORD),
                        ("RoundTripTime", wintypes.DWORD),
                        ("DataSize", wintypes.WORD),
                        ("Reserved", wintypes.WORD),
                        ("Data", ctypes.c_void_p),
                        ("Options", IP_OPTION_INFORMATION),
                    ]

                # Resolve host
                try:
                    dst_ip = socket.gethostbyname(host)
                except Exception:
                    return (0.0, False)

                addr = ws2_32.inet_addr(dst_ip.encode('ascii'))
                if addr == 0xFFFFFFFF:
                    return (0.0, False)

                handle = iphlpapi.IcmpCreateFile()
                if handle == ctypes.c_void_p(-1).value:
                    return (0.0, False)

                data = b'0123456789abcdef'  # 16 bytes payload
                reply_size = ctypes.sizeof(ICMP_ECHO_REPLY) + len(data) + 8
                reply_buf = ctypes.create_string_buffer(reply_size)

                ret = iphlpapi.IcmpSendEcho(
                    handle,
                    addr,
                    data,
                    len(data),
                    None,
                    reply_buf,
                    reply_size,
                    int(timeout_ms),
                )

                success = ret != 0
                rtt = 0
                if success:
                    reply = ICMP_ECHO_REPLY.from_buffer(reply_buf)
                    success = (reply.Status == 0)
                    rtt = int(reply.RoundTripTime)

                iphlpapi.IcmpCloseHandle(handle)
                return (float(rtt), bool(success))
            except Exception:
                return (0.0, False)

        def _ping_subprocess(self, host, timeout_ms):
            """Portable subprocess ping fallback. Returns (rtt_ms, success)."""
            try:
                if platform.system().lower().startswith('win'):
                    # -n 1 (one echo), -w timeout_ms
                    cmd = ["ping", "-n", "1", "-w", str(int(timeout_ms)), host]
                else:
                    # -c 1 (one echo), -W timeout (seconds)
                    tsec = max(1, int(round(timeout_ms / 1000.0)))
                    cmd = ["ping", "-c", "1", "-W", str(tsec), host]
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=max(1, int(timeout_ms/1000)+2))
                text = out.stdout + out.stderr
                if out.returncode == 0:
                    # Parse RTT from output
                    # Windows: "time=23ms", Linux: "time=23.4 ms"
                    import re
                    m = re.search(r"time[=<]\s*([\d\.]+)\s*ms", text, re.IGNORECASE)
                    if m:
                        return (float(m.group(1)), True)
                    # Some Windows locales print "Tiempo="; fallback to success without RTT
                    return (0.0, True)
                return (0.0, False)
            except Exception:
                return (0.0, False)

    # ---- Minimal ICMPServer (simulation mode) ----
    class ICMPServer:
        def __init__(self, delay_range=(0, 0.05)):
            self.delay_range = delay_range
            self.running = False
            self._thread = None
            self._cb = None
            self._requests = 0
            self._bytes = 0

        def set_stats_callback(self, cb):
            self._cb = cb

        def start(self):
            if self.running:
                return True
            self.running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            return True  # simulation always "starts"

        def _run(self):
            while self.running:
                time.sleep(1.0)
                # simulate some activity
                self._requests += 1
                self._bytes += 64
                if self._cb:
                    ts = datetime.now().strftime("%H:%M:%S")
                    self._cb(ts, {"requests": self._requests, "bytes": self._bytes})

        def stop(self):
            self.running = False

    # ---- Minimal RTTGraph (matplotlib embed) ----
    class RTTGraph:
        def __init__(self, parent):
            self.rtt_data = []
            self.timestamps = []
            try:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                from matplotlib.figure import Figure
                self._Figure = Figure
                self._Canvas = FigureCanvasTkAgg
                self.figure = self._Figure(figsize=(6, 3), dpi=100)
                self.ax = self.figure.add_subplot(111)
                self.ax.set_title("RTT (ms)")
                self.ax.set_xlabel("Time")
                self.ax.set_ylabel("ms")
                self.line, = self.ax.plot([], [], color=ModernTheme.ACCENT_COLOR)
                self.canvas = self._Canvas(self.figure, master=parent)
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.canvas.draw()
                self._enabled = True
            except Exception:
                self._enabled = False  # gracefully degrade

        def update_plot(self, rtt_ms, ts):
            self.rtt_data.append(rtt_ms)
            self.timestamps.append(ts)
            if not getattr(self, "_enabled", False):
                return
            xs = list(range(1, len(self.rtt_data) + 1))
            self.line.set_data(xs, self.rtt_data)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw_idle()

    # ---- Minimal StatsDisplay ----
    class StatsDisplay:
        def __init__(self, parent):
            frame = ttk.LabelFrame(parent, text="Summary", padding=10)
            frame.pack(fill=tk.X, padx=10, pady=10)
            self._labels = {}
            for i, key in enumerate(["total_pings", "successful_pings", "min", "max", "avg", "jitter", "packet_loss"]):
                ttk.Label(frame, text=key.replace("_", " ").title() + ":").grid(row=i, column=0, sticky="w", padx=5, pady=2)
                var = tk.StringVar(value="-")
                ttk.Label(frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=5, pady=2)
                self._labels[key] = var

        def update_stats(self, stats):
            for k, v in stats.items():
                if k in ["min", "max", "avg", "jitter"]:
                    self._labels[k].set(f"{v:.2f} ms")
                elif k == "packet_loss":
                    self._labels[k].set(f"{v:.1f}%")
                else:
                    self._labels[k].set(str(v))

class ICMPPingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 ICMP Pinger Lab - Advanced Network Diagnostics")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Initialize components
        self.pinger = ICMPPinger(timeout=5.0)
        self.server = None
        self.stats = PingStatistics()
        self.is_pinging = False
        self.current_host = ""
        self.ping_results = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Apply modern theme
        ModernTheme.apply_theme(root)
        
        # Check Windows admin status
        if os.name == 'nt':
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    messagebox.showwarning("Admin Required", 
                        "Run as Administrator for full ICMP functionality!\n\n"
                        "• Ping client: Limited without admin (may show timeouts)\n"
                        "• Echo server: Requires admin privileges")
            except:
                pass
        
        self.setup_gui()
    
    def setup_gui(self):
        """Main GUI setup with proper geometry management"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_controls(main_frame)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.client_frame = ttk.Frame(notebook)
        notebook.add(self.client_frame, text="🏓 Ping Client")
        self.setup_client_tab()
        
        self.server_frame = ttk.Frame(notebook)
        notebook.add(self.server_frame, text="📡 Echo Server")
        self.setup_server_tab()
        
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="📊 Statistics")
        self.setup_stats_tab()
    
    def setup_controls(self, parent):
        """Global control panel"""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var,
                                foreground=ModernTheme.SUCCESS_COLOR, font=('Arial', 10))
        status_label.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="🗑️ Clear All", 
                  command=self.clear_all).pack(side=tk.RIGHT, padx=5)
    
    def setup_client_tab(self):
        """Ping client interface"""
        config_frame = ttk.LabelFrame(self.client_frame, text="Ping Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Target Host:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.host_var = tk.StringVar(value="8.8.8.8")
        host_entry = ttk.Entry(config_frame, textvariable=self.host_var, width=25)
        host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Count:").grid(row=0, column=2, sticky='w', padx=(20, 5))
        self.count_var = tk.StringVar(value="10")
        ttk.Entry(config_frame, textvariable=self.count_var, width=8).grid(row=0, column=3, padx=5)
        
        ttk.Label(config_frame, text="Interval (s):").grid(row=0, column=4, sticky='w', padx=(20, 5))
        self.interval_var = tk.StringVar(value="1.0")
        ttk.Entry(config_frame, textvariable=self.interval_var, width=8).grid(row=0, column=5, padx=5)
        
        self.start_btn = ttk.Button(config_frame, text="🚀 Start Ping", 
                                   command=self.start_ping)
        self.start_btn.grid(row=0, column=6, padx=10)
        
        self.stop_btn = ttk.Button(config_frame, text="⏹️ Stop", 
                                  command=self.stop_ping, state='disabled')
        self.stop_btn.grid(row=0, column=7, padx=5)
        
        results_frame = ttk.LabelFrame(self.client_frame, text="Live Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        results_container = ttk.Frame(results_frame)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        graph_frame = ttk.Frame(results_container)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.rtt_graph = RTTGraph(graph_frame)
        
        log_frame = ttk.Frame(results_container)
        log_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, bg=ModernTheme.BG_COLOR,
                               fg=ModernTheme.FG_COLOR, height=15, width=40,
                               font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL,
                                 command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_server_tab(self):
        """Echo server interface with enhanced idle state"""
        controls_frame = ttk.LabelFrame(self.server_frame, text="Server Configuration", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Listen Address:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.server_host_var = tk.StringVar(value="0.0.0.0")
        host_entry = ttk.Entry(controls_frame, textvariable=self.server_host_var, width=15)
        host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(controls_frame, text="Response Delay (ms):").grid(row=0, column=2, sticky='w', padx=(20, 5))
        self.delay_var = tk.StringVar(value="50")
        delay_entry = ttk.Entry(controls_frame, textvariable=self.delay_var, width=8)
        delay_entry.grid(row=0, column=3, padx=5)
        
        self.server_start_btn = ttk.Button(controls_frame, text="▶️ Start Server",
                                          command=self.start_server)
        self.server_start_btn.grid(row=0, column=4, padx=10)
        
        self.stop_server_btn = ttk.Button(controls_frame, text="⏹️ Stop Server",
                                         command=self.stop_server, state='disabled')
        self.stop_server_btn.grid(row=0, column=5, padx=5)
        
        self.server_status = ttk.Label(controls_frame, text="🔴 Server: Stopped",
                                      foreground=ModernTheme.WARNING_COLOR)
        self.server_status.grid(row=1, column=0, columnspan=6, pady=5, sticky='w')
        
        help_text = "💡 Run as Administrator for full server functionality. Simulation mode available."
        help_label = ttk.Label(controls_frame, text=help_text, foreground=ModernTheme.FG_COLOR, font=('Arial', 8, 'italic'))
        help_label.grid(row=2, column=0, columnspan=6, pady=(0, 5), sticky='w')
        
        ttk.Button(controls_frame, text="✅ Validate", command=self.validate_config).grid(row=3, column=4, columnspan=2, pady=5)
        
        log_frame = ttk.LabelFrame(self.server_frame, text="Server Activity", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.server_log = tk.Text(log_container, bg=ModernTheme.BG_COLOR,
                                 fg=ModernTheme.FG_COLOR, height=20,
                                 font=('Consolas', 9))
        server_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL,
                                        command=self.server_log.yview)
        self.server_log.configure(yscrollcommand=server_scrollbar.set)
        
        placeholder = "Server log will appear here when started. Run as Administrator for real-time ICMP responses."
        self.server_log.insert(tk.END, placeholder)
        self.server_log.config(state=tk.DISABLED)
        
        self.server_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        server_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def validate_config(self):
        """Validate server configuration"""
        try:
            host = self.server_host_var.get().strip()
            delay = float(self.delay_var.get())
            
            if not host:
                messagebox.showwarning("Validation", "Listen address cannot be empty")
                return
            if delay < 0:
                messagebox.showwarning("Validation", "Delay must be non-negative")
                return
            
            messagebox.showinfo("Validation", "Configuration is valid!")
        except ValueError:
            messagebox.showwarning("Validation", "Invalid delay value")

    def start_server(self):
        """Start the echo server with log initialization"""
        self.server_log.config(state=tk.NORMAL)
        self.server_log.delete(1.0, tk.END)
        self._start_server()

    def _start_server(self):
        """Internal start server method"""
        try:
            delay_ms = float(self.delay_var.get()) / 1000
            self.server = ICMPServer(delay_range=(0, delay_ms))
            self.server.set_stats_callback(lambda ts, stats: self.root.after(0, lambda: self.update_server_log(ts, stats)))
            
            if self.server.start():
                self.server_start_btn.config(state='disabled')
                self.stop_server_btn.config(state='normal')
                self.server_status.config(text="🟢 Server: Running (Simulation Mode)",
                                        foreground=ModernTheme.SUCCESS_COLOR)
                
                threading.Thread(target=self.monitor_server, daemon=True).start()
            else:
                messagebox.showerror("Error", "Server start failed. Admin privileges required for full functionality.")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid delay value")

    def update_server_log(self, timestamp, stats):
        """Update server log in a thread-safe manner"""
        self.server_log.insert(tk.END, f"[{timestamp}] 📈 Requests: {stats['requests']} | Bytes: {stats['bytes']}\n")
        self.server_log.see(tk.END)

    def monitor_server(self):
        """Monitor server statistics (no-op since callback handles updates)"""
        while self.server and self.server.running:
            time.sleep(1)  # Sync with simulation interval

    def setup_stats_tab(self):
        """Statistics display tab"""
        self.stats_display = StatsDisplay(self.stats_frame)
        
        btn_frame = ttk.Frame(self.stats_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="💾 Export CSV", command=self.export_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        data_frame = ttk.LabelFrame(self.stats_frame, text="Raw Data", padding=5)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.data_text = tk.Text(data_frame, height=10, bg=ModernTheme.BG_COLOR,
                                fg=ModernTheme.FG_COLOR, font=('Consolas', 9))
        data_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL,
                                      command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=data_scrollbar.set)
        
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def start_ping(self):
        """Start ping operation with visual feedback"""
        try:
            host = self.host_var.get().strip()
            if not host:
                messagebox.showerror("Error", "Please enter target host")
                return
            
            count = int(self.count_var.get())
            interval = float(self.interval_var.get())
            
            if count <= 0 or interval <= 0:
                messagebox.showerror("Error", "Count and interval must be positive")
                return
            
            self.current_host = host
            self.is_pinging = True
            self.stats.clear()
            self.ping_results = []
            
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_var.set("🏓 Pinging... ⏳")
            
            self.pulse_status()
            self.pinger.start_ping_thread(host, count, interval, self.ping_callback)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"Ping failed: {e}")
    
    def pulse_status(self):
        """Pulse effect for 'Pinging...' status"""
        if self.is_pinging:
            current = self.status_var.get()
            if "⏳" in current:
                self.status_var.set(f"🏓 Pinging... {'⠋' if time.time() % 1 < 0.5 else '⠙'}")
            else:
                self.status_var.set("🏓 Pinging... ⏳")
            self.root.after(500, self.pulse_status)
    
    def ping_callback(self, results):
        """Handle ping completion with real-time updates"""
        self.root.after(0, lambda: self.process_results(results))
    
    def process_results(self, results):
        """Process and display ping results in real-time with fixed plotting"""
        self.ping_results.extend(results)
        self.stats.add_results(self.ping_results)

        for i, (rtt, success) in enumerate(results):
            seq = len(self.ping_results) - len(results) + i
            status = "✅ SUCCESS" if success else "❌ TIMEOUT"
            color = ModernTheme.SUCCESS_COLOR if success else ModernTheme.WARNING_COLOR
            timestamp = datetime.now().strftime("%H:%M:%S")

            log_entry = f"[{timestamp}] {status} | Seq: {seq} | RTT: {rtt:.2f}ms\n"
            self.log_text.insert(tk.END, log_entry)

            # FIX: proper Tk text index for tagging
            start_idx = f"end-{len(log_entry)}c"
            end_idx = "end"
            if success:
                self.log_text.tag_add("success", start_idx, end_idx)
                self.root.after(0, lambda rtt=rtt, ts=datetime.now(): self.rtt_graph.update_plot(rtt, ts))
            else:
                self.log_text.tag_add("error", start_idx, end_idx)

        self.log_text.tag_config("success", foreground=ModernTheme.SUCCESS_COLOR)
        self.log_text.tag_config("error", foreground=ModernTheme.WARNING_COLOR)
        self.log_text.see(tk.END)
        
        self.update_stats_display()
        
        if len(self.ping_results) >= int(self.count_var.get()):
            self.ping_finished()
    
    def ping_finished(self):
        """Handle ping completion"""
        self.is_pinging = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set(f"✅ Ping to {self.current_host} completed")

    def stop_ping(self):
        """Stop current ping"""
        self.pinger.stop()
        self.is_pinging = False
        self.start_btn.config(state='normal')       # enable Start after stop
        self.stop_btn.config(state='disabled')      # disable Stop after stop
        self.status_var.set("⏹️ Ping stopped by user")

    def stop_server(self):
        """Stop echo server"""
        if self.server:
            self.server.stop()
            self.server = None
            self.server_start_btn.config(state='normal')
            self.stop_server_btn.config(state='disabled')
            self.server_status.config(text="🔴 Server: Stopped",
                                     foreground=ModernTheme.WARNING_COLOR)
    
    def update_stats_display(self):
        """Update statistics in GUI"""
        stats = self.stats.get_summary()
        self.stats_display.update_stats(stats)
        
        rtts = self.stats.get_raw_rtts()
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, f"Target: {self.current_host}\n")
        self.data_text.insert(tk.END, f"Total Pings: {stats['total_pings']}\n")
        self.data_text.insert(tk.END, f"Successful: {stats['successful_pings']}\n\n")
        self.data_text.insert(tk.END, "RTT Values (ms):\n")
        for i, rtt in enumerate(rtts[-20:]):
            self.data_text.insert(tk.END, f"  {i+1}: {rtt:.2f}\n")
    
    def clear_all(self):
        """Clear all data"""
        self.stats.clear()
        self.log_text.delete(1.0, tk.END)
        self.server_log.delete(1.0, tk.END)
        self.data_text.delete(1.0, tk.END)
        self.rtt_graph.rtt_data = []
        self.rtt_graph.timestamps = []
        # +++ guard if matplotlib backend not available
        if hasattr(self.rtt_graph, "canvas"):
            self.rtt_graph.canvas.draw()
        self.status_var.set("🗑️ All data cleared")
        self.update_stats_display()
    
    def export_stats(self):
        """Export statistics to CSV"""
        if not self.stats.results:
            messagebox.showwarning("No Data", "No ping data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                stats = self.stats.get_summary()
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ICMP Ping Statistics Report"])
                    writer.writerow([f"Target: {self.current_host}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}"])
                    writer.writerow([])
                    writer.writerow(["Metric", "Value", "Unit"])
                    writer.writerow(["Minimum RTT", f"{stats['min']:.2f}", "ms"])
                    writer.writerow(["Maximum RTT", f"{stats['max']:.2f}", "ms"])
                    writer.writerow(["Average RTT", f"{stats['avg']:.2f}", "ms"])
                    writer.writerow(["Jitter", f"{stats['jitter']:.2f}", "ms"])
                    writer.writerow(["Packet Loss", f"{stats['packet_loss']:.1f}", "%"])
                    writer.writerow(["Success Rate", f"{(stats['successful_pings']/stats['total_pings']*100):.1f}", "%"])
                
                messagebox.showinfo("Success", f"Statistics exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")
    
    def generate_report(self):
        """Generate detailed report window"""
        if not self.stats.results:
            messagebox.showwarning("No Data", "No statistics available for report")
            return

        stats = self.stats.get_summary()
        analysis = []
        if stats['packet_loss'] < 10:
            analysis.append("- Low packet loss indicates a stable connection")
        else:
            analysis.append(f"- High packet loss ({stats['packet_loss']:.1f}%) suggests network issues")
        if stats['jitter'] > 20:
            analysis.append("- High jitter suggests network congestion")
        else:
            analysis.append("- Low jitter indicates consistent latency")
        analysis.append(f"- Average RTT of {stats['avg']:.2f} ms reflects overall latency")

        # FIX: proper newline join and clean timestamp line
        analysis_text = "\n".join(analysis)
        report = f"""
🔍 ICMP PINGER LAB - DIAGNOSTIC REPORT
{'='*50}
Target Host: {self.current_host}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Pings: {stats['total_pings']}
Successful: {stats['successful_pings']}

📊 KEY METRICS:
{'-'*20}
• Minimum RTT:     {stats['min']:.2f} ms
• Maximum RTT:     {stats['max']:.2f} ms
• Average RTT:     {stats['avg']:.2f} ms
• Jitter:          {stats['jitter']:.2f} ms
• Packet Loss:     {stats['packet_loss']:.1f}%
• Success Rate:    {(stats['successful_pings']/stats['total_pings']*100):.1f}%

💡 ANALYSIS:
{'-'*20}
{analysis_text}
        """

        report_window = tk.Toplevel(self.root)
        report_window.title("Diagnostic Report")
        report_window.geometry("600x500")

        text_widget = scrolledtext.ScrolledText(report_window, wrap=tk.WORD,
                                               bg=ModernTheme.BG_COLOR,
                                               fg=ModernTheme.FG_COLOR,
                                               font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ICMPPingerApp(root)
    
    def on_closing():
        if app.is_pinging:
            app.stop_ping()
        if app.server:
            app.stop_server()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    print("🔍 Starting ICMP Pinger Lab...")
    print("💡 TIP: Right-click PowerShell → 'Run as Administrator' for full features!")
    print("📡 Basic ping works without admin, server needs privileges")
    main()