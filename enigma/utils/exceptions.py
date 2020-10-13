from builtins import BaseException


class EnigmaError(BaseException):
    def __init__(self, traceback=''):
        message = 'Bot global exception'
        BaseException.__init__(self, 'EnigmaError: ' + (traceback if traceback != '' else message))


class NoError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'There\'s no such error, this exception is used only for testing purpose'
        EnigmaError.__init__(self, 'NoError: ' + (traceback if traceback != '' else message))


class FewArgumentsError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'Provided to little arguments'
        EnigmaError.__init__(self, 'FewArgumentsError: ' + (traceback if traceback != '' else message))


class StatsError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'Can\'t update user\'s stats'
        EnigmaError.__init__(self, 'StatsError: ' + (traceback if traceback != '' else message))


class DatabaseError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'Error with database'
        EnigmaError.__init__(self, 'DatabaseError: ' + (traceback if traceback != '' else message))


class ConnectionThrottle(DatabaseError):
    def __init__(self, traceback=''):
        message = 'Connection throttling, can\'t connect to database'
        DatabaseError.__init__(self, 'ConnectionThrottle: ' + (traceback if traceback != '' else message))


class UserStatusError(DatabaseError):
    def __init__(self, traceback=''):
        message = 'Specific user raised an error, while changing their status'
        DatabaseError.__init__(self, 'UserStatusError: ' + (traceback if traceback != '' else message))


class WebError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'Error while accessing web'
        EnigmaError.__init__(self, 'UrlError: ' + (traceback if traceback != '' else message))


class ImageError(WebError):
    def __init__(self, traceback=''):
        message = 'Cannot get image'
        WebError.__init__(self, 'ImageError: ' + (traceback if traceback != '' else message))
