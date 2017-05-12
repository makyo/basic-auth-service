"""AioHTTP middlewares."""

from aiohttp import (
    web,
    BasicAuth,
)


class BaseBasicAuthMiddlewareFactory:
    """A middleware for handling Basic Authentication."""

    def __init__(self, realm):
        self.realm = realm

    def is_valid_auth(self, user, password):
        """Return whether the basic authentication si valid.

        It should be overridden by subclasses.
        """
        return False

    async def __call__(self, app, handler):
        """Return the middleware handler."""

        async def middleware_handler(request):
            if not self._validate_auth(request):
                headers = {
                    'WWW-Authenticate': 'Basic realm="{}"'.format(self.realm)}
                return web.HTTPUnauthorized(headers=headers)

            return await handler(request)

        return middleware_handler

    def _validate_auth(self, request):
        """Validate Basic-Auth in a request."""
        basic_auth = request.headers.get('Authorization')
        if not basic_auth:
            return False

        auth = BasicAuth.decode(basic_auth)
        return self.is_valid_auth(auth.login, auth.password)


class BasicAuthMiddlewareFactory(BaseBasicAuthMiddlewareFactory):
    """Basic-Auth middleware fetching authentication from a collection."""

    def __init__(self, realm, collection):
        super().__init__(realm)
        self.collection = collection

    def is_valid_auth(self, user, password):
        return self.collection.credentials_match(user, password)
