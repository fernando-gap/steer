from json import loads, JSONDecodeError
import webbrowser as browser

class ParseParams:

    def params_from(self, json = False, params = None):
        """ Determine how the params will be assigned"""

        if type(json) == str:
            with open(json, 'r') as file:
                params = loads(file.read())

        self.client_id = '&client_id=' + params['client_id']
        self.redirect_uri = '&redirect_uri=' + params['redirect_uri']
        self.response_type = '&response_type=' + params['response_type']

        return (ParseParams.check_scopes(params['scopes'])
                + self.redirect_uri
                + self.response_type
                + self.client_id)



    @staticmethod
    def check_scopes(scopes):
        """The scopes can be both: list or a string"""

        layout = '?scope='
        if type(scopes) is list:
           return layout + '%20'.join(scopes)

        return layout + scopes



class OAuth2(ParseParams):

    def __init__(self, set_params = False, json = False, **params):
        """Assign values to the params variables"""

        self.code_challenge = None
        self.uri = self.params_from(json=json, params=set_params or params)
        self._oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'


    def create(self, challenge = None):
        """ Creates google authentication request """

        if challenge is None: 
            return self._oauth_url + self.uri 

        self.code_challenge = challenge
        return self._oauth_url + self.uri + self.code_challenge.method()


    def open(self):
        """Open the oauth url on user's default browser"""
        try:
            browser.open(OAuth2.create(self, self.code_challenge))

        except browser.Error:
            return OAuth2.create(self, self.code_challenge)
    
    
    def acesstoken(self, *, secret, code): 
        """Return a OAuth2CodeExchange factory"""
        # read secret from a file
         
        self.code = '?response_code=' + code
        return OAuth2CodeExchange(self.client_id, 
                                  self.redirect_uri,
                                  self.code,
                                  self.code_challenge,
                                  secret)



class OAuth2CodeExchange:

    def __init__(self, client_id, 
                 redirect_uri, 
                 response_code,
                 code_verifier,
                 client_secret):
        
        # check whether a code challenge exists
        if code_verifier is None:
            self.code_verifier = ''
        else:
            self.code_verifier = '&code_verifier=' + code_verifier.get_method()

        self.client_secret = '&client_secret=' + client_secret
        self._access_token_url = 'https://oauth2.googleapis.com/token'

        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.response_code = response_code


    def exchange(self, grant_type = 'authorization_code'):
        """Create OAuth2 URI access token exchange"""

        return (_access_token_url
                + '?code=' + self.response_code
                + '&grant_type=' + grant_type
                + self.client_id
                + self.client_secret
                + self.redirect_uri
                + self.code_verifier)

