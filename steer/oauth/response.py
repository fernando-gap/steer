
class OAuth2Response:
    
    def __init__(self, res):
        
        from datetime import datetime, timedelta
        self.access_token = res['access_token']
        self.refresh_token = res['refresh_token']
        
        # save expires date
        self.expires_in = res['expires_in']
        self.before_expires = datetime.now()
        
    def get_tokens(self):
        return [self.access_token, self.refresh_token]

    def is_expired(self):
        """Verify whether the current token is expired"""

        
        self.when_expires = self.before_expires + timedelta(
                          seconds=self.expires_in)

        if datetime.now() > self.when_expires:
            return True

        return False
