from hashlib import sha256
from base64 import urlsafe_b64encode
from string import ascii_letters, digits
from secrets import choice

class IMethod:
    def method(self):
        raise NotImplemented

    def get_method(self):
        raise NotImplemented


class S256(IMethod):

    def __init__(self):
        self.codestr = '&code_challenge='
        self.codemethod = '&code_challenge_method=S256'


    @classmethod
    def randstring(cls):
        """Create a ramdom string of 128 digits"""

        chars = ascii_letters.join(digits).join(['-', '.', '_', '~'])
        chars_list = [letter for letter in chars]
        chars_list.sort()

        entropy = ''.join(choice(chars_list) for i in range(128))
        return entropy


    def method(self):
        """Implements method S256"""

        randstr = S256.randstring()
        hash256 = sha256()
        hash256.update(bytes(randstr, 'ascii'))

        b64 = urlsafe_b64encode(hash256.digest())
        self.code_challenge = b64.decode('utf-8').removesuffix('=')

        return  self.codestr + self.code_challenge + self.codemethod


    def get_method(self):
        return self.code_challenge
