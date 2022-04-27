class WrongPassword(Exception):
    def __init__(self, message, cause=None):
        super(WrongPassword, self).__init__(message)
        self._cause = cause


class KeyMapError(Exception):
    def __init__(self, message, cause=None):
        super(KeyMapError, self).__init__(message)
        self._cause = cause


class DummyFileFound(Exception):
    pass


class InvalidToken(Exception):
    pass
