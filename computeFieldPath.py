# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

import json
import sys
import numpy as np
import matplotlib.path as path
import matplotlib.pyplot as plt
import seaborn as sns
import time
from getEnvironment import euclideanDistance
from constants import *

startTime = time.time() # Start the timer

# Load in data from custom user specification
with open (ROOM_BOUNDARY_OUTPUT, 'r') as f:
    ROOM_BOUNDARY = json.load(f)
with open(ROOM_OBSTACLES_OUTPUT, 'r') as f: 
    ROOM_OBSTACLES = json.load(f)
with open(LOCATION_OUTPUT, 'r') as f: 
    (START_X, START_Y), (GOAL_X, GOAL_Y) = json.load(f)
print('Read in environment data...')

# Organize the boundary into a polygon data structure
BOUNDARY  = path.Path(ROOM_BOUNDARY)
OBSTACLES = [path.Path(obs) for obs in ROOM_OBSTACLES]

# Create a matrix to store the potential
WINDOW_SIDE = np.arange(-WINDOW_MAX_SIZE / 2.0, WINDOW_MAX_SIZE / 2.0, D)
CELLS = [[0 for x in WINDOW_SIDE] for y in WINDOW_SIDE]
MARKED = [[False for x in WINDOW_SIDE] for y in WINDOW_SIDE]
TOTAL_CELLS = 1.0 * len(CELLS) * len(CELLS[0])

# Need to fill up queue with points to mark
QUEUE = []

def getQueueIndexForPoint(p):
    '''
    Returns index in QUEUE associated with a given point, p.
    '''
    x, y = p
    row = len(MARKED) - int((y + WINDOW_MAX_SIZE / 2) / D) - 1
    col = int((x + WINDOW_MAX_SIZE / 2) / D)
    return row, col

def inQueue(p):
    '''
    Returns True if the point is already in the queue for any level.
    '''
    return p in [pt for (pt, level) in QUEUE]

def addPointsOnInterior(p1, p2):
    '''
    This function computes the equation of the line connecting p1 and p2. It 
    then adds all of the points D to the interior of the line to QUEUE so 
    that they can be marked.
    '''
    global QUEUE
    (x1, y1), (x2, y2) = p1, p2
    if (x2 - x1) == 0: 
        m = sys.maxint
    else:
        m = (y2 - y1) / (x2 - x1)

    # Equation of the line connecting p1 and p2
    def y(x):
        return m * (x - x1) + y1

    leftX, rightX = (x1, x2) if x1 < x2 else (x2, x1)
    linePoints = [(x, y(x)) for x in np.arange(leftX, rightX, D)]
    for (x, y) in linePoints:
        # Define points around the point on the line
        pW  = (x - D, y)
        pE  = (x + D, y)
        pNW = (x - D, y + D)
        pSW = (x - D, y - D)
        pNE = (x + D, y + D)
        pSE = (x + D, y - D)

        # See which side(s) is contained in BOUNDARY
        pW_  = BOUNDARY.contains_point(pW), pW
        pE_  = BOUNDARY.contains_point(pE), pE
        pNW_ = BOUNDARY.contains_point(pNW), pNW
        pSW_ = BOUNDARY.contains_point(pSW), pSW
        pNE_ = BOUNDARY.contains_point(pNE), pNE
        pSE_ = BOUNDARY.contains_point(pSE), pSE

        # Find exact cells we need to 
        ps = [pW_, pE_, pNW_, pSW_, pNE_, pSW_]

        # Add unmarked cells around the current cell to the queue
        for p_in, p in ps: 
            row, col = getQueueIndexForPoint(p)
            if p_in and not MARKED[row][col] and not inQueue(p):
                QUEUE.append((p, 1))

def attractiveGradient(curX, curY):
    '''
    Computes and returns the attractive potential at the current location.
    '''
    return [-K * (curX - GOAL_X), -K * (curY - GOAL_Y)]

def repulsiveGradient(curX, curY):
    '''
    Computes and returns the repulsive potential at the current location. It 
    simply looks at the locations around the current location and retuns the 
    direction with the highest value, the direction that is the most clear of 
    obstacles.
    '''
    # Define points in every direction of current point
    pN  = curX, curY + D
    pS  = curX, curY - D
    pW  = curX - D, curY
    pE  = curX + D, curY
    pNW = curX - D, curY + D
    pSW = curX - D, curY - D
    pNE = curX + D, curY + D
    pSE = curX + D, curY - D
    ps  = [pN, pS, pW, pE, pNW, pSW, pNE, pSE]

    # Find safest neighbor to jump to
    maxNeighbor = -1
    maxPotential = -1
    for p in ps:
        i, j = getQueueIndexForPoint(p)
        # Check and make sure we have a valid location
        if not MARKED[i][j]:
            continue
        curPotential = CELLS[i][j]
        if curPotential > maxPotential:
            maxPotential = curPotential
            maxNeighbor = p

    # Set repulsive gradient going towards safest neighbor
    maxX, maxY = maxNeighbor
    return [-G * (curX - maxX), -G * (curY - maxY)]

