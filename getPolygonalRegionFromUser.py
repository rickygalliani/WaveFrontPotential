# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

import turtle
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

def mouseClick(x, y):
    '''
    Handle mouse-click events.
    '''
    pass

if __name__ == '__main__':

    printWelcomeMsg()

    turtle.setup(WINDOW_MAX_SIZE, WINDOW_MAX_SIZE) # Set window size
    WINDOW = turtle.Screen() # Get reference to window

    tess = turtle.Turtle()
        

    WINDOW.onclick(mouseClick) # Listen for mouse-click events
    turtle.mainloop()
