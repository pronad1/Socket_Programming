# ICMP Pinger Lab (Python)

A simple ICMP ping application with a GUI client and an optional echo server. The client sends ICMP Echo Requests, measures round-trip time (RTT), and reports per-ping results and summary statistics.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)

## Overview
This lab includes:
- A GUI-based ICMP Ping Client for measuring RTT and packet loss.
- An optional ICMP Echo Server that replies to Echo Requests (with optional random delay).

## Features
- GUI controls: target host, count, timeout
- Per-ping RTT and timeout reporting
- Summary stats: sent/received, loss, average RTT
- Optional echo server with random delay simulation
- Threaded client for a responsive UI

## Prerequisites
- Python 3.8+ (Tkinter included in standard Python on Windows)
- Dependencies (see requirements.txt):
  - scapy
  - numpy, matplotlib (optional)
- Windows:
  - Run the scripts in an elevated PowerShell (Administrator) for raw sockets
  - Optional: Npcap (https://npcap.com/) for advanced sniffing

## Installation
```bash
# (optional) create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## Project Structure
```
d:\Languages\Socket_Programming\
├── README.md
├── requirements.txt
├── icmp_pinger_gui.py        # GUI ping client
└── icmp_ping_server.py       # Optional echo server
```

## Usage

### Run the GUI Ping Client
```bash
python d:\Languages\Socket_Programming\icmp_pinger_gui.py
```
- Enter Target Host (e.g., 8.8.8.8 or localhost), Count, Timeout (s)
- Click Start Ping to see per-ping results and final statistics

### (Optional) Run the Echo Server
```bash
# Use an elevated shell (Administrator on Windows / sudo on Linux)
python d:\Languages\Socket_Programming\icmp_ping_server.py
```
- Replies to ICMP Echo Requests
- May add a small random delay to simulate network variability

## Troubleshooting
- Permission denied / raw socket errors:
  - Windows: run PowerShell as Administrator
  - Linux/Mac: use sudo
- “No libpcap provider available” warning:
  - Install Npcap on Windows if using sniffing; GUI client works without it
- Timeouts to public hosts:
  - ICMP may be blocked by firewalls; try 8.8.8.8 or your gateway
- Import/module errors:
  - Ensure venv is active and run: `pip install -r requirements.txt`

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
Maintainer: Prosenjit Mondol  
GitHub: https://github.com/pronad1  
Email: prosenjit1156@gmail.com
