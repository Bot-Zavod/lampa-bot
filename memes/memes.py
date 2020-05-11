from .anecdot import anecdots
from random import choice
from os import listdir, path


def get_anecdot() -> str:
    return choice(anecdots)


def get_meme() -> str:
    img = "memes/bot_memes/" + choice(listdir("memes/bot_memes"))
    full_path = path.abspath(path.expanduser(path.expandvars(img)))
    return full_path
