BOT_NAME = "TR1"
BOT_COLOR = "#9e0a0a"

MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
MOVES_REVERSE = list(MOVES.keys())
MOVES_REVERSE.reverse()


def count_open_neighbors(pos, walls, width, height):
    x, y = pos
    count = 0
    visited = [(x, y)]
    neighbours = [(x, y)]
    iter = 3000
    
    while neighbours != [] and iter > 0:
        x, y = neighbours.pop(0)
        for dx, dy in MOVES.values():
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls
                    and (nx, ny) not in visited):
                neighbours.append((nx, ny))
                visited.append((nx, ny))
                count += 1
            iter -= 1
    return count


def get_move(state):
    me = state["players"][state["you"]]
    x, y = me["pos"]
    walls = state["walls"]
    width, height = state["width"], state["height"]

    best_move, best_score = None, -1
    # if y < int(height / 2):
    for direction in MOVES.keys():
        nx, ny = x + MOVES[direction][0], y + MOVES[direction][1]
        if not (0 <= nx < width and 0 <= ny < height) or (nx, ny) in walls:
            continue
        score = count_open_neighbors((nx, ny), walls | {(nx, ny)}, width, height)
        if score > best_score:
            best_move, best_score = direction, score
    return best_move or "UP"
