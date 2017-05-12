"""Testing utilities."""

import json

import asynctest

from aiohttp import (
    web,
    BasicAuth,
    streams,
)
from aiohttp.helpers import sentinel
from aiohttp.test_utils import make_mocked_request


def basic_auth_header(user, password):
    """Return a dict with the basic-auth header key and value."""
    return {'Authorization': BasicAuth(user, password).encode()}


def get_request(app, path='/', method='GET', content=None,
                auth=None, content_type=None, headers=None,
                json_encode=True):
    """Create a test request.

    The `auth` parameter for Basic-Authentication can be provided as tuple with
    (user, password).

    If `json_encode` is set to False, the content is not converted to JSON (in
    which case it should be bytes).

    """
    if headers is None:
        headers = {}
    if auth is not None:
        headers.update(basic_auth_header(*auth))

    if json_encode and content is None:
        content = {}

    if content is not None:
        payload = streams.StreamReader(loop=app.loop)
        if json_encode:
            data = json.dumps(content).encode('utf-8')
        else:
            data = content
        payload.feed_data(data)
        payload.feed_eof()
        headers.update(
            {'Content-Type': 'application/json',
             'Content-Length': str(len(data))})
    else:
        payload = sentinel

    if content_type is not None:
        headers['Content-Type'] = content_type

    return make_mocked_request(
        method, path, app=app, payload=payload, headers=headers)


class HandlerTestCase(asynctest.TestCase):
    """Test class for testing direct calls to HTTP handlers."""

    def setUp(self):
        super().setUp()
        self.app = self.create_app()

    def create_app(self):
        return web.Application()

    def get_request(self, *args, **kwargs):
        """Create a test request."""
        return get_request(self.app, *args, **kwargs)

    async def make_request(self, *args, **kwargs):
        """Make a request through the application.

        Arguments are passed directly to get_request().

        """
        request = self.get_request(*args, **kwargs)
        info = await self.app.router.resolve(request)
        return await info.handler(request)
