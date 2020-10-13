import re

from .exceptions import FewArgumentsError

chars = {
    'bitcoin': '\u20bf'
}


def strip_emoji(text: str):
    """Remove emoji from text"""
    if len(text) != 0:
        re_emoji = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
        return re_emoji.sub(r'', text)
    else:
        raise FewArgumentsError


def fixed_width(text: str, width: int = 20, remove_emoji: bool = True):
    """Shorten or extend string to exact width"""
    if len(text) > 0:
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
    else:
        raise FewArgumentsError


def separate_value(value: int, separator: str = ' '):
    """Add separator to big integers"""
    if value > 0:
        result = ''
        n = str(value)
        for c in range(1, len(n) + 1):
            result += n[-c]
            if c % 3 == 0:
                result += separator
        return result[::-1]
    else:
        raise FewArgumentsError


def upper_name(name: str):
    """Make First Letters Capitalize"""
    if name:
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
    else:
        raise FewArgumentsError


def safe_lower(value):
    """Save value as lowercase if it's string for sure"""
    if value:
        if type(value) is int:
            return value.lower()
            pass
        else:
            return value
    else:
        raise FewArgumentsError


def sort_nested_list(nested_list: list, key_pos: int = 0):
    """Sort list by key in nested list"""
    if nested_list:
        nested_list.sort(key=lambda x: safe_lower(x[key_pos]))
        return nested_list
    else:
        raise FewArgumentsError
