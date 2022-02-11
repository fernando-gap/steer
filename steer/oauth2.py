from json import loads, JSONDecodeError


class ParseParams:
    """Parse params from a json file, a set, or by a dictionary"""

    def params_from(self, json = False, params = None):
        """ Determine how the params will be assigned"""

        if type(json) == str:
            with open(json, 'r') as file:
                params = loads(file.read())

        scopes_values = ParseParams.check_scopes(params['scopes'])

        b = [
            scopes_values,
            params['redirect_uri'],
            params['response_type'],
            params['client_id']
        ]

        return '{0}&redirect_uri={1}&response_type={2}&client_id={3}'.format(b[0], b[1], b[2], b[3])


    @classmethod
    def check_scopes(cls, scopes):
        """The scopes can be both: list or a string"""

        layout = '?scope='
        if type(scopes) is list:
           return layout + '%20'.join(scopes)

        return layout + scopes



class OAuth2(ParseParams):
    """Responsible to create the oauth2 request only"""

    __OAUTH2_URL = 'https://accounts.google.com/o/oauth2/v2/auth'


    def __init__(self, set_params = False, json = False, **params):
        """Assign values to the params variables"""
        self.uri = self.params_from(json=json, params=set_params or params)


    # TODO: implements challenge
    def create(self, challenge = False):
        """ Creates google authentication request """
        return self.uri + __OAUTH2_URL
