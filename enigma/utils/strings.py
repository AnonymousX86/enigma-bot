import re
from typing import Any, Union, List

chars = {
    'bitcoin': '\u20bf'
}


def strip_emoji(text: str) -> str:
    """Removes emoji from text.

    :param text: Text from which emojis should be removed.
    :return: Text without emojis.
    """
    re_emoji = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    return re_emoji.sub(r'', text)


def fixed_width(text: str, width: int = 20, remove_emoji: bool = True):
    """Shortens or extends string to exact width. Optionally removes emojis.

    :param text: Text to shrink or extend.
    :param width: Fixed text width.
    :param remove_emoji: Tells if emojis should be removed or not.
    :return: Formatted text with fixed width and optionally without emojis.
    """
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
    """Adds separator to big integers.

    :param value: Value to format.
    :param separator: Separator.
    :return: Formatted value.
    """
    result = ''
    n = str(value)
    for c in range(1, len(n) + 1):
        result += n[-c]
        if c % 3 == 0:
            result += separator
    return result[::-1]


def upper_name(name: str):
    """Makes first letters upper case. Not like CamelStyle but Every Single Word With Spaces.

    :param name: Text to capitalize.
    :return: Formatted text.
    """
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
    """Saves value as lowercase only if it's string.

    :param value: Text or Any to make lowercase.
    :return: Lowercase text.
    """
    if type(value) is str:
        return value.lower()
        pass
    else:
        return value


def sort_nested_list(nested_list: List[List], key_pos: int = 0) -> List[List]:
    """Sorts list by key in nested list.

    :param nested_list: Nested list.
    :param key_pos: Sorting key position.
    :return: Sorted nested list.
    """
    nested_list.sort(key=lambda x: safe_lower(x[key_pos]))
    return nested_list


def number_suffix(num: int):
    return "st" if str(num)[-1] == "1" else "nd" if str(num)[-1] == "2" else "rd" if str(num)[-1] == "3" else "th"
