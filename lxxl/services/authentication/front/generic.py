from lxxl.lib import router, output, auth, app
from lxxl.lib.app import Error, Controller


class Generic(router.Root):

    def check(self, environ, params):
        try:
            authent = auth.Auth()
            authent.check(auth.DIGEST_AUTH)
            output.authenticated()
        except app.Error:
            pass

        return app.Controller().getResponse(True)
