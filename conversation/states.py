from enum import Enum


class States(Enum):
    NONE = 000
    IDLE = 1
    IN_PAYMENT = 2
    FRUIT = 100
    SOUND = 101
    ANIMAL = 102
    CONSENT = 103
    READY = 104
    BEFORE_CHAT = 200
    STICKERS = 201
    STICKERS_ANSW = 202
    IN_CONNECTION = 300
    CURRENT_MOOD = 401
    WHY_LEAVE = 402
    FUNNY = 500
    FUNNY_ANSW = 501
