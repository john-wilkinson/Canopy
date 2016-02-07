from errors import MethodNotImplementedError

class IOInterface(object):
    QUIET = 1
    NORMAL = 2
    VERBOSE = 4
    VERY_VERBOSE = 8
    DEBUG = 16

    def write(self):
        raise MethodNotImplementedError('write')

    def write_error(self):
        raise MethodNotImplementedError('write_error')

    def overwrite(self):
        raise MethodNotImplementedError('overwrite')

    def overwrite_error(self):
        raise MethodNotImplementedError('overwrite_error')

    def ask(self):
        raise MethodNotImplementedError('ask')

    def ask_confirmation(self):
        raise MethodNotImplementedError('ask_confirmation')

    def ask_and_validate(self):
        raise MethodNotImplementedError('ask_and_validate')

    def ask_and_hide_answer(self):
        raise MethodNotImplementedError('ask_and_hide_answer')

    def get_authentication(self):
        raise MethodNotImplementedError('get_authentication')

    def has_authentication(self):
        raise MethodNotImplementedError('has_authentication')

    def set_authentication(self):
        raise MethodNotImplementedError('set_authentication')

    def load_configuration(self):
        raise MethodNotImplementedError('load_configuration')
