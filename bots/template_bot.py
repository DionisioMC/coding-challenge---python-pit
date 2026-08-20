"""
Copy this file, rename it (e.g. bots/bot_yourname.py), and fill it in.

Rules reminder:
- state["walls"] is a set of (x, y) cells you must NOT move into (they're
  occupied by a trail - yours or an opponent's).
- state["players"][state["you"]]["pos"] is your current head position.
- Grid is state["width"] x state["height"], with (0, 0) at the top-left.
- You must return one of "UP", "DOWN", "LEFT", "RIGHT".
- You get ~0.2 seconds to respond. If you crash or time out, your snake
  just keeps going straight.
"""

BOT_NAME = "Template Bot"
BOT_COLOR = "#f4a261"  # hex color, e.g. "#ff00ff" - shown as your snake's color in replays

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

    # Example: pick any move that doesn't immediately kill us.
    for direction, (dx, dy) in MOVES.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
            return direction

    # No safe move exists - we're trapped. Doesn't matter what we return.
    return "UP"
