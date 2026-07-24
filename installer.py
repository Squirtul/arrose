
# configures services and all other dependencies

import os
import subprocess
import sys
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_command(command, shell=False, ignore_errors=False):
    print(f"\n>>> Running: {command if isinstance(command, str) else ' '.join(command)}")
    try:
        subprocess.run(command, shell=shell, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"--- Error executing command ---")
        if not ignore_errors:
            print("Exiting installer due to failure.")
            sys.exit(1)

def main():
    print("=== Arrose Installer ===")
    print("Starting installation in 3 seconds...")
    time.sleep(3)

    print("\n--- Enabling SPI Interface ---")
    run_command(["sudo", "raspi-config", "nonint", "do_spi", "0"])

    print("\n--- Configuring Volatile Logging ---")
    run_command("sudo sed -i 's/.*Storage=.*/Storage=volatile/g' /etc/systemd/journald.conf", shell=True)
    
    run_command("grep -q '^RuntimeMaxUse=50M' /etc/systemd/journald.conf || echo 'RuntimeMaxUse=50M' | sudo tee -a /etc/systemd/journald.conf", shell=True)
    
    run_command("sudo rm -rf /var/log/journal", shell=True, ignore_errors=True)
    run_command(["sudo", "systemctl", "restart", "systemd-journald"])

    print("\n--- Installing APT Packages ---")
    run_command(["sudo", "apt", "update"])
    run_command(["sudo", "apt", "install", "-y", "python3-pip", "python3-pil", "python3-numpy", "p7zip-full"])

    print("\n--- Fixing GPIO & Installing PIP Packages ---")
    run_command(["pip3", "uninstall", "RPi.GPIO", "--break-system-packages", "-y"], ignore_errors=True)
    run_command(["pip3", "install", "--break-system-packages", "rpi-lgpio", "requests", "geopy", "spidev"])

    print("\n--- Setting up Waveshare LCD Library ---") # web was slow, so shipped directly now
    os.makedirs("/home/pi/arrose", exist_ok=True)

    print("\n--- Configuring Services ---")

    services = [
        "arrose-generate.service", 
        "arrose-generate.timer", 
        "arrose-spi-display.service", 
        "arrose-web.service", 
        "arrose-clear-log.service"
    ]
    
    for srv in services:
        run_command(f"sudo cp /home/pi/arrose/{srv} /etc/systemd/system/", shell=True, ignore_errors=True)

    run_command(["sudo", "systemctl", "daemon-reload"])
    run_command(["sudo", "systemctl", "enable", "--now", "arrose-generate.timer"], ignore_errors=True)
    run_command(["sudo", "systemctl", "enable", "--now", "arrose-spi-display.service"], ignore_errors=True)
    run_command(["sudo", "systemctl", "enable", "--now", "arrose-web.service"], ignore_errors=True)
    run_command(["sudo", "systemctl", "enable", "arrose-clear-log.service"], ignore_errors=True)

    print("\n--- Setting up CLI Commands ---")
    run_command(["sudo", "cp", "/home/pi/arrose/set-airport", "/usr/local/bin/set-airport"], ignore_errors=True)
    run_command("sudo chmod +x /usr/local/bin/set-airport /home/pi/arrose/set_airport.py", shell=True)
    run_command(["sudo", "cp", "/home/pi/arrose/arrose-sudoers", "/etc/sudoers.d/arrose"], ignore_errors=True)
    run_command(["sudo", "chmod", "440", "/etc/sudoers.d/arrose"], ignore_errors=True)

    print("\n=== Installation Complete! ===")
    run_command(["sudo", "reboot"])

if __name__ == "__main__":
    main()