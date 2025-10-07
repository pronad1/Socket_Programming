#!/usr/bin/env python3
"""
Quick Project Validation Script
Fast validation of all socket programming projects and assignments

This script provides:
- Quick health checks for all projects
- Assignment validation
- Video streaming system checks
- Network connectivity tests
- Dependency verification

Usage:
    python validate_project.py              # Check everything
    python validate_project.py --assignment # Check only assignments
    python validate_project.py --streaming  # Check only video streaming
    python validate_project.py --quick      # Quick check only

Author: Prosenjit Mondol
Date: October 2025
Project: Socket Programming Laboratory
"""

import os
import sys
import socket
import subprocess
import time
from typing import Dict, List, Tuple


class ProjectValidator:
    """Quick validation for all projects"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results = []
        
    def validate_all(self) -> bool:
        """Validate all projects"""
        print("🔍 Socket Programming Project Validation")
        print("=" * 50)
        
        checks = [
            ("Project Structure", self.check_project_structure),
            ("Python Dependencies", self.check_python_dependencies),
            ("Network Connectivity", self.check_network),
            ("Assignment Projects", self.check_assignments),
            ("Video Streaming System", self.check_video_streaming),
            ("Sample Files", self.check_sample_files)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"\n📋 {check_name}")
            print("-" * 30)
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ Error in {check_name}: {e}")
                all_passed = False
        
        self.print_summary(all_passed)
        return all_passed
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
        if details:
            print(f"      {details}")
        
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def check_project_structure(self) -> bool:
        """Check if all required directories exist"""
        required_dirs = [
            "src/python/simple_socket",
            "src/video_streaming/server",
            "src/video_streaming/client", 
            "assignments/udp_streaming"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = os.path.join(self.base_dir, dir_path)
            exists = os.path.exists(full_path)
            self.log_result(f"Directory: {dir_path}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def check_python_dependencies(self) -> bool:
        """Check Python and required modules"""
        modules_to_check = [
            'socket', 'threading', 'tkinter', 'json', 'struct', 'subprocess'
        ]
        
        # Check Python version
        python_version = sys.version_info
        version_ok = python_version.major >= 3 and python_version.minor >= 7
        self.log_result("Python 3.7+", version_ok, f"Found: Python {python_version.major}.{python_version.minor}")
        
        # Check modules
        all_modules_ok = True
        for module in modules_to_check:
            try:
                __import__(module)
                self.log_result(f"Module: {module}", True)
            except ImportError:
                self.log_result(f"Module: {module}", False, "Not available")
                all_modules_ok = False
        
        return version_ok and all_modules_ok
    
    def check_network(self) -> bool:
        """Check network connectivity"""
        # Test socket creation
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.close()
            self.log_result("TCP Socket Creation", True)
            tcp_ok = True
        except Exception as e:
            self.log_result("TCP Socket Creation", False, str(e))
            tcp_ok = False
        
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.close()
            self.log_result("UDP Socket Creation", True)
            udp_ok = True
        except Exception as e:
            self.log_result("UDP Socket Creation", False, str(e))
            udp_ok = False
        
        # Test localhost binding
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('localhost', 0))  # Bind to any available port
            port = test_socket.getsockname()[1]
            test_socket.close()
            self.log_result("Localhost Binding", True, f"Test port: {port}")
            bind_ok = True
        except Exception as e:
            self.log_result("Localhost Binding", False, str(e))
            bind_ok = False
        
        return tcp_ok and udp_ok and bind_ok
    
    def check_assignments(self) -> bool:
        """Check assignment projects"""
        # Check UDP Streaming Assignment
        udp_assignment_dir = os.path.join(self.base_dir, "assignments", "udp_streaming")
        
        if not os.path.exists(udp_assignment_dir):
            self.log_result("UDP Streaming Assignment", False, "Directory not found")
            return False
        
        required_files = [
            "streaming_server.py",
            "streaming_client.py", 
            "test_streaming.py",
            "quick_test.py"
        ]
        
        all_files_exist = True
        for file_name in required_files:
            file_path = os.path.join(udp_assignment_dir, file_name)
            exists = os.path.exists(file_path)
            self.log_result(f"Assignment file: {file_name}", exists)
            if not exists:
                all_files_exist = False
        
        # Try to run quick test
        if all_files_exist:
            try:
                result = subprocess.run(
                    [sys.executable, "quick_test.py"],
                    cwd=udp_assignment_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.log_result("UDP Assignment Functionality", True, "Quick test passed")
                else:
                    self.log_result("UDP Assignment Functionality", False, "Quick test failed")
                    all_files_exist = False
            except subprocess.TimeoutExpired:
                self.log_result("UDP Assignment Functionality", False, "Test timeout")
                all_files_exist = False
            except Exception as e:
                self.log_result("UDP Assignment Functionality", False, str(e))
                all_files_exist = False
        
        return all_files_exist
    
    def check_video_streaming(self) -> bool:
        """Check video streaming system"""
        streaming_dir = os.path.join(self.base_dir, "src", "video_streaming")
        
        if not os.path.exists(streaming_dir):
            self.log_result("Video Streaming System", False, "Directory not found")
            return False
        
        # Check required components
        components = {
            "server/video_server.py": "Server implementation",
            "client/video_client.py": "Client implementation",
            "protocols/rtsp_protocol.py": "RTSP protocol",
            "protocols/rtp_protocol.py": "RTP protocol",
            "utils/video_utils.py": "Utilities",
            "start_streaming.py": "Launcher script"
        }
        
        all_components_ok = True
        for component_path, description in components.items():
            full_path = os.path.join(streaming_dir, component_path)
            exists = os.path.exists(full_path)
            self.log_result(f"Video streaming: {description}", exists)
            if not exists:
                all_components_ok = False
        
        # Try to import modules
        if all_components_ok:
            sys.path.insert(0, streaming_dir)
            try:
                from protocols.rtsp_protocol import RTSPParser
                from protocols.rtp_protocol import RTPSession
                from utils.video_utils import QualityProfileManager
                self.log_result("Video Streaming Imports", True, "All modules importable")
            except ImportError as e:
                self.log_result("Video Streaming Imports", False, str(e))
                all_components_ok = False
            finally:
                sys.path.remove(streaming_dir)
        
        return all_components_ok
    
    def check_sample_files(self) -> bool:
        """Check sample files"""
        # Check if sample media files exist or can be created
        media_dir = os.path.join(self.base_dir, "src", "video_streaming", "media")
        
        if not os.path.exists(media_dir):
            self.log_result("Media Directory", False, "Not found")
            return False
        
        create_script = os.path.join(media_dir, "create_samples.py")
        if os.path.exists(create_script):
            self.log_result("Sample Creation Script", True)
            
            # Check if samples already exist
            sample_files = ['sample_480p.mp4', 'sample_720p.mp4', 'sample_1080p.mp4']
            existing_samples = [f for f in sample_files if os.path.exists(os.path.join(media_dir, f))]
            
            if existing_samples:
                self.log_result("Sample Media Files", True, f"Found: {len(existing_samples)} files")
            else:
                self.log_result("Sample Media Files", False, "No samples found (run create_samples.py)")
            
            return True
        else:
            self.log_result("Sample Creation Script", False, "Not found")
            return False
    
    def print_summary(self, all_passed: bool):
        """Print validation summary"""
        print("\n" + "🏁" + "=" * 48 + "🏁")
        print("  VALIDATION SUMMARY")
        print("🏁" + "=" * 48 + "🏁")
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"📊 Results: {passed}/{total} checks passed")
        
        if all_passed:
            print("🎉 ALL CHECKS PASSED!")
            print("   Your socket programming projects are ready to use.")
            print()
            print("🚀 Quick Start Options:")
            print("   • UDP Assignment:     cd assignments/udp_streaming && python quick_test.py")
            print("   • Video Streaming:    cd src/video_streaming && python start_streaming.py all")
            print("   • Simple Sockets:     cd src/python/simple_socket && python server.py")
        else:
            print("⚠️  SOME CHECKS FAILED")
            failed_tests = [r for r in self.results if not r['passed']]
            print(f"   Please fix the following {len(failed_tests)} issues:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print("🎬" + "=" * 48 + "🎬")


def quick_health_check():
    """Very quick health check"""
    print("⚡ Quick Health Check")
    print("-" * 20)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check critical files
    critical_files = [
        "src/python/simple_socket/server.py",
        "assignments/udp_streaming/streaming_server.py",
        "src/video_streaming/server/video_server.py"
    ]
    
    all_good = True
    for file_path in critical_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_good = False
    
    # Quick Python check
    try:
        import socket, threading, tkinter
        print("   ✅ Python modules")
    except ImportError:
        print("   ❌ Python modules")
        all_good = False
    
    if all_good:
        print("   🎉 Basic health check passed!")
    else:
        print("   ⚠️ Issues found - run full validation")
    
    return all_good


def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--quick":
            return quick_health_check()
        elif arg == "--assignment":
            validator = ProjectValidator()
            return validator.check_assignments()
        elif arg == "--streaming":
            validator = ProjectValidator()
            return validator.check_video_streaming()
        elif arg in ["--help", "-h"]:
            print("📖 Project Validation Script")
            print()
            print("Usage:")
            print("   python validate_project.py              # Full validation")
            print("   python validate_project.py --quick      # Quick check")
            print("   python validate_project.py --assignment # Check assignments only")
            print("   python validate_project.py --streaming  # Check video streaming only")
            print("   python validate_project.py --help       # Show this help")
            return True
    
    # Run full validation
    validator = ProjectValidator()
    return validator.validate_all()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)