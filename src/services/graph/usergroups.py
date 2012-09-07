from lib import router, output
from lib.app import Error, Controller


class UserGroups(router.Root):

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

    def addUser(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def removeUser(self, environ, params):
        try:
            output.success('woooohooooo', 200)
        except Error:
            pass

        return Controller().getResponse(True)
