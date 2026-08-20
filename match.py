import argparse
import datetime
import os
import random

from bot_loader import BotLoadError, load_bot
from engine import play_match
from viewer import save_replay_html

REPLAYS_DIR = os.path.join(os.path.dirname(__file__), "replays")
LOG_PATH = os.path.join(os.path.dirname(__file__), "bracket_log.txt")

SUDDEN_DEATH_MAX_ROUNDS = 5
SUDDEN_DEATH_MIN_DIM = 10
SUDDEN_DEATH_SHRINK = 3
SUDDEN_DEATH_MIN_TURNS = 100


def run_with_tiebreak(bots, width, height, max_turns, seed, max_rounds=SUDDEN_DEATH_MAX_ROUNDS):
    notes = []
    result, game = play_match(bots, width=width, height=height, max_turns=max_turns, seed=seed)
    round_bots = bots
    round_num = 0

    while result["tie"] and round_num < max_rounds:
        round_num += 1
        tied_names = set(result["winners"])
        round_bots = [b for b in round_bots if b[0] in tied_names]
        if len(round_bots) < 2:
            break 
        round_bots = round_bots[1:] + round_bots[:1] 
        width = max(SUDDEN_DEATH_MIN_DIM, width - SUDDEN_DEATH_SHRINK)
        height = max(SUDDEN_DEATH_MIN_DIM, height - SUDDEN_DEATH_SHRINK)
        max_turns = max(SUDDEN_DEATH_MIN_TURNS, max_turns // 2)
        seed = (seed or 0) + round_num * 1000 + 7
        note = (f"Tied between {', '.join(b[0] for b in round_bots)} -> sudden-death round "
                f"{round_num} on a {width}x{height} board, {max_turns}-turn limit")
        print(f"  -> {note}")
        notes.append(note)
        result, game = play_match(round_bots, width=width, height=height, max_turns=max_turns, seed=seed)

    if result["tie"]:
        tiebreak_seed = (seed or 0) + 99999
        chosen = random.Random(tiebreak_seed).choice(result["winners"])
        note = (f"Still tied after {round_num} sudden-death round(s) between "
                f"{', '.join(result['winners'])} -> broke the tie at random "
                f"(seed={tiebreak_seed}): {chosen} advances")
        print(f"  -> {note}")
        notes.append(note)
        result = dict(result)
        result["winners"] = [chosen]
        result["tie"] = False
        result["tie_broken_by_coinflip"] = True

    return result, game, notes


def main():
    parser = argparse.ArgumentParser(description="Run a single Tron Bot Arena match.")
    parser.add_argument("bot_files", nargs="+", help="2-4 bot .py file paths")
    parser.add_argument("--width", type=int, default=20)
    parser.add_argument("--height", type=int, default=20)
    parser.add_argument("--max-turns", type=int, default=500)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--label", default=None, help="Optional label for this match (e.g. 'Quarterfinal 1')")
    parser.add_argument("--no-tiebreak", action="store_true",
                         help="Don't auto-resolve ties with sudden death - just report the tie as-is")
    args = parser.parse_args()

    if not (2 <= len(args.bot_files) <= 4):
        parser.error("provide 2-4 bot files")

    bots = []
    for path in args.bot_files:
        try:
            name, get_move_fn, color = load_bot(path)
        except BotLoadError as e:
            parser.error(str(e))
        bots.append((name, get_move_fn, color))

    label = args.label or " vs ".join(b[0] for b in bots)
    print(f"Running: {label}")

    notes = []
    if args.no_tiebreak:
        result, game = play_match(bots, width=args.width, height=args.height,
                                   max_turns=args.max_turns, seed=args.seed)
    else:
        result, game, notes = run_with_tiebreak(
            bots, width=args.width, height=args.height,
            max_turns=args.max_turns, seed=args.seed,
        )

    print(f"\nTurns played (final round): {result['turns_played']}")
    if result["tie"]:
        print(f"Result: TIE between {', '.join(result['winners'])}")
    else:
        tag = " (tie broken by coin flip)" if result.get("tie_broken_by_coinflip") else ""
        print(f"Winner: {result['winners'][0]}{tag}")

    print("\nStandings (final round):")
    for s in result["standings"]:
        status = "alive" if s["alive"] else f"died turn {s['death_turn']} ({s['death_reason']})"
        print(f"  {s['name']:<20} length={s['length']:<5} {status}")

    if result["errors"]:
        print(f"\n{len(result['errors'])} bot error(s)/timeout(s) occurred during the final round:")
        for err in result["errors"][:5]:
            print(f"  turn {err['turn']} - {err['player']}: {err['error']}")

    os.makedirs(REPLAYS_DIR, exist_ok=True)
    safe_label = label.replace(" ", "_").replace("/", "-")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    replay_path = os.path.join(REPLAYS_DIR, f"{safe_label}_{timestamp}.html")
    save_replay_html(game, replay_path, title=label)
    print(f"\nReplay saved: {replay_path}")
    if notes:
        print("(Replay shows only the final, deciding round - not any earlier sudden-death rounds.)")

    with open(LOG_PATH, "a") as f:
        if result["tie"]:
            winner_str = f"TIE ({', '.join(result['winners'])})"
        else:
            winner_str = result["winners"][0]
        f.write(
            f"[{timestamp}] {label} | players: {', '.join(b[0] for b in bots)} "
            f"| winner: {winner_str} | turns: {result['turns_played']}\n"
        )
        for note in notes:
            f.write(f"    note: {note}\n")
    print(f"\nLogged to {LOG_PATH}")


if __name__ == "__main__":
    main()
