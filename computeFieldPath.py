# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

import json
import numpy as np
import matplotlib.path as path
from constants import *

# Load in data from custom user specification
with open (ROOM_BOUNDARY_OUTPUT, 'r') as f:
    ROOM_BOUNDARY = json.load(f)
with open(ROOM_OBSTACLES_OUTPUT, 'r') as f: 
    ROOM_OBSTACLES = json.load(f)
with open(LOCATION_OUTPUT, 'r') as f: 
    START_LOCATION, GOAL_LOCATION = json.load(f)

# Organize the boundary into a polygon data structure
BOUNDARY  = path.Path(ROOM_BOUNDARY)
OBSTACLES = [path.Path(obs) for obs in ROOM_OBSTACLES]

MAP = [[0 for x in range(WINDOW_LENGTH)] for y in WINDOW_LENGTH]
out = 0.0
in_ = 0.0
for i_ind, i in enumerate(np.arange(-WINDOW_MAX_SIZE / 2.0, WINDOW_MAX_SIZE / 2.0, DELTA)):
    MAP.append([])
    for j_ind, j in enumerate(np.arange(-WINDOW_MAX_SIZE / 2.0, WINDOW_MAX_SIZE / 2.0, DELTA)):
        if BOUNDARY.contains_point((i,j)):
            MAP[i_ind].append(0)
        else: 
            MAP[i_ind].append(1)
        