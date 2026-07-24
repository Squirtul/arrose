
# returns number of controllers of each type as a dict

sfxs = ["DEL", "GND", "TWR", "APP", "ACC"]

def controllerCount(controllers, position_lists):
    online = {c["callsign"] for c in controllers}
    counts = {}
    for category in sfxs:
        positions = position_lists.get(category, [])
        counts[category] = sum(1 for pos in positions if pos in online)
    return counts

    # currently anything over 3 is irrelevant.. could always cap it at 3