from anecdot import anecdots
from random import choice
from os import listdir, path

def get_anecdot() -> str:
    return choice(anecdots)

def get_mem() -> str:
    img = "mems/bot_mems/" + choice(listdir("mems/bot_mems"))
    full_path = path.abspath(path.expanduser(path.expandvars(img)))
    return full_path

# print(get_mem())