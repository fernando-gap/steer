from json import loads, JSONDecodeError
import webbrowser as browser

class ParseParams:

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

    def __init__(self, set_params = False, json = False, **params):
        """Assign values to the params variables"""

        self.uri = self.params_from(json=json, params=set_params or params)
        self._oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'


    def create(self, challenge = None):
        """ Creates google authentication request """

        if challenge is None: 
            self.oauthurl = self._oauth_url + self.uri 
            return self.oauthurl


        self.oauthurl = self._oauth_url + self.uri + challenge.method()
        return self.oauthurl


    def open(self):
        """Open the oauth url on user's default browser"""
        try:
            browser.open(self.oauthurl)

        except browser.Error:
            print('browser error')
    

