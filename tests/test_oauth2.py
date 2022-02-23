import unittest as ut
from steer.oauth.api import OAuth2, _ParseParams, OAuth2CodeExchange
import json

class TestParseParams(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        """Read all input data and outupt data for the class"""

        with open('test_oauth2/fixture.json') as inputdata:
            cls.input = json.loads(inputdata.read())

        with open('test_oauth2/expected.json') as outputdata:
            cls.output = json.loads(outputdata.read())


    def setUp(self):
        self.params = _ParseParams()


    def test_scopes(self):

        # test if scope is a list
        input_ = self.input['iscopes']['a']
        output = self.output['oscopes']['a']
        self.assertEqual(self.params._create_url_params(input_), output)


        # test if scope is not a list
        input_ = self.input['iscopes']['b']
        output = self.output['oscopes']['b']
        self.assertEqual(self.params._create_url_params(input_), output)

    
    def test_params(self):
        input_ = self.params._create_url_params(self.input['iscopes']['c'])
        output= self.output['oscopes']['c']
        
        self.assertEqual(input_, output)


class TestOAuth2(ut.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('test_oauth2/fixture.json') as inputdata:
            cls.input = json.loads(inputdata.read())
        
        with open('test_oauth2/expected.json') as output:
            cls.output = json.loads(output.read())
    

    def test_create(self):
        # load json config
        auth_json = OAuth2(json_path='test_oauth2/data.json')

        # use a config dict instead
        auth_dict = OAuth2(dict_params=self.input['ioauth2']['a'])

        # use dictionary arguments
        auth_args = OAuth2(client_id='client_id',
                           response_type='code',
                           scope='scope',
                           redirect_uri='redirect_uri'
                           )

        output = self.output['o_auth2']['a']

        self.assertEqual(auth_json.create(), output)
        self.assertEqual(auth_dict.create(), output)
        self.assertEqual(auth_args.create(), output)

    def test_accesstoken(self):
        auth = OAuth2(self.input['ioauth2']['b'])
        output = self.output['o_auth2']['b']

        self.assertEqual(auth.accesstoken('code'), output)

        # test passing secret as argument
        del auth.params['client_secret']
        self.assertEqual(auth.accesstoken('code', 'client_secret'), output)


    def test_revokeaccess(self):
        auth = OAuth2(json_path='test_oauth2/data.json')
        revoke = auth.revokeaccess(refresh_token='refresh_token')
        result = 'https://oauth2.googleapis.com/revoke?token=refresh_token'

        self.assertEqual(revoke, result)

    
    def test_refresh_tokens(self):
        auth = OAuth2(json_path='test_oauth2/data.json')
        refresh_url = auth.refreshtokens('refresh_token', 'client_secret')
        output = self.output['o_auth2']['c']


        self.assertEqual(refresh_url, output)

if __name__ == '__main__':
    ut.main()
