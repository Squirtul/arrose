@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo               Arrose Remote Installer                    
echo ========================================================
echo 
echo Per SSH requirements, you'll be prompted for your password twice.
echo.

set /p PI_IP="Enter your Raspberry Pi IP address: "

if "%PI_IP%"=="" (
    echo [ERROR] IP address cannot be empty!
    pause
    exit /b
)

set /p PI_USER="Enter your Pi username [default: pi]: "
if "%PI_USER%"=="" set PI_USER=pi

echo.
echo --------------------------------------------------------
echo Starting transfer to %PI_USER%@%PI_IP%...
echo --------------------------------------------------------
echo.

:: Transfer directly to /home/pi/arrose
scp -r "%~dp0*" %PI_USER%@%PI_IP%:/home/%PI_USER%/arrose

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] File transfer failed. Check your IP, username, or network connection.
    pause
    exit /b
)

echo.
echo --------------------------------------------------------
echo Files transferred successfully!
echo Starting remote installation script...
echo --------------------------------------------------------
echo.

:: Move into /home/pi/arrose first, then run installer.py
ssh -t %PI_USER%@%PI_IP% "cd /home/%PI_USER%/arrose && python3 installer.py"

echo.
echo ========================================================
echo Installation process finished!
echo ========================================================
pause