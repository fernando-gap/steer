import unittest as ut
from steer import OAuth2Response

class TestOAuthResponse(ut.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.google_response = {
            'access_token': '1/fFAGRNJru1FTz70BzhT3Zg',
            'refresh_token': '1//xEoDL4iW3cxlI7yDbSRFYNG01kVKM2C-259HOF2aQb',
            'expires_in': 3500
        }

        cls.res = OAuth2Response(cls.google_response, save=False)


    def test_get_tokens(self):
        tokens = self.res.get_tokens()
        result = [self.google_response['access_token'],
                  self.google_response['refresh_token']]

        self.assertEquals(tokens, result)


    def test_is_expired(self):
        # test if is expired
        self.res.expires_in = -3500
        self.assertEquals(self.res.is_expired(), True)

        # test if is not expired
        self.res.expires_in = 3500
        self.assertEquals(self.res.is_expired(), False)



if __name__ == '__main__':
    ut.main()
