import os
import sys
import math
import random
import time

import cv2
import numpy as np
import pygame

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1200
HEIGHT = 750

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

FPS = 60

# Tiny particles
NUM_PARTICLES = 2600

# Hand interaction
HAND_RADIUS = 270

# Particle physics
MAX_SPEED = 22.0

# Hand smoothing
HAND_SMOOTHING = 0.38

# Model
MODEL_FILE = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "hand_landmarker.task"
)


# ============================================================
# PARTICLE MODES
# ============================================================

MODES = [
    "COSMIC",
    "VORTEX",
    "GALAXY",
    "STORM"
]

mode = 0


# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.DOUBLEBUF
)

pygame.display.set_caption(
    "NEON HAND PARTICLE UNIVERSE"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    18
)

small_font = pygame.font.SysFont(
    "Arial",
    14
)

title_font = pygame.font.SysFont(
    "Arial",
    25,
    bold=True
)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)

camera.set(
    cv2.CAP_PROP_FPS,
    30
)

if not camera.isOpened():

    print()
    print("Could not open webcam.")
    print()

    pygame.quit()
    sys.exit()


# ============================================================
# MEDIAPIPE MODEL
# ============================================================

if not os.path.exists(MODEL_FILE):

    print()
    print("=" * 60)
    print("hand_landmarker.task is missing.")
    print("=" * 60)
    print()
    print(
        "Put hand_landmarker.task in the same folder"
    )
    print(
        "as this Python file."
    )
    print()
    print(
        "No automatic download is performed."
    )
    print()

    camera.release()
    pygame.quit()
    sys.exit()


# ============================================================
# MEDIAPIPE VIDEO MODE
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=MODEL_FILE
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,

    # IMPORTANT
    # detect_for_video() requires VIDEO mode
    running_mode=vision.RunningMode.VIDEO,

    num_hands=1,

    min_hand_detection_confidence=0.45,

    min_hand_presence_confidence=0.45,

    min_tracking_confidence=0.45
)

hand_landmarker = (
    vision.HandLandmarker.create_from_options(
        options
    )
)


# ============================================================
# PARTICLE ARRAYS
# ============================================================

particles_x = np.random.uniform(
    0,
    WIDTH,
    NUM_PARTICLES
).astype(np.float32)

particles_y = np.random.uniform(
    0,
    HEIGHT,
    NUM_PARTICLES
).astype(np.float32)

velocity_x = np.random.uniform(
    -0.6,
    0.6,
    NUM_PARTICLES
).astype(np.float32)

velocity_y = np.random.uniform(
    -0.6,
    0.6,
    NUM_PARTICLES
).astype(np.float32)


# ============================================================
# VERY SMALL PARTICLE SIZES
# ============================================================

particle_size = np.random.choice(
    [
        0.8,
        0.9,
        1.0,
        1.0,
        1.0,
        1.1,
        1.2,
        1.3,
        1.5,
        1.7
    ],
    NUM_PARTICLES
).astype(np.float32)


# ============================================================
# COLOR / ANIMATION
# ============================================================

particle_hue = np.random.uniform(
    175,
    320,
    NUM_PARTICLES
).astype(np.float32)

particle_phase = np.random.uniform(
    0,
    math.pi * 2,
    NUM_PARTICLES
).astype(np.float32)

particle_twinkle = np.random.uniform(
    0.7,
    1.5,
    NUM_PARTICLES
).astype(np.float32)


# ============================================================
# SURFACES
# ============================================================

particle_surface = pygame.Surface(
    (WIDTH, HEIGHT),
    pygame.SRCALPHA
)

glow_surface = pygame.Surface(
    (WIDTH, HEIGHT),
    pygame.SRCALPHA
)


# ============================================================
# HAND VARIABLES
# ============================================================

hand_detected = False

hand_x = WIDTH / 2
hand_y = HEIGHT / 2

previous_hand_x = hand_x
previous_hand_y = hand_y

hand_speed = 0

landmarks = None

gesture = "NONE"


# ============================================================
# SHOCKWAVE
# ============================================================

shockwave_radius = 0
shockwave_strength = 0


# ============================================================
# LASER
# ============================================================

laser_active = False

LASER_LENGTH = 1600

LASER_WIDTH = 22


# ============================================================
# LASER PARTICLES
# ============================================================

laser_particles = []

