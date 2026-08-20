"""Shared helper to import a bot .py file and pull out its BOT_NAME, BOT_COLOR, get_move."""
import importlib.util
import os


class BotLoadError(Exception):
    pass


def load_bot(path):
    """
    Load a single bot module from a file path.
    Returns (name, get_move_fn, color_or_None).
    Raises BotLoadError if the file can't be imported or is missing get_move().
    """
    if not os.path.isfile(path):
        raise BotLoadError(f"no such file: {path}")

    modname = f"bots.{os.path.splitext(os.path.basename(path))[0]}"
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:  # noqa: BLE001 - bot code is untrusted
        raise BotLoadError(f"{path} failed to import: {e}") from e

    if not hasattr(module, "get_move"):
        raise BotLoadError(f"{path} has no get_move() function")

    name = getattr(module, "BOT_NAME", os.path.splitext(os.path.basename(path))[0])
    color = getattr(module, "BOT_COLOR", None)
    return name, module.get_move, color
