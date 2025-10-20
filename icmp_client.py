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
import platform
import subprocess
import socket
import re
try:
    import ctypes
    from ctypes import wintypes
except Exception:
    ctypes = None

class ICMPPinger:
    def __init__(self, timeout=10.0):
        self.timeout = timeout  # Increased to 10s for slower networks
        self.running = False
        self.results = []
        self.stop_event = threading.Event()
        
        # Configure Scapy quietly; do NOT force pcap — it breaks if Npcap isn't installed
        try:
            conf.verb = 0
        except Exception:
            pass
        
        logging.info("ICMP Pinger initialized with timeout %.1f seconds", self.timeout)

    # +++ helper: admin detection (Windows)
    def _is_admin_windows(self):
        if os.name != 'nt' or ctypes is None:
            return False
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    # +++ helper: Windows ICMP API (works without admin)
    def _ping_windows_icmp(self, host, timeout_ms):
        if os.name != 'nt' or ctypes is None:
            return (0.0, False)
        try:
            iphlpapi = ctypes.windll.iphlpapi
            ws2_32 = ctypes.windll.ws2_32

            # Declare prototypes to avoid calling convention/size issues
            try:
                ws2_32.inet_addr.argtypes = [ctypes.c_char_p]
                ws2_32.inet_addr.restype = wintypes.DWORD

                iphlpapi.IcmpCreateFile.restype = ctypes.c_void_p

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

                iphlpapi.IcmpSendEcho.argtypes = [
                    ctypes.c_void_p,         # IcmpHandle
                    wintypes.DWORD,          # DestinationAddress
                    ctypes.c_void_p,         # RequestData
                    wintypes.WORD,           # RequestSize
                    ctypes.POINTER(IP_OPTION_INFORMATION),  # RequestOptions
                    ctypes.c_void_p,         # ReplyBuffer
                    wintypes.DWORD,          # ReplySize
                    wintypes.DWORD,          # Timeout
                ]
                iphlpapi.IcmpSendEcho.restype = wintypes.DWORD

                iphlpapi.IcmpCloseHandle.argtypes = [ctypes.c_void_p]
                iphlpapi.IcmpCloseHandle.restype = wintypes.BOOL
            except Exception:
                # If prototypes fail, continue with best effort
                pass

            # Resolve once
            try:
                dst_ip = socket.gethostbyname(host)
            except Exception:
                logging.debug("Windows ICMP: DNS resolution failed for %s", host)
                return (0.0, False)

            addr = ws2_32.inet_addr(dst_ip.encode('ascii'))
            if addr == 0xFFFFFFFF:
                logging.debug("Windows ICMP: inet_addr failed for %s", dst_ip)
                return (0.0, False)

            handle = iphlpapi.IcmpCreateFile()
            if handle in (None, 0, ctypes.c_void_p(-1).value):
                logging.debug("Windows ICMP: IcmpCreateFile failed")
                return (0.0, False)

            data = b'0123456789abcdef'  # 16 bytes payload
            reply_size = ctypes.sizeof(ICMP_ECHO_REPLY) + len(data) + 8
            reply_buf = ctypes.create_string_buffer(reply_size)

            ret = iphlpapi.IcmpSendEcho(
                handle,
                addr,
                ctypes.c_char_p(data),
                len(data),
                None,
                ctypes.byref(reply_buf),
                reply_size,
                int(timeout_ms),
            )

            success = ret != 0
            rtt = 0.0
            if success:
                reply = ICMP_ECHO_REPLY.from_buffer(reply_buf)
                success = (reply.Status == 0)
                rtt = float(reply.RoundTripTime)

            iphlpapi.IcmpCloseHandle(handle)

            if not success:
                logging.debug("Windows ICMP: IcmpSendEcho returned Status!=0")
            else:
                logging.debug("Windows ICMP: success RTT=%.2f ms", rtt)

            return (rtt, bool(success))
        except Exception as e:
            logging.debug("Windows ICMP exception: %s", e)
            return (0.0, False)

    # +++ helper: subprocess ping (cross-platform fallback)
    def _ping_subprocess(self, host, timeout_ms):
        try:
            if platform.system().lower().startswith('win'):
                cmd = ["ping", "-n", "1", "-w", str(int(timeout_ms)), host]
            else:
                tsec = max(1, int(round(timeout_ms / 1000.0)))
                cmd = ["ping", "-c", "1", "-W", str(tsec), host]
            out = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=max(1, int(timeout_ms/1000) + 2)
            )
            text = out.stdout + out.stderr
            if out.returncode == 0:
                m = re.search(r"time[=<]\s*([\d\.]+)\s*ms", text, re.IGNORECASE)
                if m:
                    return (float(m.group(1)), True)
                return (0.0, True)  # success but couldn't parse RTT
            return (0.0, False)
        except Exception:
            return (0.0, False)

    def ping(self, host, count=4, interval=1.0):
        """Send ICMP Echo Requests to a host and return results"""
        self.results = []
        use_windows_icmp = (os.name == 'nt' and not self._is_admin_windows())

        for i in range(count):
            if self.stop_event.is_set():
                break

            rtt = 0.0
            success = False
            try:
                if use_windows_icmp:
                    # Try Windows API first; if it fails, fallback to subprocess
                    rtt, success = self._ping_windows_icmp(host, int(self.timeout * 1000))
                    if not success:
                        rtt, success = self._ping_subprocess(host, int(self.timeout * 1000))
                        if not success:
                            logging.debug("Subprocess ping failed")
                else:
                    # Try Scapy first (likely admin)
                    try:
                        packet = IP(dst=host) / ICMP(type=8, code=0)
                        start_time = time.monotonic()
                        response = sr1(packet, timeout=self.timeout, verbose=False)
                        end_time = time.monotonic()
                        if response is not None and response.haslayer(ICMP) and response.getlayer(ICMP).type == 0:
                            rtt = (end_time - start_time) * 1000.0
                            success = True
                    except PermissionError:
                        success = False
                    except Exception:
                        success = False

                    if not success:
                        rtt, success = self._ping_subprocess(host, int(self.timeout * 1000))
            except Exception as e:
                logging.error("Ping failed: %s", e)
                rtt, success = 0.0, False

            self.results.append((rtt, success))
            logging.info("Ping %d to %s: RTT=%.2fms, Success=%s", i+1, host, rtt, success)

            if i < count - 1 and not self.stop_event.is_set():
                time.sleep(max(0.0, interval))

        return self.results

    def start_ping_thread(self, host, count, interval, callback):
        """Start pinging in a separate thread with per-ping updates via callback"""
        self.running = True
        self.stop_event.clear()

        def ping_thread():
            try:
                self.results = []
                # Stream per-ping results to GUI
                for i in range(count):
                    if self.stop_event.is_set():
                        break

                    # Reuse core logic for one probe
                    single = self.ping(host, count=1, interval=0.0)
                    # Callback expects a list of (rtt, success)
                    if self.running and callback and single:
                        callback(single)

                    if i < count - 1 and not self.stop_event.is_set():
                        time.sleep(max(0.0, interval))
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