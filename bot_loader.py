import importlib.util
import os


class BotLoadError(Exception):
    pass


def load_bot(path):
    if not os.path.isfile(path):
        raise BotLoadError(f"no such file: {path}")

    modname = f"bots.{os.path.splitext(os.path.basename(path))[0]}"
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise BotLoadError(f"{path} failed to import: {e}") from e

    if not hasattr(module, "get_move"):
        raise BotLoadError(f"{path} has no get_move() function")

    name = getattr(module, "BOT_NAME", os.path.splitext(os.path.basename(path))[0])
    color = getattr(module, "BOT_COLOR", None)
    return name, module.get_move, color