for _ in range(500):

    laser_particles.append({

        "distance": random.uniform(
            0,
            LASER_LENGTH
        ),

        "offset": random.uniform(
            -13,
            13
        ),

        "speed": random.uniform(
            7,
            26
        ),

        "size": random.uniform(
            0.6,
            1.8
        ),

        "phase": random.uniform(
            0,
            math.pi * 2
        )
    })


# ============================================================
# TIMESTAMP
# ============================================================

video_timestamp = 0


# ============================================================
# UTILITY
# ============================================================

def distance_points(a, b):

    dx = a.x - b.x
    dy = a.y - b.y

    return math.sqrt(
        dx * dx +
        dy * dy
    )


# ============================================================
# FINGER EXTENSION
# ============================================================

def finger_extended(
    hand,
    tip_index,
    pip_index,
    mcp_index
):

    wrist = hand[0]

    tip = hand[tip_index]

    pip = hand[pip_index]

    mcp = hand[mcp_index]

    # --------------------------------------------------------
    # Distance from wrist
    # --------------------------------------------------------

    tip_distance = distance_points(
        tip,
        wrist
    )

    pip_distance = distance_points(
        pip,
        wrist
    )

    # --------------------------------------------------------
    # Finger length relationship
    # --------------------------------------------------------

    distance_test = (
        tip_distance
        >
        pip_distance * 1.12
    )

    # --------------------------------------------------------
    # Joint angle
    # --------------------------------------------------------

    ax = mcp.x - pip.x
    ay = mcp.y - pip.y

    bx = tip.x - pip.x
    by = tip.y - pip.y

    len_a = math.sqrt(
        ax * ax +
        ay * ay
    )

    len_b = math.sqrt(
        bx * bx +
        by * by
    )

    if len_a < 0.0001 or len_b < 0.0001:

        return distance_test

    dot = (
        ax * bx +
        ay * by
    )

    cosine = dot / (
        len_a *
        len_b
    )

    cosine = max(
        -1,
        min(
            1,
            cosine
        )
    )

    angle = math.degrees(
        math.acos(cosine)
    )

    angle_test = angle > 145

    return (
        distance_test
        and
        angle_test
    )


# ============================================================
# GESTURE DETECTION
# ============================================================

def detect_gesture(hand):

    thumb_tip = hand[4]

    index_tip = hand[8]
    middle_tip = hand[12]
    ring_tip = hand[16]
    pinky_tip = hand[20]

    index_extended = finger_extended(
        hand,
        8,
        6,
        5
    )

    middle_extended = finger_extended(
        hand,
        12,
        10,
        9
    )

    ring_extended = finger_extended(
        hand,
        16,
        14,
        13
    )

    pinky_extended = finger_extended(
        hand,
        20,
        18,
        17
    )

    # ========================================================
    # PINCH
    # ========================================================

    pinch_distance = distance_points(
        thumb_tip,
        index_tip
    )

    if pinch_distance < 0.075:

        return "PINCH"

    # ========================================================
    # LASER
    #
    # Index finger extended.
    # Other fingers mostly curled.
    #
    # This is deliberately permissive.
    # ========================================================

    curled_count = 0

    if not middle_extended:
        curled_count += 1

    if not ring_extended:
        curled_count += 1

    if not pinky_extended:
        curled_count += 1

    if (
        index_extended
        and
        curled_count >= 2
    ):

        return "LASER"

    # ========================================================
    # VORTEX
    #
    # Index + middle
    # ========================================================

    if (
        index_extended
        and
        middle_extended
        and
        not ring_extended
        and
        not pinky_extended
    ):

        return "VORTEX"

    # ========================================================
    # OPEN PALM
    # ========================================================

    extended_count = sum([
        index_extended,
        middle_extended,
        ring_extended,
        pinky_extended
    ])

    if extended_count >= 4:

        return "OPEN PALM"

    # ========================================================
    # FIST
    # ========================================================

    if extended_count == 0:

        return "FIST"

    # ========================================================
    # NEUTRAL
    # ========================================================

    return "NEUTRAL"


# ============================================================
# HAND DETECTION
# ============================================================

