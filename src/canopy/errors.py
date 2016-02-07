class CanopyError(Exception):
    pass

class MethodNotImplementedError(CanopyError):
    def __init__(self, method):
        super(MethodNotImplementedError, self).__init__("Method {} is not implemented".format(method))
