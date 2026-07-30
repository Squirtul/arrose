import re

# return online controllers

sfxs = ["DEL", "GND", "TWR", "APP", "ACC"]


def normalise(callsign):
    return re.sub(r"_+", "_", callsign) # clear relief callsigns. eg "EFHK__DEL" > "EFHK_DEL"


def controllerCount(controllers, position_lists):
    online = {normalise(c["callsign"]) for c in controllers}
    counts = {}
    for category in sfxs:
        positions = position_lists.get(category, [])
        counts[category] = sum(1 for pos in positions if normalise(pos) in online)
    return counts