def detect_hand(frame):

    global video_timestamp

    # --------------------------------------------------------
    # BGR -> RGB
    # --------------------------------------------------------

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    # --------------------------------------------------------
    # MediaPipe timestamps must increase
    # --------------------------------------------------------

    video_timestamp += 33

    result = hand_landmarker.detect_for_video(
        mp_image,
        video_timestamp
    )

    if not result.hand_landmarks:

        return None

    hand = result.hand_landmarks[0]

    # ========================================================
    # PALM CENTER
    # ========================================================

    palm_indices = [
        0,
        5,
        9,
        13,
        17
    ]

    palm_x = np.mean([
        hand[i].x
        for i in palm_indices
    ])

    palm_y = np.mean([
        hand[i].y
        for i in palm_indices
    ])

    # ========================================================
    # GESTURE
    # ========================================================

    gesture_name = detect_gesture(
        hand
    )

    return (
        palm_x,
        palm_y,
        hand,
        gesture_name
    )


# ============================================================
# LASER DIRECTION
# ============================================================

def get_laser_direction():

    if landmarks is None:

        return (
            1.0,
            0.0
        )

    # Index MCP
    base = landmarks[5]

    # Index TIP
    tip = landmarks[8]

    dx = tip.x - base.x
    dy = tip.y - base.y

    length = math.sqrt(
        dx * dx +
        dy * dy
    )

    if length < 0.001:

        return (
            1.0,
            0.0
        )

    return (
        dx / length,
        dy / length
    )


# ============================================================
# RESET PARTICLES
# ============================================================

def reset_particles():

    global particles_x
    global particles_y
    global velocity_x
    global velocity_y

    particles_x[:] = np.random.uniform(
        0,
        WIDTH,
        NUM_PARTICLES
    )

    particles_y[:] = np.random.uniform(
        0,
        HEIGHT,
        NUM_PARTICLES
    )

    velocity_x[:] = np.random.uniform(
        -0.6,
        0.6,
        NUM_PARTICLES
    )

    velocity_y[:] = np.random.uniform(
        -0.6,
        0.6,
        NUM_PARTICLES
    )


# ============================================================
# SHOCKWAVE
# ============================================================

def create_shockwave():

    global shockwave_radius
    global shockwave_strength

    shockwave_radius = 20
    shockwave_strength = 1.0


def update_shockwave():

    global shockwave_radius
    global shockwave_strength

    if shockwave_strength <= 0:

        return

    shockwave_radius += 15

    shockwave_strength *= 0.94

    dx = particles_x - hand_x
    dy = particles_y - hand_y

    distances = np.sqrt(
        dx * dx +
        dy * dy
    )

    distances = np.maximum(
        distances,
        1
    )

    difference = np.abs(
        distances -
        shockwave_radius
    )

    hit = difference < 35

    if np.any(hit):

        strength = (
            1 -
            difference[hit] / 35
        )

        strength *= shockwave_strength

        velocity_x[hit] += (
            dx[hit]
            /
            distances[hit]
            *
            strength
            *
            3.5
        )

        velocity_y[hit] += (
            dy[hit]
            /
            distances[hit]
            *
            strength
            *
            3.5
        )

    if shockwave_radius > 800:

        shockwave_strength = 0


# ============================================================
# LASER COLLISION
# ============================================================

def laser_collision():

    if not laser_active:

        return

    if landmarks is None:

        return

    direction_x, direction_y = (
        get_laser_direction()
    )

    origin_x = hand_x
    origin_y = hand_y

    # Relative position
    rx = particles_x - origin_x
    ry = particles_y - origin_y

    # Distance along laser
    along = (
        rx * direction_x
        +
        ry * direction_y
    )

    # Distance away from laser
    side = np.abs(
        rx * direction_y
        -
        ry * direction_x
    )

    # --------------------------------------------------------
    # Laser hit
    # --------------------------------------------------------

    hit = (
        (along > 0)
        &
        (along < LASER_LENGTH)
        &
        (side < LASER_WIDTH)
    )

    if not np.any(hit):

        return

    strength = np.clip(
        1 -
        (
            side[hit]
            /
            LASER_WIDTH
        ),
        0,
        1
    )

    # --------------------------------------------------------
    # Push particles forward
    # --------------------------------------------------------

    velocity_x[hit] += (
        direction_x
        *
        (
            1.5
            +
            strength * 5
        )
    )

    velocity_y[hit] += (
        direction_y
        *
        (
            1.5
            +
            strength * 5
        )
    )

    # --------------------------------------------------------
    # Slight sideways explosion
    # --------------------------------------------------------

    velocity_x[hit] += (
        -direction_y
        *
        strength
        *
        1.2
    )

    velocity_y[hit] += (
        direction_x
        *
        strength
        *
        1.2
    )


