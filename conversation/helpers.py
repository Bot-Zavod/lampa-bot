from typing import List


def to_regex(reply_keyboard: List[str]) -> str:
    result: str = "^("

    for i in reply_keyboard:
        for j in range(len(i)):
            result += str(i[j])
            if j < len(i) - 1:
                result += "|"

    result += ")$"
    return result
