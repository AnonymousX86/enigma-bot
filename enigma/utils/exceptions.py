from builtins import BaseException


class EnigmaError(BaseException):
    def __init__(self, traceback=''):
        message = 'Bot global exception'
        BaseException.__init__(self, 'EnigmaError: ' + (traceback if traceback else message))


class NoError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'There\'s no such error, this exception is used only for testing purpose'
        EnigmaError.__init__(self, 'NoError: ' + (traceback if traceback else message))


class DatabaseError(EnigmaError):
    def __init__(self, traceback=''):
        message = 'Error with database'
        EnigmaError.__init__(self, 'DatabaseError: ' + (traceback if traceback else message))
