# Python Pit

Write a Python bot that slythers through a 2D matrix. Leave a trail
behind you, avoid crashing into walls, trails, or other pythons, and
be the last one standing.

## The rules

- Game plays in a 2D 20x20 matrix, `(0, 0)` is the top-left corner.
- Every turn, all alive bots choose a direction simultaneously:
  `"UP"`, `"DOWN"`, `"LEFT"`, or `"RIGHT"`.
- Your snake moves one cell in that direction and leaves a permanent
  trail behind (every cell you've ever occupied becomes a wall).
- You die if you: leave the grid, hit any trail (yours or an
  opponent's), or crash head-on into another snake.
- You can't reverse 180 degrees in one move (if you're going RIGHT,
  choosing LEFT is ignored and you keep going straight).
- Last snake alive wins.

## Writing your bot

1. Copy `Campus_bots/template_bot.py` to `Campus_bots/your_campus/bot_yourlogin.py`.
2. Set `BOT_NAME` to whatever you want displayed in replays (be respectful).
3. Set `BOT_COLOR` to the color your snake will be drawn, in hex format (e.g.`"#ff00ff"`)
4. Implement `get_move(state)`, it must return one of either: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`.

You get about 0.2 seconds per turn. If your bot crashes, throws an
exception, or takes too long, it continues moving in a straight line.

### The `state` dict you receive

```python
{
  "width": 20, "height": 20,
  "turn": 42, #Number of elapsed turns
  "you": 0, #Player ID
  "your_direction": "RIGHT",
  "players": {
    0: {"name": "...", "pos": (5, 7), "direction": "RIGHT", "alive": True, "length": 43},
    1: {"name": "...", "pos": (14, 3), "direction": "DOWN", "alive": True, "length": 43},
    ...
  },
  "walls": {(0, 0), (1, 0), ...}  #Occupied cells
}
```

`state["players"][state["you"]]["pos"]` is always your current head
position.

## Testing your Bot

Matches are run by compiling match.py with two bots from the Campus_bots/ directory.
The bots position is based on the command line compilation, first one starts top left and second one starts bottom right.
A --label flag can be added for keeping track of matches.
A --width and --height flag can be used to change the arena.

```bash
python3 match.py Campus_bots/bot_rogde-so.py Campus_bots/bot_r-garcia.py --label "Example Match"
```

Supports maximum 4 bots per match (just for fun):

```bash
python3 match.py Campus_bots/bot_a.py Campus_bots/bot_b.py Campus_bots/bot_c.py Campus_bots/bot_d.py --width 50 --height 50 --label "Free-for-all"
```

Each run prints the result, appends one line to `bracket_log.txt`, and writes an HTML replay to `replays/`. 
Just double-click any `.html` file to watch the match play out in your browser.

## Included example bots (for reference / warm-up)

- `Campus_bots/example_random_bot.py`: moves randomly among safe directions.
  This is the weakest possible bot, beating it is the bare minimum.
- `Campus_bots/example_greedy_bot.py`: picks whichever safe move leaves it
  the most open neighboring space. A reasonable mid-tier opponent.

## Submitting your Bot

Before submitting make sure of the following:
- The file name must include the intra username of all developers.
- The file is saved inside the correct Campus_bots folder.
- The bot has been tested and functions properly.
- The bot doesn't need any other dependencies.

To submit:
- Make sure not to edit any other file except your own bot.
- Fork the repository - Open the repository page and click "Fork", then "Create fork".
- Clone your fork.
- Work on a branch - Commit whenever you reach something that works.
- Push and open the pull request.
- The submission will be reviewed before being accepted.