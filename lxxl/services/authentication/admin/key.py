from lib import router, output, app
from model.auth import access


class Key(router.Root):

    def create(self, environ, params):
        try:
            req = app.Controller().getRequest()
            keyid = req.POST.get('keyid')
            isAdmin = req.POST.get('xxxadmin')
            hosts = req.POST.get('hosts').split(',')

            if not keyid:
                output.error('invalid format', 400)

            exists = access.KeyFactory().get(keyid)

            if exists:
                output.error('already exists', 403)

            apiKey = access.ApiKey()
            apiKey.key = keyid
            apiKey.hosts = hosts
            apiKey.generateSecret()

            if isAdmin:
                apiKey.admin = True

            access.KeyFactory().new(apiKey)

            output.success(apiKey.secret, 201)
        except app.Error:
            pass

        return app.Controller().getResponse(True)
