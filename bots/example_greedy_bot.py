"""
A step up from random: avoids moves that lead into an immediate dead end
by checking how many escape routes each candidate move leaves.
"""

BOT_NAME = "Greedy Bot"
BOT_COLOR = "#457b9d"

MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


def count_open_neighbors(pos, walls, width, height):
    x, y = pos
    count = 0
    for dx, dy in MOVES.values():
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
            count += 1
    return count


def get_move(state):
    me = state["players"][state["you"]]
    x, y = me["pos"]
    walls = state["walls"]
    width, height = state["width"], state["height"]

    best_move, best_score = None, -1
    for direction, (dx, dy) in MOVES.items():
        nx, ny = x + dx, y + dy
        if not (0 <= nx < width and 0 <= ny < height) or (nx, ny) in walls:
            continue
        # Prefer moves that leave us the most open space next turn.
        score = count_open_neighbors((nx, ny), walls | {(nx, ny)}, width, height)
        if score > best_score:
            best_move, best_score = direction, score

    return best_move or "UP"