# ============================================================
# UPDATE PARTICLES
# ============================================================

def update_particles():

    global particles_x
    global particles_y
    global velocity_x
    global velocity_y
    global particle_phase
    global particle_hue

    # ========================================================
    # ANIMATION
    # ========================================================

    particle_phase += (
        0.015 *
        particle_twinkle
    )

    # ========================================================
    # MODE: COSMIC
    # ========================================================

    if mode == 0:

        velocity_x += (
            np.cos(
                particle_phase
            )
            *
            0.012
        )

        velocity_y += (
            np.sin(
                particle_phase * 1.2
            )
            *
            0.012
        )

    # ========================================================
    # MODE: VORTEX
    # ========================================================

    elif mode == 1:

        dx = (
            particles_x
            -
            WIDTH / 2
        )

        dy = (
            particles_y
            -
            HEIGHT / 2
        )

        d = np.sqrt(
            dx * dx +
            dy * dy
        )

        d = np.maximum(
            d,
            1
        )

        velocity_x += (
            -dy / d
            *
            0.045
        )

        velocity_y += (
            dx / d
            *
            0.045
        )

    # ========================================================
    # MODE: GALAXY
    # ========================================================

    elif mode == 2:

        dx = (
            particles_x
            -
            WIDTH / 2
        )

        dy = (
            particles_y
            -
            HEIGHT / 2
        )

        d = np.sqrt(
            dx * dx +
            dy * dy
        )

        d = np.maximum(
            d,
            1
        )

        # Spiral
        velocity_x += (
            -dy / d
            *
            0.055
        )

        velocity_y += (
            dx / d
            *
            0.055
        )

        # Center gravity
        velocity_x -= (
            dx / d
            *
            0.008
        )

        velocity_y -= (
            dy / d
            *
            0.008
        )

    # ========================================================
    # MODE: STORM
    # ========================================================

    elif mode == 3:

        velocity_x += (
            np.sin(
                particle_phase * 2
            )
            *
            0.035
        )

        velocity_y += (
            np.cos(
                particle_phase * 1.7
            )
            *
            0.035
        )

    # ========================================================
    # HAND INTERACTION
    # ========================================================

    if hand_detected:

        dx = (
            particles_x
            -
            hand_x
        )

        dy = (
            particles_y
            -
            hand_y
        )

        distance = np.sqrt(
            dx * dx +
            dy * dy
        )

        distance = np.maximum(
            distance,
            1
        )

        influence = (
            HAND_RADIUS
            -
            distance
        ) / HAND_RADIUS

        influence = np.clip(
            influence,
            0,
            1
        )

        # Make influence smoother
        influence *= influence

        # ====================================================
        # OPEN PALM
        # ====================================================

        if gesture == "OPEN PALM":

            # Attraction
            velocity_x -= (
                dx / distance
                *
                influence
                *
                0.55
            )

            velocity_y -= (
                dy / distance
                *
                influence
                *
                0.55
            )

            # Swirl
            velocity_x += (
                -dy / distance
                *
                influence
                *
                0.35
            )

            velocity_y += (
                dx / distance
                *
                influence
                *
                0.35
            )

        # ====================================================
        # FIST
        # ====================================================

        elif gesture == "FIST":

            # Explosion
            velocity_x += (
                dx / distance
                *
                influence
                *
                1.8
            )

            velocity_y += (
                dy / distance
                *
                influence
                *
                1.8
            )

        # ====================================================
        # PINCH
        # ====================================================

        elif gesture == "PINCH":

            # Strong gravity
            velocity_x -= (
                dx / distance
                *
                influence
                *
                1.25
            )

            velocity_y -= (
                dy / distance
                *
                influence
                *
                1.25
            )

        # ====================================================
        # VORTEX
        # ====================================================

        elif gesture == "VORTEX":

            velocity_x += (
                -dy / distance
                *
                influence
                *
                1.35
            )

            velocity_y += (
                dx / distance
                *
                influence
                *
                1.35
            )

    # ========================================================
    # SHOCKWAVE
    # ========================================================

    update_shockwave()

    # ========================================================
    # FRICTION
    # ========================================================

    velocity_x *= 0.965
    velocity_y *= 0.965

    # ========================================================
    # LIMIT SPEED
    # ========================================================

    speed = np.sqrt(
        velocity_x ** 2
        +
        velocity_y ** 2
    )

    too_fast = (
        speed > MAX_SPEED
    )

    if np.any(too_fast):

        scale = (
            MAX_SPEED
            /
            speed[too_fast]
        )

        velocity_x[too_fast] *= scale

        velocity_y[too_fast] *= scale

    # ========================================================
    # MOVE
    # ========================================================

    particles_x += velocity_x
    particles_y += velocity_y

    # ========================================================
    # SCREEN WRAP
    # ========================================================

    particles_x %= WIDTH
    particles_y %= HEIGHT

    # ========================================================
    # COLOR MOVEMENT
    # ========================================================

    particle_hue += 0.18

    particle_hue %= 360


