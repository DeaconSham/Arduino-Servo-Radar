import pygame
import serial
import math
import sys

#configuration
SERIAL_PORT = '/dev/cu.usbmodem21401'
BAUD_RATE = 9600
MAX_DISTANCE = 100

#pygame setup
pygame.init()

#screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RADAR_ORIGIN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
RADAR_RADIUS = 500

#colours
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

#display Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Arduino Radar")
font = pygame.font.Font(None, 24) # Use the default font for compatibility
clock = pygame.time.Clock()

#serial Connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port {SERIAL_PORT}: {e}")
    pygame.quit()
    sys.exit()

#data Storage
detected_points = []

def polar_to_cartesian(angle, distance):
    """Convert polar coordinates to Cartesian coordinates for drawing."""
    rad = math.radians(180 - angle)
    x = RADAR_ORIGIN[0] + distance * math.cos(rad)
    y = RADAR_ORIGIN[1] - distance * math.sin(rad)
    return int(x), int(y)

def draw_radar_background():
    """Draw the static elements of the radar display."""
    #concentric circles
    for i in range(1, 5):
        radius = i * (RADAR_RADIUS / 4)
        pygame.draw.circle(screen, DARK_GREEN, RADAR_ORIGIN, int(radius), 1)

    #radial lines
    for angle in range(0, 181, 30):
        rad = math.radians(180 - angle) # Align with data drawing
        end_x = RADAR_ORIGIN[0] + RADAR_RADIUS * math.cos(rad)
        end_y = RADAR_ORIGIN[1] - RADAR_RADIUS * math.sin(rad)
        pygame.draw.line(screen, DARK_GREEN, RADAR_ORIGIN, (end_x, end_y), 1)

current_angle = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #read and parse data from Arduino
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            parts = line.split(',')
            if len(parts) == 2:
                angle_str, distance_str = parts
                angle = int(angle_str)
                distance = int(distance_str)
                current_angle = angle
                
                if 0 < distance < MAX_DISTANCE:
                    detected_points = [p for p in detected_points if p[0] != angle]
                    detected_points.append((angle, distance))

        except (ValueError, UnicodeDecodeError) as e:
            print(f"Could not parse data: '{line}'. Error: {e}")

    #drawing
    screen.fill(BLACK)
    draw_radar_background()

    #draw detected points
    for angle, distance in detected_points:
        scaled_distance = (distance / MAX_DISTANCE) * RADAR_RADIUS
        pos = polar_to_cartesian(angle, scaled_distance)
        pygame.draw.circle(screen, GREEN, pos, 3)

    #draw sweeping radar line
    sweep_end_pos = polar_to_cartesian(current_angle, RADAR_RADIUS)
    pygame.draw.line(screen, GREEN, RADAR_ORIGIN, sweep_end_pos, 2)

    #draw text info
    angle_text = font.render(f"Angle: {current_angle}°", True, WHITE)
    screen.blit(angle_text, (10, 10))

    #update display
    pygame.display.flip()

    #frame rate
    clock.tick(60)

#cleanup
ser.close()
pygame.quit()
sys.exit()