# ICMP Pinger Lab (Python)
A GUI-based ICMP ping application with live RTT graphing, per-ping logs, and summary statistics. Works on Windows without administrator rights using the Windows ICMP API, and uses Scapy/raw sockets when privileges are available. Includes an optional echo server simulation inside the GUI.



## Table of Contents
- Overview
- Features
- Prerequisites
- Installation
- Project Structure
- Usage
- Troubleshooting
- License
- Contact

## Overview
This lab provides:
- A modern GUI ping client to measure RTT and packet loss.
- An optional echo server simulation to visualize server-side activity.
- Robust Windows support:
  - No admin needed for basic pings (uses Windows ICMP API).
  - Admin enables Scapy/raw sockets path.

## Features
- GUI controls: target host, count, interval
- Per-ping RTT reporting and colored log status
- Live RTT plot and summary statistics (min/max/avg, jitter, loss)
- CSV export and a readable diagnostic report
- Echo server simulation with adjustable delay

## Prerequisites
- Python 3.8+
- Install dependencies:
  - pip install -r requirements.txt
- Windows notes:
  - Basic pings work without admin (Windows ICMP API).
  - For Scapy/raw sockets and real sniffing, run PowerShell as Administrator and consider Npcap.

## Installation
```bash
# Optional: create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure
```
d:\Languages\Socket_Programming\
├── README.md
├── requirements.txt
├── main.py                # GUI application (entry point)
└── icmp_client.py         # ICMP ping client with Windows/Scapy/subprocess fallbacks
```

## Usage

### Start the GUI
```bash
python d:\Languages\Socket_Programming\main.py
```
- Enter Target Host (e.g., 8.8.8.8), Count, and Interval (s).
- Click “Start Ping” to see live results, graph, and statistics.
- Use “Export CSV” or “Generate Report” in the Statistics tab.
- The Echo Server tab runs a simulation for server activity logs.

### Quick CLI check (optional)
```bash
python d:\Languages\Socket_Programming\icmp_client.py
```
Prints RTT and success for a few pings to 8.8.8.8.

## Troubleshooting
- Permission/Raw socket errors:
  - Windows: run PowerShell as Administrator to enable Scapy/raw sockets.
  - Without admin, the app still works using Windows ICMP API fallback.
- “No libpcap provider available” warning:
  - Install Npcap on Windows for advanced sniffing (not required for basic ping).
- Timeouts to public hosts:
  - Firewalls or networks may block ICMP. Try 8.8.8.8 or your default gateway.
- Graph not updating:
  - Ensure matplotlib is installed via requirements.txt. The app gracefully disables plotting if unavailable.
- Dependencies:
  - Activate your venv and run: pip install -r requirements.txt

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
Maintainer: Prosenjit Mondol  
GitHub: https://github.com/pronad1  
Email: prosenjit1156@gmail.com
