
# changes selected airport

import pathlib
import re
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent
CONFIG_PATH = BASE / "config.py"

sys.path.insert(0, str(BASE))
from airports import AIRPORTS


def list_airports():
    print("Available airports:", ", ".join(sorted(AIRPORTS)))


def main():
    if len(sys.argv) != 2:
        print("Usage: set-airport ICAO")
        list_airports()
        sys.exit(1)

    icao = sys.argv[1].strip().upper()

    if icao not in AIRPORTS:
        print(f"Unknown airport '{icao}'.")
        list_airports()
        sys.exit(1)

    text = CONFIG_PATH.read_text()
    new_text, count = re.subn(
        r'^AIRPORT\s*=\s*".*"$',
        f'AIRPORT = "{icao}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    if count == 0:
        print("Could not find an 'AIRPORT = \"...\"' line in config.py - no changes made.")
        sys.exit(1)

    CONFIG_PATH.write_text(new_text)
    print(f"Airport set to {icao}.")

    # Trigger redraw as soon as change made
    result = subprocess.run(
        ["sudo", "systemctl", "start", "arrose-generate.service"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Triggered an immediate refresh.")
    else:
        print("Config updated, but could not trigger a refresh automatically:")
        print(result.stderr.strip())
        print("It will pick up within a minute anyway.") # yeah its almost always bad if this happens. syntax error or corruption in the generate service most of the time

if __name__ == "__main__":
    main()