# ============================================================
# DRAW PARTICLES
# ============================================================

def draw_particles():

    particle_surface.fill(
        (0, 0, 0, 0)
    )

    glow_surface.fill(
        (0, 0, 0, 0)
    )

    current_time = (
        pygame.time.get_ticks()
    )

    # ========================================================
    # TINY NEON PARTICLES
    # ========================================================

    for i in range(
        NUM_PARTICLES
    ):

        x = int(
            particles_x[i]
        )

        y = int(
            particles_y[i]
        )

        # ====================================================
        # TWINKLE
        # ====================================================

        pulse = (
            math.sin(
                particle_phase[i]
                *
                particle_twinkle[i]
                +
                current_time * 0.002
            )
            +
            1
        ) * 0.5

        radius = particle_size[i]

        # ====================================================
        # COLOR
        # ====================================================

        color = pygame.Color(
            255,
            255,
            255
        )

        color.hsva = (
            float(
                particle_hue[i]
            ),
            78,
            100,
            100
        )

        r = color.r
        g = color.g
        b = color.b

        # ====================================================
        # VERY SUBTLE GLOW
        #
        # IMPORTANT:
        # This is deliberately tiny.
        # ====================================================

        if radius >= 1:

            glow_radius = max(
                2,
                int(
                    radius * 2.5
                )
            )

            pygame.draw.circle(
                glow_surface,
                (
                    r,
                    g,
                    b,
                    12
                ),
                (
                    x,
                    y
                ),
                glow_radius
            )

        # ====================================================
        # NEON CORE
        # ====================================================

        core_radius = max(
            1,
            int(
                radius
                +
                pulse * 0.35
            )
        )

        pygame.draw.circle(
            particle_surface,
            (
                r,
                g,
                b,
                240
            ),
            (
                x,
                y
            ),
            core_radius
        )

        # ====================================================
        # WHITE HOT CENTER
        # ====================================================

        if core_radius >= 2:

            pygame.draw.circle(
                particle_surface,
                (
                    245,
                    250,
                    255,
                    230
                ),
                (
                    x,
                    y
                ),
                1
            )

    # ========================================================
    # SUBTLE GLOW
    # ========================================================

    screen.blit(
        glow_surface,
        (
            0,
            0
        ),
        special_flags=pygame.BLEND_ADD
    )

    # ========================================================
    # PARTICLE CORES
    # ========================================================

    screen.blit(
        particle_surface,
        (
            0,
            0
        ),
        special_flags=pygame.BLEND_ADD
    )


# ============================================================
# DRAW LASER
# ============================================================

