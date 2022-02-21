import unittest as ut
from steer.oauth.api import OAuth2, _ParseParams, OAuth2CodeExchange


class TestParseParams(ut.TestCase):

    def setUp(self):
        self.parse_params = _ParseParams()



    def test_check_scopes_equals(self):

        d_ls = [
            'https://www.googleapis.com/auth/scopes1',
            'https://www.googleapis.com/auth/scopes2',
            'https://www.googleapis.com/auth/scopes3',
            'https://www.googleapis.com/auth/scopes4',
        ]

        d_res = f'?scope={d_ls[0]}%20{d_ls[1]}%20{d_ls[2]}%20{d_ls[3]}'
        d_str = f'{d_ls[0]}%20{d_ls[1]}%20{d_ls[2]}%20{d_ls[3]}'

        self.assertEqual(_ParseParams.check_scopes(d_ls), d_res)
        self.assertEqual(_ParseParams.check_scopes(d_str), d_res)



    def test_check_scopes_exc_raises(self):
        with self.assertRaises(TypeError):
            _ParseParams.check_scopes(False)

        with self.assertRaises(TypeError):
            _ParseParams.check_scopes(True)

        with self.assertRaises(TypeError):
            _ParseParams.check_scopes(None)

        with self.assertRaises(TypeError):
            _ParseParams.check_scopes(())

        with self.assertRaises(TypeError):
            _ParseParams.check_scopes({})



    def test_parse_from(self):
        json = self.parse_params.params_from('./test_data/data.json')
        want = ("?scope=https://www.googleapis.com/auth/scopes"
                "&redirect_uri=http://localhost:port"
                "&response_type=code&client_id=your_client_id")

        from json import loads

        self.assertEqual(json, want)

        with open('./test_data/data.json') as file:
            json = file.read()


        sets = self.parse_params.params_from(params=loads(json))
        self.assertEqual(sets, want)



    def test_parse_exc_raises(self):
        from json import JSONDecodeError
        with self.assertRaises(FileNotFoundError):
            self.parse_params.params_from('./test_data/noexist')

        with self.assertRaises(TypeError):
            self.parse_params.params_from(params=False)

        with self.assertRaises(TypeError):
            self.parse_params.params_from()



class TestOAuth2(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.oauth2 = OAuth2(json='test_data/data.json')
        
    
    def test_create(self):
        result = ('https://accounts.google.com/o/oauth2/v2/auth?'
                'scope=https://www.googleapis.com/auth/scopes'
                '&redirect_uri=http://localhost:port'
                '&response_type=code&client_id=your_client_id')

        self.assertEqual(self.oauth2.create(), result)


    def test_accesstoken(self):
        instance = self.oauth2.accesstoken(code="oauth_code")
        self.assertIsInstance(instance, OAuth2CodeExchange)


    def test_revokeaccess(self):
        revoke = self.oauth2.revokeaccess(refresh_token='refresh_token')
        result = 'https://oauth2.googleapis.com/revoke?token=' \
                 'refresh_token'

        self.assertEqual(revoke, result)

    
    def test_refresh_tokens(self):
        refresh = self.oauth2.refreshtokens('secret', 'tokens')
        
        result = 'https://oauth2.googleapis.com/token?grant_type=refresh_token' \
                 '&client_id=your_client_id' \
                 '&client_secret=secret' \
                 '&refresh_token=tokens'


        self.assertEqual(refresh, result)


class TestOAuth2CodeExchange(ut.TestCase):

    def test_no_code_challenge_exchange(self):
        #test without code_verifier
        oauth2 = OAuth2(json='./test_data/data.json')
        oauth2.create()
        exchange = oauth2.accesstoken('code')
        ex = exchange.exchange(secret='secret')

        result = 'https://oauth2.googleapis.com/token' \
                 '?grant_type=authorization_code' \
                 '&code=code' \
                 '&client_id=your_client_id' \
                 '&redirect_uri=http://localhost:port' \
                 '&client_secret=secret' \

        self.assertEqual(ex, result)


    def test_code_challenge_exchange(self):
        # test when json holds client secret
        oauth = OAuth2(json='test_data/data-1.json')
        oauth.create()
        ex = oauth.accesstoken('code')
        token = ex.exchange()
        expected ='https://oauth2.googleapis.com/token' \
                  '?grant_type=authorization_code' \
                  '&code=code' \
                  '&client_id=your_client_id' \
                  '&redirect_uri=http://localhost:port' \
                  '&client_secret=secret' \

        self.assertEqual(token, expected)


if __name__ == '__main__':
    ut.main()
