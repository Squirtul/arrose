#!/bin/bash

echo "========================================================"
echo "               Arrose Remote Installer                  "
echo "========================================================"
echo ""
echo "Per SSH requirements, you'll be prompted for your password twice."
echo ""

# Prompt for IP address
read -p "Enter your Raspberry Pi IP address: " PI_IP

if [ -z "$PI_IP" ]; then
    echo "[ERROR] IP address cannot be empty!"
    exit 1
fi

# Prompt for username with default fallback
read -p "Enter your Pi username [default: pi]: " PI_USER
PI_USER=${PI_USER:-pi}

echo ""
echo "--------------------------------------------------------"
echo "Starting transfer to $PI_USER@$PI_IP..."
echo "--------------------------------------------------------"
echo ""

# Get current script directory in Linux
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Transfer files
scp -r "$SCRIPT_DIR/"* "$PI_USER@$PI_IP:/home/$PI_USER/arrose"

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] File transfer failed. Check your IP, username, or network connection."
    exit 1
fi

echo ""
echo "--------------------------------------------------------"
echo "Files transferred successfully!"
echo "Starting remote installation script..."
echo "--------------------------------------------------------"
echo ""

# Execute remote script
ssh -t "$PI_USER@$PI_IP" "cd /home/$PI_USER/arrose && python3 installer.py"

echo ""
echo "========================================================"
echo "Installation process finished!"
echo "========================================================"