# Identify points on the interior of the boundary
p1 = ROOM_BOUNDARY[0]
for p2 in ROOM_BOUNDARY[1:]:
    addPointsOnInterior(p1, p2)
    p1 = p2 # Move p1 forward
print('Computed points on interior of environment boundary...')

# Identify points on exterior of each obstacle and interior of boundary
for obs in ROOM_OBSTACLES:
    p1 = obs[0]
    for p2 in obs[1:]:
        addPointsOnInterior(p1, p2)
        p1 = p2 # Move p1 forward
print('Computed points on immediate exterior of each obstacle...')

# Mark all the points that aren't in the boundary
numMarked = 0
for x in WINDOW_SIDE:
    for y in WINDOW_SIDE:
        row, col = getQueueIndexForPoint((x, y))
        # If point is not within the boundary of the environment, mark it
        if not BOUNDARY.contains_point((x, y)):
            MARKED[row][col] = True
            numMarked += 1
        else: 
            for obs in OBSTACLES:
                # If point is inside one of the obstacles within environment
                # boundary, mark it
                if obs.contains_point((x, y)):
                    MARKED[row][col] = True
                    numMarked += 1
                    continue
print('Marked all unreachable points in the environment...')

# Continuously mark all the cells and set their potential levels until we've 
# marked every cell
reachableToMark = TOTAL_CELLS - numMarked
numMarked = 0
while len(QUEUE) != 0: 
    # Get celll off the queue
    cell, l = QUEUE.pop(0)
    cellX, cellY = cell

    # Increase the level of the cell
    row, col = getQueueIndexForPoint(cell)
    if MARKED[row][col]:
        continue

    CELLS[row][col] = l
    MARKED[row][col] = True
    numMarked += 1

    # Define points around current point
    pN  = cellX, cellY + D
    pS  = cellX, cellY - D
    pW  = cellX - D, cellY
    pE  = cellX + D, cellY
    pNW = cellX - D, cellY + D
    pSW = cellX - D, cellY - D
    pNE = cellX + D, cellY + D
    pSE = cellX + D, cellY - D
    ps  = [pN, pS, pW, pE, pNW, pSW, pNE, pSE]

    # Add unmarked cells around the current cell to the queue
    for p in ps: 
        row, col = getQueueIndexForPoint(p)
        if not MARKED[row][col] and not inQueue(p):
            QUEUE.append((p, l + 1))

    per = str(round(numMarked / reachableToMark, 3) * 100) 
    pro = per + '%. ' + str(len(QUEUE)) + ' cells left in queue'
    m = ('Marking reachable points with their potential. ' + pro + '...    \r')
    sys.stdout.write(m)
    sys.stdout.flush()

curX, curY = START_X, START_Y
curRow, curCol = getQueueIndexForPoint((curX, curY))
pathXs, pathYs = [curCol], [curRow]
# While we're sufficiently far away from goal location
while euclideanDistance(curX, curY, GOAL_X, GOAL_Y) >= D:
    # Compute attractive gradient at this point
    attGradX, attGradY = attractiveGradient(curX, curY)

    # Compute repulsive gradient at this point
    repGradX, repGradY = repulsiveGradient(curX, curY)

    # Compute current gradient from attractive and repulsive gradients
    curGradX = attGradX + repGradX
    curGradY = attGradY + repGradY

    # Move to the next location based on gradient
    curX = curX + (D * curGradX)
    curY = curY + (D * curGradY)

    # Get cell indices for current location
    curRow, curCol = getQueueIndexForPoint((curX, curY))
    pathXs.append(curCol)
    pathYs.append(curRow)

    # Report to console progress of path finding...

print('Computed path from start location to goal...')

# Create heatmap
hm = sns.heatmap(CELLS, cmap='YlOrRd', cbar=False, 
                 xticklabels=False, yticklabels=False)
hm.set_title('Wave Front Potential')
plt.plot(pathXs, pathYs, linewidth=5)
# plt.scatter([START_X], [START_Y], s=100, c='b')
# plt.scatter([GOAL_X], [GOAL_Y], s=100, c='b')
plt.savefig('wavefront_potential.png')
print('Generated heatmap of field and path from start to goal...')

elapsedTime = str(round(time.time() - startTime, 3))
print('\n[SUCCESS]: ' + elapsedTime + ' seconds...\n')

plt.show()



