
class _ParseParams:

    def params_from(self, json = False, params = None):
        """ Determine how the params will be assigned"""
        from json import loads

        if type(json) == str:
            with open(json, 'r') as file:
                params = loads(file.read())

        self.client_id = '&client_id=' + params['client_id']
        self.redirect_uri = '&redirect_uri=' + params['redirect_uri']
        self.response_type = '&response_type=' + params['response_type']

        if 'client_secret' in params:
            self.client_secret = params['client_secret']
        else:
            self.client_secret = ''


        return (_ParseParams.check_scopes(params['scopes'])
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



class OAuth2(_ParseParams):

    def __init__(self, set_params = False, json = False, **params):
        """Assign values to the params variables"""

        self.uri = self.params_from(json=json, params=set_params or params)
        self._oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'


    def create(self, challenge = None):
        """ Creates google authentication request """

        if challenge == None:
            self.code_challenge = None
            return self._oauth_url + self.uri

        self.code_challenge = challenge
        return self._oauth_url + self.uri + self.code_challenge.method()


    def open(self):
        """Open the oauth url on user's default browser"""

        import webbrowser as browser

        try:
            browser.open(OAuth2.create(self, self.code_challenge))

        except browser.Error:
            return OAuth2.create(self, self.code_challenge)


    def accesstoken(self, code):
        """Return a OAuth2CodeExchange factory"""
        return OAuth2CodeExchange(self, code)


    def revokeaccess(self, **token):
        """URL to revoke users' access"""
        for k in token:
            if k == 'refresh_token' or k == 'access_token':
                return 'https://oauth2.googleapis.com/revoke?token=' \
                    + token[k]


    def refreshtokens(self, secret, refresh_token):
        return ('https://oauth2.googleapis.com/token?grant_type=refresh_token'
                + self.client_id
                + '&client_secret=' + secret
                + '&refresh_token=' + refresh_token)


class OAuth2CodeExchange:

    def __init__(self, oauth2, code):

        self.oauth2 = oauth2
        self.code = '&code=' + code


    def exchange(self, secret = ''):
        """Create OAuth2 URI access token exchange"""

        if self.oauth2.code_challenge == None:
            self.oauth2.code_challenge = ''
        else:
           self.oauth2.code_challenge = '&code_verifier=' + self.oauth2.code_challenge.get_method()

        return ('https://oauth2.googleapis.com/token' \
                '?grant_type=authorization_code'
                + self.code
                + self.oauth2.client_id
                + self.oauth2.redirect_uri
                + '&client_secret=' + secret + self.oauth2.client_secret
                + self.oauth2.code_challenge)
