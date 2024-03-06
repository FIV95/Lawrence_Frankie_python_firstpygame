import pygame
import math
import sys

# Import pygame.locals for easier access to key coordinates
from pygame.locals import(
    K_UP, #Key constant for up arrow key
    K_DOWN, #Key constant for down arrow key
    K_LEFT, #Key constant for left arrow key
    K_RIGHT, # Key constant for right arrow key
    KEYDOWN, # Key constant representing a key press
    KEYUP, # Key constant representing a key release
    QUIT # Key constant representing a window close event
)

pygame.init()

# Define health bar attributes
health_bar_width = 200 # Width of health bar
health_bar_height = 20 # Height of health bar
health_bar_surf = pygame.Surface((health_bar_width, health_bar_height)) # Create surface for health bar
health_bar_surf.fill((255, 0, 0))  # Red color
health_bar_rect = health_bar_surf.get_rect(topleft=(10, 10))  # Position at top-left corner

# Screen attributes
screen_width = 1024 # Width of screen
screen_height = 768 # Height of screen
screen = pygame.display.set_mode((screen_width, screen_height)) # Create screen
pygame.display.set_caption("Pygame Test") # Set window title

# Clock for framerate
clock = pygame.time.Clock()

# Player attributes
player_surf = pygame.Surface((25, 25)) # Create surface for player
player_surf.fill((0, 0, 255)) # Blue color
player_rect = player_surf.get_rect(center=(150,678)) # Position the center of the player surface at (150, 678)
player_health = 100 # Player's health

# Player moveset
# boleans for player movement
move_left = False
move_right = False
move_up = False
move_down= False

# Terrain
terrain_list = [] # List of terrain rectangles
terrain_surf = pygame.Surface((100, 100)) # Create surface for terrain
terrain_surf.fill((0, 0, 0)) # Black color
for x in range(2): # Create 2 rows of terrain
    for y in range(3): # Create 3 columns of terrain
        terrain_rect = terrain_surf.get_rect(center=(x*200+150, y*200+175)) # Position the center of the terrain surface at (x*200+150, y*200+175)
        pygame.draw.rect(terrain_surf, (0, 255, 0), terrain_rect, 2) # Draw a green rectangle on the terrain surface
        terrain_list.append(terrain_rect) # Add the terrain rectangle to the list of terrain rectangles

# Obstacles
obstacle_list = [] # List of obstacle rectangles
obstacle_surf = pygame.Surface((100, 200)) # Create surface for obstacles
obstacle_surf.fill((0, 0, 0)) # Black color
for x in range(2): # Create 2 rows of obstacles
    for y in range(3): # Create 3 columns of obstacles
        obstacle_rect = pygame.Rect(x*200+600, y*200+120, 100, 200) # Create a rectangle at (x*200+600, y*200+120) with width 100 and height 200
        obstacle_list.append(obstacle_rect) # Add the obstacle rectangle to the list of obstacle rectangles

