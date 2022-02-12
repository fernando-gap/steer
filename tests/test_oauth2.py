from steer.oauth2 import OAuth2, ParseParams
import test_data


import unittest as ut

class TestParseParams(ut.TestCase):

    def setUp(self):
        self.parse_params = ParseParams()



    def test_check_scopes_equals(self):

        d_ls = [
            'https://www.googleapis.com/auth/scopes1',
            'https://www.googleapis.com/auth/scopes2',
            'https://www.googleapis.com/auth/scopes3',
            'https://www.googleapis.com/auth/scopes4',
        ]

        d_res = f'?scope={d_ls[0]}%20{d_ls[1]}%20{d_ls[2]}%20{d_ls[3]}'
        d_str = f'{d_ls[0]}%20{d_ls[1]}%20{d_ls[2]}%20{d_ls[3]}'

        self.assertEqual(ParseParams.check_scopes(d_ls), d_res)
        self.assertEqual(ParseParams.check_scopes(d_str), d_res)



    def test_check_scopes_exc_raises(self):
        with self.assertRaises(TypeError):
            ParseParams.check_scopes(False)

        with self.assertRaises(TypeError):
            ParseParams.check_scopes(True)

        with self.assertRaises(TypeError):
            ParseParams.check_scopes(None)

        with self.assertRaises(TypeError):
            ParseParams.check_scopes(())

        with self.assertRaises(TypeError):
            ParseParams.check_scopes({})



    def test_parse_from(self):
        json = self.parse_params.params_from('./test_data/data.json')
        want = "?scope=https://www.googleapis.com/auth/scopes&redirect_uri=http://localhost:port&response_type=code&client_id=your_client_id"

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
        want = "https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.googleapis.com/auth/scopes&redirect_uri=http://localhost:port&response_type=code&client_id=your_client_id"

        self.assertEqual(TestOAuth2.oauth2.create(), want)

if __name__ == '__main__':
    ut.main()
