
class _ParseParams:

    def _create_url_params(self, params):
        """Create URL params into a dictionary"""

        self.params = params
        url_params = ''

        # multiple scopes only if exist the prop and it is a list
        if 'scope' in params:
            if type(params.get('scope')) is list:
               params['scope'] = '%20'.join(params['scope'])

        is_first_param = 0
        for field, value in params.items():
            if is_first_param == 0:

                url_params += f'?{field}={value}'
                is_first_param += 1
            else:
                url_params += f'&{field}={value}'

        return url_params


class OAuth2(_ParseParams):

    def __init__(self, dict_params = False, json_path = False, **params):
        """Assign values to the params variables"""

        self._oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'

        if json_path != False:
            from json import loads
            with open(json_path, 'r') as file:
                params = loads(file.read())

        self.params = params
        self.code_challenge = ''

        if type(dict_params) is dict:
            self.params = dict_params


    def create(self, challenge = ''):
        """ Creates google authentication request URL for Desktop APPS.

        To create an oauth url it needs the following attributes:

        :client_id
        :scope
        :response_type
        :redirect_uri

        The support provided is the Loopbakc IP address which is
        recommended by google.
        """
        
        valid = ['client_id', 'scope', 'response_type', 'redirect_uri']
        create_params = self.params.copy()
        
        # check if all valid keys exists
        for key in valid:
            if key not in create_params:
                raise KeyError(f'{key} is missing')
        
        # invalid attributes are removed
        for key in self.params:
            if key not in valid:
                create_params.pop(key)

            
        # assign self.params to use the params provided by the user
        # and store the params to create the url    
        params = self._create_url_params(create_params)


        if challenge == '':
            return self._oauth_url + params

        self.code_challenge = challenge
        return self._oauth_url + params + self.code_challenge.method()


    def open(self):
        """Open the oauth url on user's default browser"""

        import webbrowser as browser

        try:
            browser.open(OAuth2.create(self, self.code_challenge))

        except browser.Error:
            return OAuth2.create(self, self.code_challenge)


    # Do not return a factory instead return the rusult of OAuth2CodeExchange.exchange()
    def accesstoken(self, code, secret = None):
        """Create an oauth2 code exchange URL.

        Arguments:
        :code: str -- A code response given by google
        :secret: str -- A client OAuth2 secret (optional)

        To create an Exchange Authorization Token it needs the 
        following attributes:

            :client_id
            :client_secret
            :code
            :code_verifier (optional)
            :grant_type
            :redirect_uri
        """

        # to avoiding changing self.params
        params_copy = self.params.copy()
        params_copy.pop('scope')
        params_copy.pop('response_type')

        if 'client_secret' not in self.params and secret != None:
            params_copy.update({'client_secret': secret})
        else:
            raise TypeError('client secret was not provided')

        params_copy.update({
            'code': code,
            'grant_type': 'authorization_code'
        })
        return OAuth2CodeExchange(params_copy, self.code_challenge).exchange()


    def revokeaccess(self, **token):
        """URL to revoke users' access"""
        for k in token:
            if k == 'refresh_token' or k == 'access_token':
                return 'https://oauth2.googleapis.com/revoke?token=' \
                    + token[k]


    # Do not read from the params try to read from the params dictionary first
    def refreshtokens(self, refresh_token, secret = ''):

        refresh_params = self.params.copy()

        # remove uneeded keys
        refresh_params.pop('redirect_uri')
        refresh_params.pop('response_type')
        refresh_params.pop('scope')

        # check if a secret is already defined
        if 'client_secret' not in self.params:
            refresh_params.update({'client_secret': secret})

        refresh_params.update({'refresh_token': refresh_token})
        refresh_params.update({'grant_type': 'refresh_token'})
        params = self._create_url_params(refresh_params)

        return 'https://oauth2.googleapis.com/token' + params


# inherit the _ParseParams class
class OAuth2CodeExchange(_ParseParams):

    def __init__(self, oauth, challenge = ''):

        from json import loads

        # in case oauth is json
        if type(oauth) is str:
            with open(oauth) as file:
                oauth = file.read()
                
        self.oauth = oauth
        self.code_verifier = challenge


    def exchange(self):
        """Create OAuth2 URI access token exchange"""

        if type(self.code_verifier) is not str:
            self.oauth.update({'code_verifier': self.code_verifier.get_method()})

        return ('https://oauth2.googleapis.com/token' \
                + self._create_url_params(self.oauth))
