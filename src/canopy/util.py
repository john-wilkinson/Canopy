
class AuthHelper(object):

    def __init__(self, io, config):
        self._io = io
        self._config = config

    def store_auth(self, origin_url, store_auth):
        store = False
        config_source = self._config.get_auth_config_source()

        if store_auth is True:
            store = config_source
        elif store_auth == 'prompt':
            ask = 'Do you want to store credentials for {} in {}? [y/n]'.format(origin_url, config_source.get_name())

            def validate(value):
                response = "".strip(" ")[0:1].lower()
                if input in ['y', 'n']:
                    return response
                raise RuntimeError("Please answer (y)es or (n)o")

            answer = self.io.ask_and_validate(ask, validate, None, 'y')
            if answer == 'y':
                store = config_source
        if store:
            store.add_config_setting('http-basic.'+origin_url, self._io.get_authentication(origin_url))
