import re
from typing import Any, Union, List

chars = {
    'bitcoin': '\u20bf'
}


def strip_emoji(text: str) -> str:
    re_emoji = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    return re_emoji.sub(r'', text)


def fixed_width(text: str, width: int = 20, remove_emoji: bool = True):
    if remove_emoji is True:
        temp = text
        text = strip_emoji(temp)

    if len(text) == width:
        return text
    elif len(text) > width:
        return text[:width - 3] + '...'
    else:
        while len(text) < width:
            text += ' '
        return text


def separate_value(value: int, separator: str = ' ') -> str:
    result = ''
    n = str(value)
    for c in range(1, len(n) + 1):
        result += n[-c]
        if c % 3 == 0:
            result += separator
    return result[::-1]


def upper_name(name: str):
    if ' ' not in name:
        return f'{name[0].upper()}{name[1:]}'
    else:
        result = ''
        i = 0
        while True:
            if i >= len(name):
                return result
            elif i == 0:
                result += name[0].upper()
                i += 1
            elif name[i] == ' ':
                result += name[i:i + 2].upper()
                i += 2
            else:
                result += name[i]
                i += 1


def safe_lower(value: Union[str, Any]) -> Union[str, Any]:
    if type(value) is str:
        return value.lower()
        pass
    else:
        return value


def sort_nested_list(nested_list: List[List], key_pos: int = 0) -> List[List]:
    nested_list.sort(key=lambda x: safe_lower(x[key_pos]))
    return nested_list


def number_suffix(num: int):
    return "st" if str(num)[-1] == "1" else "nd" if str(num)[-1] == "2" else "rd" if str(num)[-1] == "3" else "th"


def f_btc(num: int) -> str:
    return f'{round(num*0.0001, 4)} {chars["bitcoin"]}'
