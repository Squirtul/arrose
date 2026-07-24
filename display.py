
# helpful functions/proc related to grids

from config import RING_LENGTH, NUM_RINGS, NUM_SECTORS

# makes the grid based on selected sector and ring numbers !!sector number is flexible here, but not in bearing calculations. need to fix this before you change sector number!!
def createGrid():
    return [[0 for _ in range(NUM_SECTORS)] for _ in range(NUM_RINGS)]

# find an acfts ring based on its eta. since acft closer than 25m arent shown, the innermost ring is given an unfair disadvantage.. maybe some leeway for it later
def getRing(eta_minutes):
    ring = int(eta_minutes // RING_LENGTH)
    if ring >= NUM_RINGS:
        # ring cap
        return None
    return ring

def addAircraft(grid, ring, sector):
    grid[ring][sector] += 1