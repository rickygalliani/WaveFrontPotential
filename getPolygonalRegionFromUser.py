# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

import turtle
import time
import json
from constants import *

def printWelcomeMsg():
    '''
    Prints a welcome message to the user.
    '''
    print('\n\n' + '-' * 65 + '\n')
    print(' ' * 28 + 'WELCOME' + ' ' * 28 + '\n')
    print('  This system generates a path from a start location to an end\n' +
          '  location within a user-specified description of a closed, \n' + 
          '  polygonal room with polygonal obstacles in its interior \n' +
          '  using the Wave Front Potential Method.')
    print('\n\n' + '-' * 65 + '\n\n')

def printCustomizeInstructions():
    '''
    Prints instructions about how to customize the polygonal room to the 
    console.
    '''
    print('\n\n' + '-' * 65 + '\n')
    print(' ' * 18 + 'INPUT CUSTOMIZATION INSTRUCTIONS' + ' ' * 18 + '\n')
    print('  1. Click once in locations in the window to form the\n' + 
          '     polygonal boundary of your room. When you\'re done tracing \n' + 
          '     the boundary of your room, click twice.')
    print('\n\n' + '-' * 65 + '\n\n')

def mouseClick(x, y):
    '''
    Handle mouse-click events.
    '''
    global ROOM_BOUNDARY, PREV_CLICK_TIME, DRAWING_BOUNDARY, DRAWING_OBSTACLE

    # See if user is done drawing the boundary or the current shape
    curClickTime = time.time()

    # User is done with boundary or current shape, indicated by double click
    if (curClickTime - PREV_CLICK_TIME) < DOUBLE_CLICK_THRESHOLD:
        print('Got double-click.')
        if DRAWING_BOUNDARY:
            # Remove last point was just part of double-click.
            ROOM_BOUNDARY = ROOM_BOUNDARY[:-1] 
            turtle.undo()
            turtle.undo()

            # Close up the boundary
            finX, finY = ROOM_BOUNDARY[-1]
            initX, initY = ROOM_BOUNDARY[0]
            turtle.penup()
            turtle.goto(finX, finY)
            turtle.pendown()
            turtle.goto(initX, initY)
            turtle.penup()

            # No longer drawing boundary, now drawing obstacles
            DRAWING_BOUNDARY = False
            print('Ending boundary drawing.')

        else: # DRAWING_OBSTACLE
            # Remove last point from current obstacle, part of double-click
            ROOM_OBSTACLES[-1] = ROOM_OBSTACLES[-1][:-1]
            turtle.undo()
            turtle.undo()

            # Close up the boundary
            finX, finY = ROOM_OBSTACLES[-1][-1] 
            initX, initY = ROOM_OBSTACLES[-1][0]
            turtle.penup()
            turtle.goto(finX, finY)
            turtle.pendown()
            turtle.goto(initX, initY)
            turtle.penup()

            # No longer drawing this obstacle
            DRAWING_OBSTACLE = False

    else: 
        if DRAWING_BOUNDARY:
            print('Adding point to boundary')
            # Add current point to boundary
            ROOM_BOUNDARY.append((x, y)) 

            # Draw a point where the user clicked
            turtle.goto(x, y)
            turtle.pendown()
            turtle.dot()

        elif DRAWING_OBSTACLE:
            print('Adding point to existing obstacle')
            # Add current point to current obstacle
            ROOM_OBSTACLES[-1].append((x, y)) 

            # Draw a point where the user clicked
            turtle.goto(x, y)
            turtle.pendown()
            turtle.dot()

        else:
            print('Adding point to new obstacle')
            # Create a new list of points for new obstacle and add current 
            # point to new obstacle
            ROOM_OBSTACLES.append([(x, y)])
            DRAWING_OBSTACLE = True

            # Draw a point where the user clicked
            turtle.goto(x, y)
            turtle.pendown()
            turtle.dot()

    # Keep track of click times, looking out for double-click
    PREV_CLICK_TIME = curClickTime 

def dumpData(x, y):
    '''
    Dumps the data in ROOM_BOUNDARY and ROOM_OBSTACLES to .csv's.
    '''
    # Dump ROOM_BOUNDARY data
    with open(ROOM_BOUNDARY_OUTPUT, 'w') as wr:
        json.dump(ROOM_BOUNDARY, wr)

    # Dump ROOM_OBSTACLES data
    with open(ROOM_OBSTACLES_OUTPUT, 'wb') as wr:
        json.dump(ROOM_OBSTACLES, wr)

# Global variables
ROOM_BOUNDARY    = [] # List of vertices in the polygonal boundary of the room
ROOM_OBSTACLES   = [] # 2D list of vertices of polygonal obstacles in room
PREV_CLICK_TIME  = time.time() # Keep track of timing of each click
DRAWING_BOUNDARY = True # Indicates whether we're collecting boundary points
DRAWING_OBSTACLE = False # Indicates whether we're collecting obstacle points

# Output files
ROOM_BOUNDARY_OUTPUT  = 'room_boundary.csv'
ROOM_OBSTACLES_OUTPUT = 'room_obstacles.csv'

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
        # Print instructions for user to console
        printCustomizeInstructions() 

        # Set window size
        turtle.setup(WINDOW_MAX_SIZE, WINDOW_MAX_SIZE) 

        # Get reference to window
        window = turtle.Screen() 

        # Listen for mouse-click events
        turtle.penup()

        window.onclick(mouseClick) 
        window.onclick(dumpData, 2)
        turtle.mainloop()

    else:
        pass
    

    print(str(ROOM_BOUNDARY))

