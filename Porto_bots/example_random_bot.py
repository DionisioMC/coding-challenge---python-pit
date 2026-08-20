import random

BOT_NAME = "Random Bot"
BOT_COLOR = "#e63946"

MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


def get_move(state):
    me = state["players"][state["you"]]
    x, y = me["pos"]
    walls = state["walls"]
    width, height = state["width"], state["height"]

    safe = []
    for direction, (dx, dy) in MOVES.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
            safe.append(direction)

    return random.choice(safe) if safe else "UP"
