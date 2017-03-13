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
print('\nRead in environment data...')

# Organize the boundary into a polygon data structure
BOUNDARY  = path.Path(ROOM_BOUNDARY)
OBSTACLES = [path.Path(obs) for obs in ROOM_OBSTACLES]

# Create a matrix to store the potential
WINDOW_SIDE = np.arange(-WINDOW_SIZE / 2.0, WINDOW_SIZE / 2.0, D)
CELLS = [[0 for x in WINDOW_SIDE] for y in WINDOW_SIDE]
MARKED = [[FREE_SPACE for x in WINDOW_SIDE] for y in WINDOW_SIDE]
TOTAL_CELLS = 1.0 * len(CELLS) * len(CELLS[0])

# Need to fill up queue with points to mark
QUEUE = []

def getIndexForPoint(p):
    '''
    Returns index in QUEUE associated with a given point, p.
    '''
    x, y = p
    row = len(MARKED) - int((y + WINDOW_SIZE / 2) / D) - 1
    col = int((x + WINDOW_SIZE / 2) / D)
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

        # Find exact cells we need to 
        ps = [pW, pE, pNW, pSW, pNE, pSW]

        # Add unmarked cells around the current cell to the queue
        for p in ps: 
            row, col = getIndexForPoint(p)
            if MARKED[row][col] == FREE_SPACE and not inQueue(p):
                QUEUE.append((p, 1))

# Mark all the points that aren't in the boundary
numMarked = 0
for x in WINDOW_SIDE:
    for y in WINDOW_SIDE:
        row, col = getIndexForPoint((x, y))
        # If point is not within the boundary of the environment, mark it
        if not BOUNDARY.contains_point((x, y)):
            MARKED[row][col] = BOUNDARY_SPACE
            numMarked += 1
        else: 
            for obs in OBSTACLES:
                # If point is inside one of the obstacles within environment
                # boundary, mark it
                if obs.contains_point((x, y)):
                    MARKED[row][col] = OBSTACLE_SPACE
                    numMarked += 1
                    continue
print('Marked all unreachable points in the environment...')

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

# Continuously mark all the cells and set their potential levels until we've 
# marked every cell
reachableToMark = TOTAL_CELLS - numMarked
numMarked = 0
while len(QUEUE) != 0: 
    # Get celll off the queue
    cell, l = QUEUE.pop(0)
    cellX, cellY = cell
    row, col = getIndexForPoint(cell)

    # Skip over this cell if it's in a boundary, obstacle, or has been visited
    if MARKED[row][col] in [BOUNDARY_SPACE, OBSTACLE_SPACE, VISITED_SPACE]:
        continue

    # Add level to this cell's entry and mark it as visited
    CELLS[row][col] = l
    MARKED[row][col] = VISITED_SPACE
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
        row, col = getIndexForPoint(p)
        if MARKED[row][col] == FREE_SPACE and not inQueue(p):
            QUEUE.append((p, l + 1))

    per = str(round(numMarked / reachableToMark, 3) * 100) 
    pro = per + '% (' + str(len(QUEUE)) + ')'
    m = ('Marking reachable points with their potential. ' + pro + '...    \r')
    sys.stdout.write(m)
    sys.stdout.flush()

print('')
# Start robot at start location given by user
curX, curY = START_X, START_Y

# Add the start location to the path
curRow, curCol = getIndexForPoint((curY, curX))
PATH_XS, PATH_YS = [], []

# Compute distance from current location to goal
curDist = euclideanDistance(curX, curY, GOAL_X, GOAL_Y)
totalDist = curDist

# Keep track of number of steps taken by robot
stepsTaken = 0

# While we're sufficiently far away from goal location or haven't taken 
# the maximum number of steps we allow before giving up
while curDist >= CLOSE_PATH_THRESHOLD and stepsTaken <= MAX_NUM_STEPS:
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

    maxScore, maxNeighbor, maxRow, maxCol = 0, 0, 0, 0
    for (pX, pY) in ps:
        # Get indices of data related to this point
        row, col = getIndexForPoint((pX, pY))

        # Skip points that are outside boundary of environment and points 
        # inside an obstacle
        if MARKED[row][col] == BOUNDARY_SPACE or \
           MARKED[row][col] == OBSTACLE_SPACE:
            continue

        # Skip points that are already in the path
        if (col, int(WINDOW_SIZE / D) - row) in zip(PATH_XS, PATH_YS):
            continue

        # Compute distance to goal from this point
        pDist = euclideanDistance(pX, pY, GOAL_X, GOAL_Y)
        distScore = K * (totalDist - pDist)

        # See what the potential value for this point is
        potentialScore = G * CELLS[row][col]

        # Score for this neighbor selection
        curScore = distScore + potentialScore

        # Update new maximum
        if curScore > maxScore:
            maxScore = curScore
            maxNeighbor = pY, pX
            maxRow, maxCol = row, col

    # Add new location to the path
    curY, curX = maxNeighbor
    PATH_XS.append(maxCol)
    PATH_YS.append(int(WINDOW_SIZE / D) - maxRow)

    # Report to console progress of path finding...
    curDist = euclideanDistance(curX, curY, GOAL_X, GOAL_Y)
    pro = str(round((totalDist - curDist) / curDist, 3)) + '% ' 
    pro += '(' + str(stepsTaken) + ' steps, ' + str(round(curDist, 3)) + ' away)'
    sys.stdout.write('Computing path from start to goal. ' + pro + '...\r')
    sys.stdout.flush()

    # Increment the number of total steps so that we don't keep looking for 
    # paths forever
    stepsTaken += 1

# Plot heatmap of repulsive potential
hm = sns.heatmap(CELLS, cmap='YlOrRd', cbar=False, 
                 xticklabels=False, yticklabels=False)
hm.set_title('Wave Front Potential and Path')

# Plot robot's path from start to goal
plt.plot(PATH_XS, PATH_YS, linewidth=3)

# Compute cells associated with start and goal locations, then plot start and 
# goal locations
startRow, startCol = getIndexForPoint((START_X, START_Y))
goalRow, goalCol = getIndexForPoint((GOAL_X, GOAL_Y))
plt.plot([startCol], [int(WINDOW_SIZE / D) - startRow], marker='o', color='green', markersize=5)
plt.plot([goalCol], [int(WINDOW_SIZE / D) - goalRow], marker='o', color='red', markersize=5)

# Save plot
plt.savefig('wavefront_potential.png')
print('\nGenerated heatmap of field and path from start to goal...')

elapsedTime = str(round(time.time() - startTime, 3))
print('\n[SUCCESS]: ' + elapsedTime + ' seconds...\n')

plt.show()



