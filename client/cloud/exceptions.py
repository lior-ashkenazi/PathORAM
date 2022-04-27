class ErrorInCloudMap(Exception):
    def __init__(self, message, cause=None):
        super(ErrorInCloudMap, self).__init__(message)
        self._cause = cause
