from time import time

OT_NAME = "TR1"
BOT_COLOR = "#9e0a0a"

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
    start = time()
    me = state["players"][state["you"]]
    x, y = me["pos"]
    walls = state["walls"]
    width, height = state["width"], state["height"]

    best_move, best_score = None, -1
    for direction, (dx, dy) in MOVES.items():
        nx, ny = x + dx, y + dy
        if not (0 <= nx < width and 0 <= ny < height) or (nx, ny) in walls:
            continue
        score = count_open_neighbors((nx, ny), walls | {(nx, ny)}, width,
                                     height)
        if score > best_score:
            best_move, best_score = direction, score
    print(time() - start)
    return best_move or "UP"
