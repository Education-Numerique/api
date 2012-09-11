from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller


class Revisions(router.Root):

    def publish(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def fetch(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def delete(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)
