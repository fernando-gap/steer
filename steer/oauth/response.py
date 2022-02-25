
class OAuth2Response:
    
    def __init__(self, res):
        
        from datetime import datetime
        self.access_token = res['access_token']

        # sometimes refresh tokens do not exist
        if 'refresh_token' in res:
            self.refresh_token = res['refresh_token']
        
        # save expires date
        self.expires_in = res['expires_in']
        self.before_expires = datetime.now()
        
    def is_expired(self):
        """Verify whether the current token is expired"""

        from datetime import timedelta, datetime
        
        self.when_expires = self.before_expires + timedelta(
                          seconds=self.expires_in)

        if datetime.now() > self.when_expires:
            return True

        return False
