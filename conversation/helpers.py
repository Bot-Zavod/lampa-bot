from typing import List


def to_regex(reply_keyboard: List[str]) -> str:
    result: str = "^("

    for i in reply_keyboard:
        for j in i:
            result += j
            result += "|"
    result = result[:-1]+ ")$"
    return result