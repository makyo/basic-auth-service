"""Basic-auth credentials."""

from collections import namedtuple
import random
import string
import hashlib


_BasicAuthCredentials = namedtuple(
    'BasicAuthCredentials', ['username', 'password'])


class BasicAuthCredentials(_BasicAuthCredentials):
    """Basic authorization credentials."""

    @classmethod
    def generate(cls):
        """Generate random BasicAuthCredentials."""
        return cls(generate_random_token(), generate_random_token())

    @classmethod
    def from_token(cls, token):
        """Create BasicAuthCredentials from a "user:password" token."""
        split = token.split(':')
        if len(split) != 2 or '' in split:
            raise ValueError(
                'Token must be in the form "user:password"')
        return cls(*split)

    def __str__(self):
        return '{}:{}'.format(self.username, self.password)


def generate_random_token(length=20):
    """Generate a random string to use as token."""
    choices = string.ascii_letters + string.digits
    return "".join(random.choice(choices) for _ in range(length))


def hash_token(token):
    """Return the hashed version of a token."""
    return hashlib.sha1(token.encode('utf-8')).hexdigest()


def match_token(token, hashsum):
    """Return whether a token matches an hash."""
    return hash_token(token) == hashsum
