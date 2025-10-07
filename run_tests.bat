@echo off
REM Windows Batch Script for Testing Socket Programming Projects
REM Quick test runner for all components

echo 🎬 Socket Programming Projects - Test Runner
echo ================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo 🔍 Running Quick Validation...
python validate_project.py --quick
if errorlevel 1 (
    echo ❌ Quick validation failed. Running full validation...
    python validate_project.py
    if errorlevel 1 (
        echo ❌ Validation failed. Please fix issues before testing.
        pause
        exit /b 1
    )
)

echo.
echo 📋 Choose test option:
echo 1. Test UDP Streaming Assignment
echo 2. Test Video Streaming System  
echo 3. Run All Tests
echo 4. Quick Health Check Only
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto test_udp
if "%choice%"=="2" goto test_video
if "%choice%"=="3" goto test_all
if "%choice%"=="4" goto health_check
if "%choice%"=="5" goto end
goto invalid_choice

:test_udp
echo.
echo 🚀 Testing UDP Streaming Assignment...
cd assignments\udp_streaming
python quick_test.py
cd "%PROJECT_ROOT%"
goto end

:test_video
echo.
echo 🎬 Testing Video Streaming System...
cd src\video_streaming
python run_project_tests.py
cd "%PROJECT_ROOT%"
goto end

:test_all
echo.
echo 🧪 Running All Tests...
echo.
echo 📡 UDP Assignment Test:
cd assignments\udp_streaming
python quick_test.py
cd "%PROJECT_ROOT%"
echo.
echo 🎬 Video Streaming Test:
cd src\video_streaming
python run_project_tests.py
cd "%PROJECT_ROOT%"
echo.
echo ✅ All tests completed!
goto end

:health_check
echo.
echo ⚡ Quick Health Check...
python validate_project.py --quick
goto end

:invalid_choice
echo ❌ Invalid choice. Please enter 1-5.
pause
goto end

:end
echo.
echo 🏁 Testing completed.
pause