from lib import router, output
from lib.app import Error, Controller


class Activities(router.Root):

    def list(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)
