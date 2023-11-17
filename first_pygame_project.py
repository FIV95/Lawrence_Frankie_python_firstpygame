import pygame
import math
import sys

from pygame.locals import(
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    KEYDOWN,
    KEYUP,
    QUIT
)

pygame.init()

# Define health bar attributes
health_bar_width = 200
health_bar_height = 20
health_bar_surf = pygame.Surface((health_bar_width, health_bar_height))
health_bar_surf.fill((255, 0, 0))  # Red color
health_bar_rect = health_bar_surf.get_rect(topleft=(10, 10))  # Position at top-left corner

# Screen attributes
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Test")

# Clock for framerate
clock = pygame.time.Clock()

# Player attributes
player_surf = pygame.Surface((25, 25))
player_surf.fill((0, 0, 255))
player_rect = player_surf.get_rect(center=(150,678))
player_health = 100

# Player moveset
move_left = False
move_right = False
move_up = False
move_down= False

# Terrain
terrain_list = []
terrain_surf = pygame.Surface((100, 100))
terrain_surf.fill((0, 0, 0))
for x in range(2):
    for y in range(3):
        terrain_rect = terrain_surf.get_rect(center=(x*200+150, y*200+175))
        pygame.draw.rect(terrain_surf, (0, 255, 0), terrain_rect, 2)
        terrain_list.append(terrain_rect)

# Obstacles
obstacle_list = []
obstacle_surf = pygame.Surface((100, 200))
obstacle_surf.fill((0, 0, 0))
for x in range(2):
    for y in range(3):
        obstacle_rect = pygame.Rect(x*200+600, y*200+120, 100, 200)
        obstacle_list.append(obstacle_rect)

# Barriers
barrier_list = [
    pygame.Rect(screen_width // 2, 0, 20, screen_height // 2 - 100),
    pygame.Rect(screen_width // 2, screen_height // 2 + 100, 20, screen_height // 2 - 100)
]

# Elevator
elevator_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.circle(elevator_surf, (255, 0, 0), (25, 25), 25, 2)
elevator_rect = elevator_surf.get_rect(center=(950, 700))
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

cameras = []
for i in range(len(camera_positions)):
    new_camera_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(new_camera_surf, (128, 0, 128, 245), (5, 5), 5)
    new_camera_position = camera_positions[i]  # Use position from list
    new_camera_angle = camera_angles[i]
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

def handle_key_events(event):
    move_left = move_right = move_up = move_down = False

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

    return move_left, move_right, move_up, move_down
def handle_player_movement(player_rect, move_left, move_right, move_up, move_down, terrain_list, obstacle_list, barrier_list, screen_width, screen_height):
    collision_tolerance = 5
    if move_left:
        player_rect.x -= 3
        if player_rect.x < 0:
            player_rect.x = 0
        for container in terrain_list + obstacle_list + barrier_list:
            if player_rect.colliderect(container):
                if abs(player_rect.left - container.right) < collision_tolerance:
                    player_rect.left = container.right
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
def handle_cameras(cameras, screen, player_health):
    for camera in cameras:
        surf = camera["surface"]
        pos = camera["position"]
        rotation_angle = math.radians(camera["rotation_angle"])
        fov_angle = math.radians(camera["fov_angle"])
        rotation_paused = camera["paused"]
        camera_radius = camera["radius"]
        rotation_speed = camera["rotation_speed"] / 100  # Reduce rotation speed
        rotation_direction = camera["rotation_direction"]
        min_angle = math.radians(camera["min_angle"])  # Set min_angle to camera's min_angle
        max_angle = math.radians(camera["max_angle"])  # Set max_angle to camera's max_angle
        line_of_sight_length = 80
        num_lines = 2

        # Update rotation_angle based on rotation_speed and rotation_direction
        if not rotation_paused:
            rotation_angle += rotation_speed * rotation_direction
            if rotation_direction == 1 and rotation_angle >= max_angle:
                rotation_angle = max_angle
                rotation_direction = -1
            elif rotation_direction == -1 and rotation_angle <= min_angle:
                rotation_angle = min_angle
                rotation_direction = 1
            camera["rotation_angle"] = math.degrees(rotation_angle)
            camera["rotation_direction"] = rotation_direction

        screen.blit(surf, (pos[0] - 5, pos[1] - 5))

        for i in range(num_lines):
            # Adjust angle based on rotation_angle and fov_angle
            angle = rotation_angle + i * fov_angle / (num_lines - 1) - fov_angle / 2
            line_start = (
                pos[0] + camera_radius * math.cos(angle),
                pos[1] + camera_radius * math.sin(angle)
            )
            line_end = (
                pos[0] + line_of_sight_length * math.cos(angle),
                pos[1] + line_of_sight_length * math.sin(angle)
            )
            if line_start[0] <= player_rect.centerx <= line_end[0] and line_start[1] <= player_rect.centery <= line_end[1]:
                player_health -= .5

            pygame.draw.line(
                screen,
                (255, 255, 0, 100),
                line_start,
                line_end,
                2
            )
    return player_health



def check_win_condition(player_position, elevator_position):
    distance = math.sqrt((player_position[0] - elevator_position[0])**2 + (player_position[1] - elevator_position[1])**2)
    return distance < 50  # Adjust this value based on the size of your player and elevator


#game loop:
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        health_bar_rect.width = health_bar_width * (player_health / 100)  # Adjust width based on player's health
        health_bar_surf = pygame.Surface((health_bar_rect.width, health_bar_height))  # Create new surface with     adjusted width
        health_bar_surf.fill((255, 0, 0))  # Fill with red color

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

    if player_health <= 0:
            screen.fill((0, 0, 0))
            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render('Game Over', 1, (255, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False


    handle_player_movement(player_rect, move_left, move_right, move_up, move_down, terrain_list, obstacle_list, barrier_list, screen_width, screen_height)

    player_position = (player_rect.centerx, player_rect.centery)  # Update this with the player's current position
    elevator_position = (950, 700)

    if check_win_condition(player_position, elevator_position):
        print("You've won the game!")  # Replace this with your win condition handling code

    #fill the backround to black:
    screen.fill((0, 0, 0))
    player_health = handle_cameras(cameras, screen, player_health)



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

