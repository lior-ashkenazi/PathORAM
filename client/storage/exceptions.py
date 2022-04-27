class NoSelectedNode(Exception):
    def __init__(self, message, cause=None):
        super(NoSelectedNode, self).__init__(message)
        self._cause = cause


class DownloadFileError(Exception):
    def __init__(self, message, cause=None):
        super(DownloadFileError, self).__init__(message)
        self._cause = cause


class FileSizeError(Exception):
    def __init__(self, message, cause=None):
        super(FileSizeError, self).__init__(message)
        self._cause = cause


class DummyFileFound(Exception):
    def __init__(self, message, cause=None):
        super(DummyFileFound, self).__init__(message)
        self._cause = cause


class FullStorage(Exception):
    def __init__(self, message, cause=None):
        super(FullStorage, self).__init__(message)
        self._cause = cause


class FileNotInStorage(Exception):
    def __init__(self, message, cause=None):
        super(FileNotInStorage, self).__init__(message)
        self._cause = cause
