
# change selected airport, ish

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


def change_airport(icao):
    icao = (icao or "").strip().upper()

    if not icao:
        return False, "No airport code given."

    if icao not in AIRPORTS:
        return False, f"Unknown airport '{icao}'."

    text = CONFIG_PATH.read_text()
    new_text, count = re.subn(
        r'^AIRPORT\s*=\s*".*"$',
        f'AIRPORT = "{icao}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )

    if count == 0:
        return False, "Could not find an 'AIRPORT = \"...\"' line in config.py - no changes made."

    CONFIG_PATH.write_text(new_text)

    # re make the thingy when you change airport
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "start", "arrose-generate.service"],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return True, f"Airport set to {icao}, but could not trigger a refresh automatically: {exc}"

    if result.returncode == 0:
        return True, f"Airport set to {icao}."

    # yeah its almost always bad if this happens. syntax error or corruption in the generate service most of the time
    return True, f"Airport set to {icao}, but could not trigger a refresh automatically: {result.stderr.strip()}"


def main():
    if len(sys.argv) != 2:
        print("Usage: set-airport ICAO")
        list_airports()
        sys.exit(1)

    success, message = change_airport(sys.argv[1])
    print(message)

    if not success:
        list_airports()
        sys.exit(1)


if __name__ == "__main__":
    main()