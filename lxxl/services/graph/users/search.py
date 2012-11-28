from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller


class Search(router.Root):

    def fetch(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)
