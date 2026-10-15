import pygame
import random
import math

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------
WIDTH = 1100
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Universe")

clock = pygame.time.Clock()

# -----------------------------
# SETTINGS
# -----------------------------
NUM_PARTICLES = 180
MAX_DISTANCE = 120
MOUSE_RADIUS = 180

# -----------------------------
# PARTICLE
# -----------------------------
class Particle:

    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)

        self.vx = random.uniform(-0.7, 0.7)
        self.vy = random.uniform(-0.7, 0.7)

        self.radius = random.choice([1, 1, 2, 2, 3])

    def update(self, mouse_x, mouse_y):

        # -------------------------
        # MOUSE GRAVITY
        # -------------------------

        dx = mouse_x - self.x
        dy = mouse_y - self.y

        distance = math.sqrt(dx * dx + dy * dy)

        if 20 < distance < MOUSE_RADIUS:

            force = (MOUSE_RADIUS - distance) / MOUSE_RADIUS

            self.vx += (dx / distance) * force * 0.08
            self.vy += (dy / distance) * force * 0.08

        # -------------------------
        # MOVEMENT
        # -------------------------

        self.x += self.vx
        self.y += self.vy

        # -------------------------
        # FRICTION
        # -------------------------

        self.vx *= 0.99
        self.vy *= 0.99

        # -------------------------
        # SCREEN WRAP
        # -------------------------

        if self.x < 0:
            self.x = WIDTH

        if self.x > WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = HEIGHT

        if self.y > HEIGHT:
            self.y = 0

    # -----------------------------
    # EXPLOSION
    # -----------------------------

    def explode(self, x, y):

        dx = self.x - x
        dy = self.y - y

        distance = math.sqrt(dx * dx + dy * dy)

        if 0 < distance < 180:

            force = (180 - distance) / distance

            self.vx += dx * force * 0.15
            self.vy += dy * force * 0.15


# -----------------------------
# CREATE PARTICLES
# -----------------------------

particles = [
    Particle()
    for _ in range(NUM_PARTICLES)
]


# -----------------------------
# MAIN LOOP
# -----------------------------

running = True

while running:

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # -------------------------
    # EVENTS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Click = explosion
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                for particle in particles:
                    particle.explode(
                        mouse_x,
                        mouse_y
                    )

    # -------------------------
    # UPDATE
    # -------------------------

    for particle in particles:

        particle.update(
            mouse_x,
            mouse_y
        )

    # -------------------------
    # DRAW BACKGROUND
    # -------------------------

    screen.fill((5, 5, 12))

    # -------------------------
    # DRAW CONNECTIONS
    # -------------------------

    for i in range(len(particles)):

        p1 = particles[i]

        for j in range(i + 1, len(particles)):

            p2 = particles[j]

            dx = p1.x - p2.x
            dy = p1.y - p2.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance < MAX_DISTANCE:

                # Closer = brighter
                alpha = int(
                    255 *
                    (1 - distance / MAX_DISTANCE)
                )

                color = (
                    alpha // 2,
                    alpha // 2,
                    alpha
                )

                pygame.draw.line(
                    screen,
                    color,
                    (int(p1.x), int(p1.y)),
                    (int(p2.x), int(p2.y)),
                    1
                )

    # -------------------------
    # DRAW PARTICLES
    # -------------------------

    for particle in particles:

        pygame.draw.circle(
            screen,
            (150, 180, 255),
            (
                int(particle.x),
                int(particle.y)
            ),
            particle.radius
        )

    # -------------------------
    # MOUSE ORB
    # -------------------------

    pygame.draw.circle(
        screen,
        (80, 100, 255),
        (mouse_x, mouse_y),
        5
    )

    pygame.draw.circle(
        screen,
        (50, 60, 150),
        (mouse_x, mouse_y),
        MOUSE_RADIUS,
        1
    )

    # -------------------------
    # UPDATE SCREEN
    # -------------------------

    pygame.display.flip()

    clock.tick(60)


pygame.quit()