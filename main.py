import pathlib
from datetime import datetime, timezone

from vatsim import get_vatsim_data
from airports import AIRPORTS
from config import AIRPORT, NUM_RINGS
from airport_positions import AIRPORT_POSITIONS
from controllers import controllerCount

from distance import distance_to_airport
from bearing import bearing_from_airport
from bearing import get_sector

from display import createGrid
from display import getRing
from display import addAircraft

WEB_DIR = pathlib.Path(__file__).resolve().parent / "web"
LOG_PATH = WEB_DIR / "status.log"
LAST_AIRPORT_PATH = WEB_DIR / "last_airport.txt"
MAX_LOG_LINES = 100

WEB_DIR.mkdir(exist_ok=True)

print()

grid = createGrid()

arptLoc = AIRPORTS[AIRPORT]

vatsim_data = get_vatsim_data()
aircraft = vatsim_data["pilots"]
controllers = vatsim_data["controllers"]

aircraft_count = 0

shown = []
excluded_close_or_slow = []
excluded_out_of_range = []

for plane in aircraft:

    flight_plan = plane.get("flight_plan")
    if not flight_plan:
        continue
    if flight_plan["arrival"] != AIRPORT:
        continue

    distance = distance_to_airport(plane, arptLoc)

    speed = plane["groundspeed"]

    if speed < 100 or distance < 24:
        excluded_close_or_slow.append({
            "callsign": plane["callsign"],
            "distance": distance,
            "speed": speed,
        })
        continue

    eta = (distance / speed) * 60
    bearing = bearing_from_airport(arptLoc, plane)
    ring = getRing(eta)

    if ring is None or ring >= NUM_RINGS:
        excluded_out_of_range.append({
            "callsign": plane["callsign"],
            "distance": distance,
            "eta": eta,
        })
        continue

    sector = get_sector(bearing)

    shown.append({
        "callsign": plane["callsign"],
        "distance": distance,
        "speed": speed,
        "eta": eta,
        "bearing": bearing,
        "sector": sector,
        "ring": ring,
    })

    addAircraft(grid, ring, sector)
    aircraft_count += 1


report_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
total_relevant = len(shown) + len(excluded_close_or_slow) + len(excluded_out_of_range)

print("=" * 60) # log created for my own  troubleshooting. might as well keep it
print(f"REPORT - {report_time} - {AIRPORT}")
print("=" * 60)
print(f"Total acft with flight plan to {AIRPORT}: {total_relevant}")
print()

print(f"SHOWN ({len(shown)}):")
if shown:
    for a in shown:
        print(
            f"  {a['callsign']:<10}"
            f" dist={a['distance']:6.1f}nm"
            f" spd={a['speed']:4.0f}kt"
            f" eta={a['eta']:5.1f}min"
            f" bearing={a['bearing']:5.1f}"
            f" sector={a['sector']}"
            f" ring={a['ring']}"
        )
else:
    print("  (none)")
print()
print("=" * 60)
print()

for row in grid:
    print(row)

from draw import draw_grid
shifted = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid) + 1)]

for r in range(len(grid)):
    for s in range(len(grid[0])):
        shifted[r + 1][s] = grid[r][s]

grid = shifted

online_categories = controllerCount(
    controllers,
    AIRPORT_POSITIONS.get(AIRPORT, {}),
)

draw_grid(grid, online_categories)

# web status - can be monitored on ip with port 8080
last_airport = None
if LAST_AIRPORT_PATH.exists():
    last_airport = LAST_AIRPORT_PATH.read_text().strip()

airport_changed = last_airport is not None and last_airport != AIRPORT
LAST_AIRPORT_PATH.write_text(AIRPORT)

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
line = f"{timestamp}  |  {AIRPORT}  |  {aircraft_count} aircraft"
if airport_changed:
    line += "  |  airport changed"

existing_lines = []
if LOG_PATH.exists():
    existing_lines = LOG_PATH.read_text().splitlines()

new_lines = [line] + existing_lines
new_lines = new_lines[:MAX_LOG_LINES]

LOG_PATH.write_text("\n".join(new_lines) + "\n")
