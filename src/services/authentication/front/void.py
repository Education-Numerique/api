from lib import router, output
from lib.app import Error, Controller


class Void(router.Root):

    def check(self, environ, params):
        try:
            output.authenticated()
        except Error:
            pass

        return Controller().getResponse(True)
