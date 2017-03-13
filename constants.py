# Ricky Galliani
# Wave Front Potential Path Finder
# March 2017

WINDOW_SIZE            = 1000
MAX_NUM_STEPS          = 5000
MAX_NUM_ENV_VERTICES   = 10
MAX_NUM_OBSTACLES      = 5
MAX_NUM_OBSTACLE_SIDES = 10
MIN_OBSTACLE_RADIUS    = 5.0
MAX_OBSTACLE_RADIUS    = 50.0
D                      = 1.0
WINDOW_LENGTH          = WINDOW_SIZE / D
CLOSE_LOOP_THRESHOLD   = 2.5
CLOSE_PATH_THRESHOLD   = 10.0
K                      = 1.0
G                      = 6.5

BOUNDARY_SPACE         = 0
OBSTACLE_SPACE         = 1
FREE_SPACE             = 2
VISITED_SPACE          = 3

# Output files
ROOM_BOUNDARY_OUTPUT   = 'room_boundary.json'
ROOM_OBSTACLES_OUTPUT  = 'room_obstacles.json'
LOCATION_OUTPUT        = 'location_output.json'