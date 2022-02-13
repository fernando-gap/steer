from datetime import datetime, timedelta

class OAuth2Response:

    def __init__(self, res, *, save):
        self.access_token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expires_in = res['expires_in']
        
    def get_tokens(self):
        return [self.access_token, self.refresh_token]

    def is_expired(self):
        """Verify whether the current token is expired"""

        before_expires = datetime.now()
        when_expires = before_expires + timedelta(
                          seconds=self.expires_in)

        if before_expires > when_expires:
            return True

        return False
