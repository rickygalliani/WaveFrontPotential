# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

import turtle
import time
import json
import math
import matplotlib.path as path
from constants import *

def printWelcomeMsg():
    '''
    Prints a welcome message to the user.
    '''
    print('\n\n' + '-' * 65 + '\n')
    print(' ' * 28 + 'WELCOME' + ' ' * 28 + '\n')
    print('  This system computes a path from a start location to an end\n' +
          '  location within a user-specified, closed, polygonal environment\n' + 
          '  with polygonal obstacles in its interior. It uses the Wave \n' + 
          '  Front Potential Method to compute the motion plan.')
    print('\n\n' + '-' * 65 + '\n\n')

def printCustomizeInstructions():
    '''
    Prints instructions about how to customize the polygonal room to the 
    console.
    '''
    print('\n\n' + '-' * 65 + '\n')
    print(' ' * 13 + 'ENVIRONMENT CUSTOMIZATION INSTRUCTIONS' + ' ' * 13 + '\n')
    print('  1. Trace a polygonal environment boundary by clicking around \n' + 
          '     the graphics window that just popped up. Make sure to \n' + 
          '     make your boundary is a closed loop.\n')
    print('  2. Trace as many polygonal obstacles as you want within the \n' + 
          '     boundary by clicking in the locations of the vertices of \n' + 
          '     your desired obstacles. Like the boundary, make sure to \n' + 
          '     make each obstacle a closed loop.\n')
    print('  3. Once you\'re done tracing out obstacles within the \n' +
          '     environment, right-click.\n')
    print('  4. Click on the start location of your robot.\n')
    print('  5. Click on the goal location of your robot.\n')
    print('  6. Right-click to save your environment, boundaries, and \n' + 
          '     and start/goal locations.')
    print('\n\n' + '-' * 65 + '\n\n')

def euclideanDistance(p1x, p1y, p2x, p2y):
    '''
    Returns the Euclidean Distance between the two input points.
    '''
    return math.sqrt((p1x - p2x) ** 2 + (p1y - p2y) ** 2)

def mouseClick(x, y):
    '''
    Handle mouse-click events.
    '''
    # Global variables
    global ROOM_BOUNDARY, ROOM_OBSTACLES
    global DRAWING_BOUNDARY, DRAWING_OBSTACLE
    global START_X, START_Y
    global PICKED_START, PICKED_GOAL
    global START_LOCATION, GOAL_LOCATION
    global DONE

    if DONE: 
        return

    if PICKED_START:
        # Place user selection of start location on screen
        turtle.shapesize(1.0, 1.0)
        turtle.pensize(10)
        turtle.goto(x, y)
        turtle.pencolor('green')
        turtle.fillcolor('green')
        turtle.dot()
        START_LOCATION = (x, y)
        PICKED_START = False
        PICKED_GOAL = True
        return

    elif PICKED_GOAL:
        # Place user of selection of goal location on screen
        turtle.pencolor('red')
        turtle.fillcolor('red')
        turtle.goto(x, y)
        turtle.dot()
        GOAL_LOCATION = (x, y)
        DONE = True
        return

    # First location on this obstacle
    if (START_X, START_Y) == (0, 0): 
        START_X, START_Y = x, y

        # Start tracing out a shape that will be filled
        turtle.fill(True)

        if DRAWING_BOUNDARY:
            turtle.fillcolor('white')
            turtle.pencolor('blue')

    # User is done with boundary or current shape, indicated by double click
    else: 
        if euclideanDistance(x, y, START_X, START_Y) <= CLOSE_LOOP_THRESHOLD:
            if DRAWING_BOUNDARY:
                # Close up the loop
                turtle.goto(START_X, START_Y)
                ROOM_BOUNDARY.append((START_X, START_Y))
                turtle.fill(False)

                # Move the pen back to the center of the screen
                turtle.penup()
                START_X, START_Y = 0, 0
                turtle.goto(START_X, START_Y)

                # Reset flag because no longer drawing boundary
                DRAWING_BOUNDARY = False

            else: # DRAWING_OBSTACLE
                # Close up the loop
                turtle.goto(START_X, START_Y)
                ROOM_OBSTACLES[-1].append((START_X, START_Y))
                turtle.fill(False)

                # Move the pen back to the center of the screen
                turtle.penup()
                START_X, START_Y = 0, 0
                turtle.goto(START_X, START_Y)

                # Reset flag because no longer drawing obstacle
                DRAWING_OBSTACLE = False

            # Don't add this point to any data structures
            return

    if DRAWING_BOUNDARY:
        # Add current point to boundary
        ROOM_BOUNDARY.append((x, y)) 

        # Draw a point where the user clicked
        turtle.goto(x, y)
        turtle.pensize(4)
        turtle.pendown()
        turtle.dot()

    elif DRAWING_OBSTACLE:
        # Add current point to current obstacle
        ROOM_OBSTACLES[-1].append((x, y)) 

        # Draw a point where the user clicked
        turtle.goto(x, y)
        turtle.pendown()
        turtle.dot()

    else:
        # Create a new list of points for new obstacle and add current 
        # point to new obstacle
        ROOM_OBSTACLES.append([(x, y)])
        DRAWING_OBSTACLE = True

        # Draw a point where the user clicked
        turtle.penup()
        turtle.goto(x, y)
        turtle.pensize(2)
        turtle.fillcolor('black')
        turtle.pencolor('black')
        turtle.pendown()
        turtle.dot()

