import concurrent.futures
import random
import re

FALLBACK_PALETTE = ["#e63946", "#457b9d", "#2a9d8f", "#f4a261"]
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def resolve_color(requested_color, fallback_index):
    """Validate a bot-supplied hex color, falling back to the default palette."""
    if isinstance(requested_color, str) and _HEX_COLOR_RE.match(requested_color):
        return requested_color
    return FALLBACK_PALETTE[fallback_index % len(FALLBACK_PALETTE)]

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

MOVE_TIMEOUT_SECONDS = 0.2  # per-bot, per-turn time budget


class Player:
    def __init__(self, pid, name, get_move_fn, start_pos, start_dir, color):
        self.id = pid
        self.name = name
        self.get_move_fn = get_move_fn
        self.pos = start_pos
        self.direction = start_dir
        self.color = color
        self.alive = True
        self.trail = [start_pos]  # includes current head as trail[-1]
        self.death_reason = None
        self.death_turn = None


def call_with_timeout(fn, arg, timeout=MOVE_TIMEOUT_SECONDS, default=None):
    """Call fn(arg) with a hard wall-clock timeout. Returns (result, error_str_or_None)."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(fn, arg)
        try:
            return future.result(timeout=timeout), None
        except concurrent.futures.TimeoutError:
            return default, "timeout"
        except Exception as e:  # noqa: BLE001 - bot code is untrusted
            return default, f"{type(e).__name__}: {e}"


class TronGame:
    def __init__(self, width=20, height=20, max_turns=500, seed=None):
        self.width = width
        self.height = height
        self.max_turns = max_turns
        self.turn = 0
        self.players = []
        self.walls = set()  # all occupied cells (any trail, any player)
        self.rng = random.Random(seed)
        self.replay = []  # list of per-turn snapshots for the viewer
        self.errors = []  # log of bot errors/timeouts, for debugging

    def add_player(self, pid, name, get_move_fn, start_pos, start_dir, color=None):
        color = resolve_color(color, pid)
        p = Player(pid, name, get_move_fn, start_pos, start_dir, color)
        self.players.append(p)
        self.walls.add(start_pos)

    def build_state_for(self, player):
        """Public state visible to a given player's bot."""
        return {
            "width": self.width,
            "height": self.height,
            "turn": self.turn,
            "you": player.id,
            "your_direction": player.direction,
            "players": {
                p.id: {
                    "name": p.name,
                    "pos": p.pos,
                    "direction": p.direction,
                    "alive": p.alive,
                    "length": len(p.trail),
                    "color": p.color,
                }
                for p in self.players
            },
            "walls": self.walls,  # set of (x, y) occupied cells
        }

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def step(self):
        """Advance the game by one turn. Returns True if the game should continue."""
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) <= 1 or self.turn >= self.max_turns:
            return False

        # 1. Ask every alive bot for a move (each gets a time budget).
        chosen = {}
        for p in alive_players:
            state = self.build_state_for(p)
            move, err = call_with_timeout(p.get_move_fn, state)
            if err is not None:
                self.errors.append(
                    {"turn": self.turn, "player": p.name, "error": err}
                )
            if move not in DIRECTIONS or move == OPPOSITE.get(p.direction):
                move = p.direction
            chosen[p.id] = move

        new_heads = {}
        for p in alive_players:
            p.direction = chosen[p.id]
            dx, dy = DIRECTIONS[p.direction]
            new_heads[p.id] = (p.pos[0] + dx, p.pos[1] + dy)

        head_counts = {}
        for pid, head in new_heads.items():
            head_counts[head] = head_counts.get(head, 0) + 1

        for p in alive_players:
            head = new_heads[p.id]
            if not self.in_bounds(head):
                p.alive = False
                p.death_reason = "hit wall (out of bounds)"
            elif head in self.walls:
                p.alive = False
                p.death_reason = "hit a trail"
            elif head_counts[head] > 1:
                p.alive = False
                p.death_reason = "head-on collision"

        for i, p1 in enumerate(alive_players):
            for p2 in alive_players[i + 1:]:
                if new_heads[p1.id] == p2.pos and new_heads[p2.id] == p1.pos:
                    p1.alive = False
                    p1.death_reason = p1.death_reason or "swap collision"
                    p2.alive = False
                    p2.death_reason = p2.death_reason or "swap collision"

        for p in alive_players:
            if p.alive:
                p.pos = new_heads[p.id]
                p.trail.append(p.pos)
                self.walls.add(p.pos)
            else:
                p.death_turn = self.turn

        self.turn += 1
        self._record_snapshot()
        return True

    def _record_snapshot(self):
        self.replay.append(
            {
                "turn": self.turn,
                "players": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "alive": p.alive,
                        "pos": p.pos,
                        "trail": list(p.trail),
                        "color": p.color,
                    }
                    for p in self.players
                ],
            }
        )

    def run(self):
        self._record_snapshot()
        while self.step():
            pass
        return self.result()

    def result(self):
        alive = [p for p in self.players if p.alive]
        candidates = alive if alive else self.players
        max_len = max((len(p.trail) for p in candidates), default=0)
        winners = [p for p in candidates if len(p.trail) == max_len]
        tie = len(winners) > 1

        return {
            "winners": [w.name for w in winners],
            "tie": tie,
            "turns_played": self.turn,
            "standings": sorted(
                (
                    {
                        "name": p.name,
                        "alive": p.alive,
                        "length": len(p.trail),
                        "death_reason": p.death_reason,
                        "death_turn": p.death_turn,
                    }
                    for p in self.players
                ),
                key=lambda r: (-r["alive"], -r["length"]),
            ),
            "errors": self.errors,
        }


DEFAULT_START_DIRS = ["RIGHT", "LEFT", "DOWN", "UP"]


def default_start_positions(width, height, n):
    """Spread up to 4 players across the corners of the grid."""
    margin = 2
    corners = [
        (margin, margin),
        (width - 1 - margin, height - 1 - margin),
        (width - 1 - margin, margin),
        (margin, height - 1 - margin),
    ]
    return corners[:n]


def play_match(bots, width=20, height=20, max_turns=500, seed=None):
    assert 2 <= len(bots) <= 4, "Tron Arena supports 2-4 players per match"
    game = TronGame(width=width, height=height, max_turns=max_turns, seed=seed)
    positions = default_start_positions(width, height, len(bots))
    for i, entry in enumerate(bots):
        name, fn, color = entry
        game.add_player(i, name, fn, positions[i], DEFAULT_START_DIRS[i], color=color)
    result = game.run()
    return result, game
