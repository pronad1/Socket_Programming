#!/bin/bash
# Linux/Mac Shell Script for Testing Socket Programming Projects
# Quick test runner for all components

echo "🎬 Socket Programming Projects - Test Runner"
echo "================================================"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "🔍 Running Quick Validation..."
python3 validate_project.py --quick
if [ $? -ne 0 ]; then
    echo "❌ Quick validation failed. Running full validation..."
    python3 validate_project.py
    if [ $? -ne 0 ]; then
        echo "❌ Validation failed. Please fix issues before testing."
        exit 1
    fi
fi

echo ""
echo "📋 Choose test option:"
echo "1. Test UDP Streaming Assignment"
echo "2. Test Video Streaming System"
echo "3. Run All Tests"
echo "4. Quick Health Check Only"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Testing UDP Streaming Assignment..."
        cd assignments/udp_streaming
        python3 quick_test.py
        cd "$PROJECT_ROOT"
        ;;
    2)
        echo ""
        echo "🎬 Testing Video Streaming System..."
        cd src/video_streaming
        python3 run_project_tests.py
        cd "$PROJECT_ROOT"
        ;;
    3)
        echo ""
        echo "🧪 Running All Tests..."
        echo ""
        echo "📡 UDP Assignment Test:"
        cd assignments/udp_streaming
        python3 quick_test.py
        cd "$PROJECT_ROOT"
        echo ""
        echo "🎬 Video Streaming Test:"
        cd src/video_streaming
        python3 run_project_tests.py
        cd "$PROJECT_ROOT"
        echo ""
        echo "✅ All tests completed!"
        ;;
    4)
        echo ""
        echo "⚡ Quick Health Check..."
        python3 validate_project.py --quick
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please enter 1-5."
        ;;
esac

echo ""
echo "🏁 Testing completed."