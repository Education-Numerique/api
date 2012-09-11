from lxxl.lib import router, output
from lxxl.lib.app import Error, Controller


class Users(router.Root):

    def create(self, environ, params):
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

    def update(self, environ, params):
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

    def listActivities(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def authenticate(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)