def dumpData():
    '''
    Dumps the ROOM_BOUNDARY, ROOM_OBSTACLES, and 
    (START_LOCATION, GOAL_LOCATION) to json files.
    '''
    # Dump ROOM_BOUNDARY data
    with open(ROOM_BOUNDARY_OUTPUT, 'w') as wr:
        json.dump(ROOM_BOUNDARY, wr)

    # Dump ROOM_OBSTACLES data
    with open(ROOM_OBSTACLES_OUTPUT, 'wb') as wr:
        json.dump(ROOM_OBSTACLES, wr)

    # Dump START_LOCATION and GOAL_LOCATION data.
    with open(LOCATION_OUTPUT, 'wb') as wr:
        json.dump([START_LOCATION, GOAL_LOCATION], wr)

def rightClick(x, y):
    '''
    Handles right-click events which either switches the mode from drawing 
    obstacles to picking the start and goal location.
    '''
    # Global variables
    global START_X, START_Y
    global PICKED_START, PICKED_GOAL
    global DONE

    if DONE: 
        # We're done gettting the environment from the user, dump the data 
        # and close the window
        dumpData()

        # Leave user with a message telling them we saved the data related 
        # to their environment
        print('  [SUCCESS]: Your custom polygonal environment was saved.\n\n' + 
              '             You can access the data for your environment\n' + 
              '             in the following files: \n' + 
              '                        - ' + ROOM_BOUNDARY_OUTPUT + '\n'
              '                        - ' + ROOM_OBSTACLES_OUTPUT + '\n'
              '                        - ' + LOCATION_OUTPUT)
        print('\n\n' + '-' * 65 + '\n')

        # Quit the window
        turtle.bye()

    elif not PICKED_START:
        turtle.penup()
        turtle.goto(START_X, START_Y)
        PICKED_START = True

# Global variables
ROOM_BOUNDARY    = [] # List of vertices in the polygonal boundary of the room
ROOM_OBSTACLES   = [] # 2D list of vertices of polygonal obstacles in room
START_LOCATION   = 0 # Start location of robot's path
GOAL_LOCATION    = 0 # Goal location of robot's path
START_X          = 0 # Keep track of start location of current boundary
START_Y          = 0
DRAWING_BOUNDARY = True # Indicates whether we're collecting boundary points
DRAWING_OBSTACLE = False # Indicates whether we're collecting obstacle points
PICKED_START     = False
PICKED_GOAL      = False
DONE             = False

if __name__ == '__main__':

    printWelcomeMsg() # Welcome user with details about this system

    # Ask user if we should guide them through process to customize their 
    # own polygonal room
    q = ('  Would you like to customize a polygonal room with polygonal\n' + 
         '  obstacles? [Y/n] ')
    customizeResponse = raw_input(q)
    customizeInput = customizeResponse == '' or customizeResponse == 'Y'

    # If user wants to customize their polygonal room and polygonal obstacles
    if customizeInput:
        printCustomizeInstructions() # Print instructions for user to console
        turtle.setup(WINDOW_SIZE, WINDOW_SIZE)  # Set window size
        turtle.title('Environment Customization Window') # Set title of window
        turtle.bgcolor('gray')
        turtle.shape('circle')
        turtle.shapesize(0.25, 0.25)
        window = turtle.Screen() # Get reference to window
        turtle.penup() # Start with the pen up, put it down once user clicks
        turtle.fillcolor('black')
        window.onclick(mouseClick) # Update GUI when a user clicks
        window.onclick(rightClick, 2) # Handle right-click events
        turtle.mainloop()

    else:
        pass

    # Organize the boundary into a polygon data structure
    BOUNDARY = path.Path(ROOM_BOUNDARY)

    # Quick sanity check to make sure all obstacles are within environment 
    # boundary and to make sure that no obstacles overlap with any other 
    # obstacles
    for i, obs in enumerate(ROOM_OBSTACLES):
        for p in obs: 
            if not BOUNDARY.contains_point(p):
                m = '[ERROR]: All obstacles are not contained within ' + \
                    'environment boundary.'
                print(m)
                exit(1)
    
    # Quick sanity check to make sure start location and end location were 
    # placed within environment boundary
    if not BOUNDARY.contains_point(START_LOCATION):
        m = '[ERROR]: Start location must be contained within the ' + \
            ' environment boundary.'
        print(m)
        exit(1)
    
    if not BOUNDARY.contains_point(GOAL_LOCATION):
        m = '[ERROR]: Goal location must be contained within the ' + \
            ' environment boundary.'
        print(m)
        exit(1)