# Barriers
barrier_list = [
    pygame.Rect(screen_width // 2, 0, 20, screen_height // 2 - 100),
    pygame.Rect(screen_width // 2, screen_height // 2 + 100, 20, screen_height // 2 - 100)
]

# Elevator
elevator_surf = pygame.Surface((50, 50), pygame.SRCALPHA) # Create surface for elevator
pygame.draw.circle(elevator_surf, (255, 0, 0), (25, 25), 25, 2) # Draw a red circle on the elevator surface
elevator_rect = elevator_surf.get_rect(center=(950, 700)) # Position the center of the elevator surface at (950, 700)
# List of camera positions
camera_positions = [
    (352, 623),
    (301, 422),
    (150, 324),
    (199, 170),
    (521, 484),
    (531, 606),
    (699, 214),
    (801, 519),
    (1011, 15),
    (399, 582)
]

# List of camera angles
camera_angles = [
    40,
    90,
    230,
    320,
    230,
    320,
    0,
    180,
    100,
    0

]

# List of cameras
cameras = [] # List of cameras
for i in range(len(camera_positions)): # Create a camera for each position
    new_camera_surf = pygame.Surface((10, 10), pygame.SRCALPHA) # Create surface for camera
    pygame.draw.circle(new_camera_surf, (128, 0, 128, 245), (5, 5), 5) # Draw a purple circle on the camera surface
    new_camera_position = camera_positions[i]  # Use position from list
    new_camera_angle = camera_angles[i] # Use angle from list
    camera = {
        "surface": new_camera_surf,
        "position": new_camera_position,
        "fov_angle": 50,
        "radius": 10,
        "rotation_speed": 1,
        "rotation_direction": 1,
        "rotation_angle": new_camera_angle,
        "pause_duration": 6000,
        "paused": False,
        "min_angle": new_camera_angle,  # Minimum rotation angle
        "max_angle": new_camera_angle + 90    # Maximum rotation angle
    }
    cameras.append(camera)

# Function to handle player movement and collisions
def handle_player_movement(player_rect, move_left, move_right, move_up, move_down, terrain_list, obstacle_list, barrier_list, screen_width, screen_height):
    collision_tolerance = 5
    if move_left: # If move_left is True
        player_rect.x -= 3 # Move player_rect left by 3
        if player_rect.x < 0: # If player_rect is off the left side of the screen
            player_rect.x = 0 # Set player_rect's left side to 0
        for container in terrain_list + obstacle_list + barrier_list: # For each container in the list of terrain and obstacle rectangles
            if player_rect.colliderect(container): # If player_rect collides with the container
                if abs(player_rect.left - container.right) < collision_tolerance: # If the distance between the left side of player_rect and the right side of the container is less than the collision tolerance
                    player_rect.left = container.right # Set player_rect's left side to the container's right side
    if move_right:
        player_rect.x += 3
        if player_rect.x > screen_width - player_rect.width:
            player_rect.x = screen_width - player_rect.width
        for container in terrain_list + obstacle_list + barrier_list:
            if player_rect.colliderect(container):
                if abs(player_rect.right - container.left) < collision_tolerance:
                    player_rect.right = container.left
    if move_down:
        player_rect.y += 3
        if player_rect.y > screen_height - player_rect.height:
            player_rect.y = screen_height - player_rect.height
        for container in terrain_list + obstacle_list + barrier_list:
            if player_rect.colliderect(container):
                if abs(player_rect.bottom - container.top) < collision_tolerance:
                    player_rect.bottom = container.top
    if move_up:
        player_rect.y -= 3
        if player_rect.y < 0:
            player_rect.y = 0
        for container in terrain_list + obstacle_list + barrier_list:
            if player_rect.colliderect(container):
                if abs(player_rect.top - container.bottom) < collision_tolerance:
                    player_rect.top = container.bottom

# Function to handle camera movement and collisions
def handle_cameras(cameras, screen, player_health):
    for camera in cameras: # For each camera
        surf = camera["surface"] # Get the camera's surface
        pos = camera["position"] # Get the camera's position
        rotation_angle = math.radians(camera["rotation_angle"]) # Get the camera's rotation angle
        fov_angle = math.radians(camera["fov_angle"]) # Get the camera's fov angle
        rotation_paused = camera["paused"] # Get the camera's paused state
        camera_radius = camera["radius"] # Get the camera's radius
        rotation_speed = camera["rotation_speed"] / 100  # Reduce rotation speed
        rotation_direction = camera["rotation_direction"] # Get the camera's rotation direction
        min_angle = math.radians(camera["min_angle"])  # Set min_angle to camera's min_angle
        max_angle = math.radians(camera["max_angle"])  # Set max_angle to camera's max_angle
        line_of_sight_length = 80 # Length of line of sight
        num_lines = 2 # Number of lines of sight conal line of sight

        # Update rotation_angle based on rotation_speed and rotation_direction
        if not rotation_paused: # If the camera is not paused
            rotation_angle += rotation_speed * rotation_direction # Update rotation_angle
            if rotation_direction == 1 and rotation_angle >= max_angle: # If the camera is rotating clockwise and has reached the max angle
                rotation_angle = max_angle # Set rotation_angle to max_angle
                rotation_direction = -1 # Set rotation_direction to -1
            elif rotation_direction == -1 and rotation_angle <= min_angle: # If the camera is rotating counterclockwise and has reached the min angle
                rotation_angle = min_angle # Set rotation_angle to min_angle
                rotation_direction = 1 # Set rotation_direction to 1
            camera["rotation_angle"] = math.degrees(rotation_angle) # Update camera's rotation_angle in the dictionary
            camera["rotation_direction"] = rotation_direction # Update camera's rotation_direction in the dictionary

        screen.blit(surf, (pos[0] - 5, pos[1] - 5)) # Blit the camera's surface to the screen


        #usages of cos and sin.
        #cos and sin are used to calculate the x and y coordinates of a point on a circle.
        # x is the end point of the line of sight.
        # y is the origin point of the line of sight. (the center of the camera) the circle
        #the x coordinate is calculated by multiplying the radius of the circle by the cosine of the angle.
        #the y coordinate is calculated by multiplying the radius of the circle by the sine of the angle.
        #the angle is measured in radians.
        #the angle is the angle between the x axis and the line connecting the center of the circle to the point on the circle.
        #why do we need to do this?
        #we need to do this because we need to calculate the x and y coordinates of the start and end points of the line of sight.
        #the start point is the center of the camera.
        #the end point is the point on the circle that is the line of sight length away from the center of the camera.


        for i in range(num_lines): # For each line of sight
            # Adjust angle based on rotation_angle and fov_angle
            angle = rotation_angle + i * fov_angle / (num_lines - 1) - fov_angle / 2 # Calculate angle
            line_start = ( # Calculate line start
                pos[0] + camera_radius * math.cos(angle),#x coordinate
                pos[1] + camera_radius * math.sin(angle) #y coordinate
            )
            line_end = ( # Calculate line end
                pos[0] + line_of_sight_length * math.cos(angle),#x coordinate
                pos[1] + line_of_sight_length * math.sin(angle)#y coordinate
            )
            if line_start[0] <= player_rect.centerx <= line_end[0] and line_start[1] <= player_rect.centery <= line_end[1]:
                player_health -= 1  # Reduce player's health because they are in the camera's line of sight

            pygame.draw.line( # Draw line of sight
                screen, # Surface to draw on
                (255, 255, 0, 100), # Color of line
                line_start, # Start point of line
                line_end, # End point of line
                2 # Width of line
            )
    return player_health # Return player's health based off of how many times they were in a camera's line of sight



def check_win_condition(player_position, elevator_position): # Check if player is close enough to elevator to win
    distance = math.sqrt((player_position[0] - elevator_position[0])**2 + (player_position[1] - elevator_position[1])**2) # Calculate distance between player and elevator
    return distance < 50  # Return True if distance is less than 50, False otherwise


#game loop:
running = True # Boolean to keep game running
while running: # While running is True the game will run
    for event in pygame.event.get(): # For each event, get the event, which is a list of all events that have happened since the last time the event queue was cleared.
        if event.type == pygame.QUIT: # If the event is a quit event
            running = False # Set running to False
            pygame.quit() # Quit pygame
            sys.exit()

        # i need to define thehealth bar in thegame loop as well because i need to update the health bar every frame.
        health_bar_rect.width = health_bar_width * (player_health / 100)  # Adjust width of health bar. 100 is max health
        health_bar_surf = pygame.Surface((health_bar_rect.width, health_bar_height))  # Create surface for health bar
        health_bar_surf.fill((255, 0, 0))  # Fill with red color
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            print(f"Mouse clicked at ({x}, {y})")

        # Handle key presses
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                print("moving left")
                move_left = True
            elif event.key == K_RIGHT:
                print("moving right")
                move_right = True
            elif event.key == K_UP:
                print("moving up")
                move_up = True
            elif event.key == K_DOWN:
                print("moving down")
                move_down = True

        # Handle key releases
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                move_left = False
            elif event.key == K_RIGHT:
                move_right = False
            elif event.key == K_UP:
                move_up = False
            elif event.key == K_DOWN:
                move_down = False

    #check if player health is less than or equal to 0. this is our lose condition.
    if player_health <= 0:
            screen.fill((0, 0, 0)) # Fill screen with black
            game_over_font = pygame.font.Font(None, 74) # Create font for game over text
            game_over_text = game_over_font.render('Game Over', 1, (255, 0, 0)) # Create game over text
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))  # Blit game over text to screen
            pygame.display.flip() # Update display
            pygame.time.wait(3000) # Wait 3 seconds
            running = False # Set running to False


    handle_player_movement(player_rect, move_left, move_right, move_up, move_down, terrain_list, obstacle_list, barrier_list, screen_width, screen_height) # Handle player movement and collisions . we call on our previously defined function.


    # this is our wind condition checks
    player_position = (player_rect.centerx, player_rect.centery)  # Update this with the player's current position
    elevator_position = (950, 700) # Update this with the elevator's position

    if check_win_condition(player_position, elevator_position): # If the player has won
        print("You've won the game!")  # todo make actual win condition

    #fill the backround to black:
    screen.fill((0, 0, 0))
    player_health = handle_cameras(cameras, screen, player_health) # Handle cameras and collisions and update player's health by invoking our previously defined function.


    # the following are all blit commands which actually pain all thjese surfaces to the screen.
    #blit player surface to appear on the screen:
    screen.blit(player_surf, player_rect)

    #blit the terrain surfaces to appear on the screen:
    for terrain in terrain_list:
       pygame.draw.rect(screen, (0, 255, 0), terrain, 2)

    #blit the obstacle surfaces to appear on the screen:
    for obstacle in obstacle_list:
         pygame.draw.rect(screen, (0, 255, 0), obstacle, 2)

    #blit the barrier surfaces to appear on the screen:
    for barrier in barrier_list:
         pygame.draw.rect(screen, (0, 255, 0), barrier, 2)

        #blit the elevator surface to appear on the screen:
    screen.blit(elevator_surf, elevator_rect)

    screen.blit(health_bar_surf, health_bar_rect)

        #update the display:
    pygame.display.update()
    clock.tick(60)
pygame.quit()
sys.exit()

