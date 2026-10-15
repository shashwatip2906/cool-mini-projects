import pygame
import math

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------
WIDTH, HEIGHT = 1000, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Lizard")

clock = pygame.time.Clock()

# -----------------------------
# COLORS
# -----------------------------
BLACK = (5, 8, 12)
WHITE = (235, 235, 235)
GRAY = (150, 150, 150)

# -----------------------------
# LIZARD SETTINGS
# -----------------------------
NUM_VERTEBRAE = 24

body = [
    pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    for _ in range(NUM_VERTEBRAE)
]

# Target = mouse position
target = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def lerp(a, b, amount):
    return a + (b - a) * amount


def rotate_vector(v, angle):
    return v.rotate(angle)


# -----------------------------
# DRAW VERTEBRAE
# -----------------------------
def draw_spine():
    for i in range(len(body) - 1):

        p1 = body[i]
        p2 = body[i + 1]

        pygame.draw.line(
            screen,
            WHITE,
            p1,
            p2,
            3
        )

        # Small vertebra
        pygame.draw.circle(
            screen,
            WHITE,
            (int(p1.x), int(p1.y)),
            4
        )


# -----------------------------
# DRAW RIBS
# -----------------------------
def draw_ribs():

    for i in range(3, 15):

        p = body[i]

        # Direction of spine
        direction = body[i - 1] - body[i + 1]

        if direction.length() == 0:
            continue

        direction = direction.normalize()

        # Perpendicular
        side = pygame.Vector2(
            -direction.y,
            direction.x
        )

        rib_length = 35 - i * 1.2

        left = p + side * rib_length
        right = p - side * rib_length

        pygame.draw.line(
            screen,
            GRAY,
            p,
            left,
            2
        )

        pygame.draw.line(
            screen,
            GRAY,
            p,
            right,
            2
        )


# -----------------------------
# DRAW LEG
# -----------------------------
def draw_leg(index, side):

    p = body[index]

    # Direction of body
    direction = body[index - 1] - body[index + 1]

    if direction.length() == 0:
        return

    direction = direction.normalize()

    perpendicular = pygame.Vector2(
        -direction.y,
        direction.x
    )

    # Left / right
    perpendicular *= side

    # Upper leg
    hip = p + perpendicular * 10

    knee = (
        hip
        + perpendicular * 35
        + direction * 5
    )

    # Lower leg
    foot = (
        knee
        + perpendicular * 25
        - direction * 5
    )

    pygame.draw.line(
        screen,
        WHITE,
        hip,
        knee,
        4
    )

    pygame.draw.line(
        screen,
        WHITE,
        knee,
        foot,
        3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(knee.x), int(knee.y)),
        3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(foot.x), int(foot.y)),
        3
    )


# -----------------------------
# DRAW HEAD
# -----------------------------
def draw_head():

    head = body[0]

    direction = body[0] - body[1]

    if direction.length() == 0:
        direction = pygame.Vector2(1, 0)

    direction = direction.normalize()

    # Head
    nose = head + direction * 30

    pygame.draw.line(
        screen,
        WHITE,
        head,
        nose,
        5
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (int(head.x), int(head.y)),
        13
    )

    # Jaw
    side = pygame.Vector2(
        -direction.y,
        direction.x
    )

    jaw_left = head + side * 10 + direction * 5
    jaw_right = head - side * 10 + direction * 5

    pygame.draw.line(
        screen,
        GRAY,
        jaw_left,
        jaw_right,
        2
    )

    # Eyes
    eye1 = head + side * 7 + direction * 5
    eye2 = head - side * 7 + direction * 5

    pygame.draw.circle(
        screen,
        BLACK,
        (int(eye1.x), int(eye1.y)),
        3
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (int(eye2.x), int(eye2.y)),
        3
    )


# -----------------------------
# DRAW TAIL
# -----------------------------
def draw_tail():

    for i in range(15, len(body) - 1):

        p1 = body[i]
        p2 = body[i + 1]

        pygame.draw.line(
            screen,
            WHITE,
            p1,
            p2,
            max(1, 4 - (i - 15) // 3)
        )


# -----------------------------
# MAIN LOOP
# -----------------------------
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Mouse controls the lizard
        if event.type == pygame.MOUSEMOTION:
            target = pygame.Vector2(event.pos)

    # -------------------------
    # MOVE HEAD TOWARDS TARGET
    # -------------------------

    body[0] = lerp(
        body[0],
        target,
        0.12
    )

    # -------------------------
    # FOLLOW THE PREVIOUS BONE
    # -------------------------

    for i in range(1, NUM_VERTEBRAE):

        previous = body[i - 1]
        current = body[i]

        direction = current - previous

        distance = 15

        if direction.length() != 0:

            direction = direction.normalize()

            desired = previous + direction * distance

            body[i] = lerp(
                current,
                desired,
                0.35
            )

    # -------------------------
    # DRAW
    # -------------------------

    screen.fill(BLACK)

    draw_tail()
    draw_spine()
    draw_ribs()

    # Legs
    draw_leg(6, 1)
    draw_leg(6, -1)

    draw_leg(10, 1)
    draw_leg(10, -1)

    draw_leg(14, 1)
    draw_leg(14, -1)

    draw_head()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()