def draw_laser():

    if not laser_active:

        return

    if landmarks is None:

        return

    direction_x, direction_y = (
        get_laser_direction()
    )

    start_x = hand_x
    start_y = hand_y

    end_x = (
        start_x
        +
        direction_x
        *
        LASER_LENGTH
    )

    end_y = (
        start_y
        +
        direction_y
        *
        LASER_LENGTH
    )

    # ========================================================
    # OUTER GLOW
    # ========================================================

    pygame.draw.line(
        screen,
        (
            15,
            70,
            180
        ),
        (
            int(start_x),
            int(start_y)
        ),
        (
            int(end_x),
            int(end_y)
        ),
        30
    )

    # ========================================================
    # BLUE BEAM
    # ========================================================

    pygame.draw.line(
        screen,
        (
            30,
            120,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        (
            int(end_x),
            int(end_y)
        ),
        17
    )

    # ========================================================
    # BRIGHT BEAM
    # ========================================================

    pygame.draw.line(
        screen,
        (
            90,
            190,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        (
            int(end_x),
            int(end_y)
        ),
        8
    )

    # ========================================================
    # WHITE CORE
    # ========================================================

    pygame.draw.line(
        screen,
        (
            225,
            250,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        (
            int(end_x),
            int(end_y)
        ),
        3
    )

    # ========================================================
    # LASER PARTICLES
    # ========================================================

    current_time = (
        pygame.time.get_ticks()
    )

    for p in laser_particles:

        p["distance"] += p["speed"]

        if p["distance"] > LASER_LENGTH:

            p["distance"] = random.uniform(
                0,
                40
            )

            p["offset"] = random.uniform(
                -13,
                13
            )

        wave = math.sin(
            current_time * 0.012
            +
            p["phase"]
            +
            p["distance"] * 0.025
        )

        offset = (
            p["offset"]
            +
            wave * 4
        )

        x = (
            start_x
            +
            direction_x
            *
            p["distance"]
            -
            direction_y
            *
            offset
        )

        y = (
            start_y
            +
            direction_y
            *
            p["distance"]
            +
            direction_x
            *
            offset
        )

        if (
            x > -10
            and x < WIDTH + 10
            and y > -10
            and y < HEIGHT + 10
        ):

            # Tiny blue glow
            pygame.draw.circle(
                screen,
                (
                    40,
                    130,
                    255
                ),
                (
                    int(x),
                    int(y)
                ),
                2
            )

            # Tiny white center
            pygame.draw.circle(
                screen,
                (
                    210,
                    245,
                    255
                ),
                (
                    int(x),
                    int(y)
                ),
                1
            )

    # ========================================================
    # LASER MUZZLE
    # ========================================================

    pulse = (
        math.sin(
            current_time * 0.02
        )
        +
        1
    ) * 0.5

    radius = int(
        9
        +
        pulse * 5
    )

    pygame.draw.circle(
        screen,
        (
            30,
            100,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        radius * 2
    )

    pygame.draw.circle(
        screen,
        (
            100,
            200,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        radius
    )

    pygame.draw.circle(
        screen,
        (
            240,
            255,
            255
        ),
        (
            int(start_x),
            int(start_y)
        ),
        4
    )


# ============================================================
# DRAW SHOCKWAVE
# ============================================================

def draw_shockwave():

    if shockwave_strength <= 0:

        return

    alpha = int(
        180
        *
        shockwave_strength
    )

    radius = int(
        shockwave_radius
    )

    if radius <= 0:

        return

    # Outer ring
    pygame.draw.circle(
        screen,
        (
            70,
            150,
            255
        ),
        (
            int(hand_x),
            int(hand_y)
        ),
        radius,
        2
    )

    # Inner ring
    if radius > 20:

        pygame.draw.circle(
            screen,
            (
                120,
                200,
                255
            ),
            (
                int(hand_x),
                int(hand_y)
            ),
            max(
                1,
                radius - 12
            ),
            1
        )


# ============================================================
# HAND SKELETON
# ============================================================

HAND_CONNECTIONS = [

    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    (0, 17)
]


# ============================================================
# DRAW HAND
# ============================================================

def draw_hand():

    if landmarks is None:

        return

    points = []

    for lm in landmarks:

        x = int(
            lm.x
            *
            WIDTH
        )

        y = int(
            lm.y
            *
            HEIGHT
        )

        points.append(
            (
                x,
                y
            )
        )

    # ========================================================
    # COLOR BY GESTURE
    # ========================================================

    if gesture == "LASER":

        line_color = (
            70,
            190,
            255
        )

    elif gesture == "VORTEX":

        line_color = (
            180,
            100,
            255
        )

    elif gesture == "PINCH":

        line_color = (
            255,
            210,
            80
        )

    elif gesture == "FIST":

        line_color = (
            255,
            80,
            100
        )

    elif gesture == "OPEN PALM":

        line_color = (
            80,
            255,
            200
        )

    else:

        line_color = (
            100,
            170,
            255
        )

    # ========================================================
    # CONNECTIONS
    # ========================================================

    for a, b in HAND_CONNECTIONS:

        pygame.draw.line(
            screen,
            line_color,
            points[a],
            points[b],
            2
        )

    # ========================================================
    # JOINTS
    # ========================================================

    for i, point in enumerate(points):

        radius = 4

        if i == 8:

            radius = 8

        pygame.draw.circle(
            screen,
            line_color,
            point,
            radius
        )

        # Tiny white center
        if i == 8:

            pygame.draw.circle(
                screen,
                (
                    240,
                    250,
                    255
                ),
                point,
                2
            )


# ============================================================
# WEBCAM PREVIEW
# ============================================================

def draw_webcam(frame):

    preview_width = 280
    preview_height = 210

    preview = cv2.resize(
        frame,
        (
            preview_width,
            preview_height
        )
    )

    # ========================================================
    # DRAW HAND ON CAMERA PREVIEW
    # ========================================================

    if landmarks is not None:

        points = []

        for lm in landmarks:

            x = int(
                lm.x
                *
                preview_width
            )

            y = int(
                lm.y
                *
                preview_height
            )

            points.append(
                (
                    x,
                    y
                )
            )

        for a, b in HAND_CONNECTIONS:

            cv2.line(
                preview,
                points[a],
                points[b],
                (
                    255,
                    180,
                    70
                ),
                2
            )

        for i, point in enumerate(points):

            cv2.circle(
                preview,
                point,
                5 if i == 8 else 3,
                (
                    255,
                    255,
                    255
                ),
                -1
            )

    # ========================================================
    # CONVERT TO PYGAME
    # ========================================================

    rgb = cv2.cvtColor(
        preview,
        cv2.COLOR_BGR2RGB
    )

    rgb = np.transpose(
        rgb,
        (
            1,
            0,
            2
        )
    )

    surface = pygame.surfarray.make_surface(
        rgb
    )

    x = (
        WIDTH
        -
        preview_width
        -
        20
    )

    y = (
        HEIGHT
        -
        preview_height
        -
        20
    )

    # ========================================================
    # BORDER
    # ========================================================

    pygame.draw.rect(
        screen,
        (
            60,
            150,
            255
        ),
        (
            x - 3,
            y - 3,
            preview_width + 6,
            preview_height + 6
        ),
        2
    )

    screen.blit(
        surface,
        (
            x,
            y
        )
    )

    # ========================================================
    # LABEL
    # ========================================================

    label = small_font.render(
        "LIVE HAND TRACKING",
        True,
        (
            150,
            210,
            255
        )
    )

    screen.blit(
        label,
        (
            x,
            y - 21
        )
    )


# ============================================================
# UI
# ============================================================

def draw_ui():

    # ========================================================
    # TITLE
    # ========================================================

    title = title_font.render(
        "NEON PARTICLE UNIVERSE",
        True,
        (
            100,
            190,
            255
        )
    )

    screen.blit(
        title,
        (
            20,
            16
        )
    )

    # ========================================================
    # STATUS
    # ========================================================

    if hand_detected:

        status = "HAND DETECTED"

    else:

        status = "SEARCHING..."

    screen.blit(
        font.render(
            "STATUS : " + status,
            True,
            (
                170,
                210,
                240
            )
        ),
        (
            22,
            52
        )
    )

    # ========================================================
    # GESTURE
    # ========================================================

    screen.blit(
        font.render(
            "GESTURE : " + gesture,
            True,
            (
                180,
                210,
                245
            )
        ),
        (
            22,
            80
        )
    )

    # ========================================================
    # LASER
    # ========================================================

    if laser_active:

        laser_status = "LASER : ON"

        laser_color = (
            80,
            210,
            255
        )

    else:

        laser_status = "LASER : OFF"

        laser_color = (
            90,
            110,
            150
        )

    screen.blit(
        font.render(
            laser_status,
            True,
            laser_color
        ),
        (
            22,
            108
        )
    )

    # ========================================================
    # MODE
    # ========================================================

    screen.blit(
        font.render(
            "MODE : " + MODES[mode],
            True,
            (
                100,
                190,
                255
            )
        ),
        (
            22,
            136
        )
    )

    # ========================================================
    # SPEED
    # ========================================================

    screen.blit(
        small_font.render(
            f"HAND SPEED : {hand_speed:.1f}",
            True,
            (
                100,
                130,
                170
            )
        ),
        (
            22,
            164
        )
    )

    # ========================================================
    # CONTROLS
    # ========================================================

    controls = [

        "INDEX FINGER  -> LASER",

        "TWO FINGERS   -> VORTEX",

        "OPEN PALM     -> ATTRACT",

        "PINCH         -> GRAVITY",

        "FIST          -> EXPLOSION",

        "FAST MOVE     -> SHOCKWAVE",

        "",

        "SPACE -> CHANGE MODE",

        "R -> RESET PARTICLES",

        "ESC -> EXIT"
    ]

    y = HEIGHT - 190

    for text in controls:

        rendered = small_font.render(
            text,
            True,
            (
                100,
                130,
                170
            )
        )

        screen.blit(
            rendered,
            (
                22,
                y
            )
        )

        y += 18


# ============================================================
# MAIN LOOP
# ============================================================

running = True


while running:

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # ESC
            # ------------------------------------------------

            if event.key == pygame.K_ESCAPE:

                running = False

            # ------------------------------------------------
            # RESET
            # ------------------------------------------------

            elif event.key == pygame.K_r:

                reset_particles()

            # ------------------------------------------------
            # CHANGE MODE
            # ------------------------------------------------

            elif event.key == pygame.K_SPACE:

                mode += 1

                mode %= len(
                    MODES
                )

    # ========================================================
    # CAMERA FRAME
    # ========================================================

    success, frame = camera.read()

    if not success:

        continue

    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )

    # ========================================================
    # HAND DETECTION
    # ========================================================

    result = detect_hand(
        frame
    )

    if result is not None:

        normalized_x = result[0]
        normalized_y = result[1]

        landmarks = result[2]

        new_gesture = result[3]

        # ====================================================
        # TARGET SCREEN POSITION
        # ====================================================

        target_x = (
            normalized_x
            *
            WIDTH
        )

        target_y = (
            normalized_y
            *
            HEIGHT
        )

        # ====================================================
        # ADAPTIVE SMOOTHING
        # ====================================================

        dx = (
            target_x
            -
            hand_x
        )

        dy = (
            target_y
            -
            hand_y
        )

        target_distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        smoothing = (
            HAND_SMOOTHING
            +
            min(
                target_distance / 900,
                0.25
            )
        )

        smoothing = min(
            smoothing,
            0.65
        )

        hand_x += (
            target_x
            -
            hand_x
        ) * smoothing

        hand_y += (
            target_y
            -
            hand_y
        ) * smoothing

        hand_detected = True

        gesture = new_gesture

    else:

        hand_detected = False

        landmarks = None

        gesture = "NONE"

    # ========================================================
    # HAND MOVEMENT
    # ========================================================

    movement_x = (
        hand_x
        -
        previous_hand_x
    )

    movement_y = (
        hand_y
        -
        previous_hand_y
    )

    raw_speed = math.sqrt(
        movement_x ** 2
        +
        movement_y ** 2
    )

    # Smooth speed
    hand_speed += (
        raw_speed
        -
        hand_speed
    ) * 0.3

    previous_hand_x = hand_x
    previous_hand_y = hand_y

    # ========================================================
    # FAST HAND MOVEMENT -> SHOCKWAVE
    # ========================================================

    if (
        hand_detected
        and
        hand_speed > 18
        and
        shockwave_strength < 0.15
    ):

        create_shockwave()

    # ========================================================
    # LASER
    # ========================================================

    laser_active = (
        hand_detected
        and
        landmarks is not None
        and
        gesture == "LASER"
    )

    # ========================================================
    # UPDATE
    # ========================================================

    update_particles()

    # ========================================================
    # LASER PARTICLE COLLISION
    # ========================================================

    laser_collision()

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.fill(
        (
            1,
            2,
            8
        )
    )

    # ========================================================
    # PARTICLES
    # ========================================================

    draw_particles()

    # ========================================================
    # SHOCKWAVE
    # ========================================================

    draw_shockwave()

    # ========================================================
    # LASER
    # ========================================================

    if laser_active:

        draw_laser()

    # ========================================================
    # HAND
    # ========================================================

    draw_hand()

    # ========================================================
    # UI
    # ========================================================

    draw_ui()

    # ========================================================
    # WEBCAM
    # ========================================================

    draw_webcam(
        frame
    )

    # ========================================================
    # FPS
    # ========================================================

    fps_text = small_font.render(
        f"{int(clock.get_fps())} FPS",
        True,
        (
            100,
            130,
            170
        )
    )

    screen.blit(
        fps_text,
        (
            WIDTH - 70,
            18
        )
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(
        FPS
    )


# ============================================================
# CLEANUP
# ============================================================

camera.release()

try:

    hand_landmarker.close()

except Exception:

    pass

pygame.quit()

sys.exit()