import turtle
import math
import random

# Screen
screen = turtle.Screen()
screen.bgcolor("black")

# Turtle
t = turtle.Turtle()
t.speed(0)
t.hideturtle()
t.pensize(1)

# Colors
colors = [
    "#ff0055",
    "#ff00ff",
    "#7a00ff",
    "#00e5ff",
    "#00ff88",
    "#ffea00",
    "#ff6600",
    "#ffffff"
]

# Draw the heart
for i in range(120):
    t.penup()
    t.goto(0, 0)

    angle = i * (math.pi * 2) / 120

    x = 16 * (math.sin(angle) ** 3) * 22

    y = (
        13 * math.cos(angle)
        - 5 * math.cos(2 * angle)
        - 2 * math.cos(3 * angle)
        - math.cos(4 * angle)
    ) * 12

    # Random color
    c = random.choice(colors)
    t.color(c)

    t.pendown()
    t.goto(x, y)

    # Create the dotted/zigzag effect
    for _ in range(8):
        t.forward(6)
        t.backward(6)
        t.right(45)
turtle.done()