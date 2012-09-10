from lib import router, output, auth
from lib.app import Error, Controller


class Anonymous(router.Root):

    def check(self, environ, params):
        try:
            authent = auth.Auth()
            authent.check(auth.ANONYM_AUTH)
            output.authenticated()
        except Error:
            pass

        return Controller().getResponse(True)
