# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

WINDOW_MAX_SIZE       = 1000
D                     = 10.0
WINDOW_LENGTH         = WINDOW_MAX_SIZE / D
CLOSE_LOOP_THRESHOLD  = 2.5
K                  = 10 ** -3
G                  = 10 ** -3

# Output files
ROOM_BOUNDARY_OUTPUT  = 'room_boundary.json'
ROOM_OBSTACLES_OUTPUT = 'room_obstacles.json'
LOCATION_OUTPUT       = 'location_output.json'