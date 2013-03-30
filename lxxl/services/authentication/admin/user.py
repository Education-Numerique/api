from lxxl.lib import router, output, storage, app
from lxxl.lib.config import Config
from lxxl.model.auth import users


class User(router.Root):

    def findByLogin(self, environ, params):
        try:
            user = users.Factory.get(params['login'])

            if not user:
                output.error('unknown acess', 404)

            resp = app.Controller().getResponse()
            resp.status = 200
            resp.text = '{"uid" : "%s", "activate" : %s  }' % (
                user.uid,
                int(user.activate)
            )
        except app.Error:
            pass

        return app.Controller().getResponse(True)

    def create(self, environ, params):
        try:
            req = app.Controller().getRequest()
            uid = req.POST.get('uid')
            login = req.POST.get('login')
            password = req.POST.get('password')

            if not uid or not login or not password:
                output.error('invalid format', 400)

            user = users.User()
            user.uid = uid
            user.login = login.lower()
            user.realm = Config().get('realm')
            user.activate = 0
            user.setDigest(password)

            users.Factory.new(user)

            output.success('user created', 201)
        except app.Error:
            pass

        return app.Controller().getResponse(True)

    def update(self, environ, params):
        try:
            req = app.Controller().getRequest()
            uid = req.POST.get('uid')
            login = req.POST.get('login')
            password = req.POST.get('password')

            if not uid or not login or not password:
                output.error('invalid format', 400)

            login = login.lower()
            user = users.Factory.get(login)

            if (not user) or (user.uid != uid):
                output.error('unknown acess', 404)

            user.setDigest(password)
            storage.Db().get('auth_users').update({
                'login': login,
                'uid': uid
            }, user)

            storage.Memcache().delete(login, 'auth')
            output.success('user updated', 200)
        except app.Error:
            pass

        return app.Controller().getResponse(True)

    def activate(self, environ, params):
        try:
            req = app.Controller().getRequest()
            uid = req.POST.get('uid')
            login = req.POST.get('login')

            if not uid or not login:
                output.error('invalid format', 400)

            login = login.lower()
            user = users.Factory.get(login)

            if (not user) or (user.uid != uid):
                output.error('unknown access', 404)

            user.activate = 1

            storage.Db().get('auth_users').update({
                'login': login,
                'uid': uid
            }, user)

            storage.Memcache().delete(login, 'auth')

            output.success('user activated', 200)
        except app.Error:
            pass

        return app.Controller().getResponse(True)

    def password(self, environ, params):
        try:
            req = app.Controller().getRequest()
            uid = req.POST.get('uid')
            login = req.POST.get('login')

            if not uid or not login:
                output.error('invalid format', 400)

            login = login.lower()
            user = users.Factory.get(login)

            if (not user) or (user.uid != uid):
                output.error('unknown acess', 404)

            user.activate = 0

            storage.Db().get('auth_users').update({
                'login': login,
                'uid': uid
            }, user)

            storage.Memcache().delete(login, 'auth')

            output.success('user deactivated', 200)

        except app.Error:
            pass

        return app.Controller().getResponse(True)

    def deactivate(self, environ, params):
        try:
            req = app.Controller().getRequest()
            uid = req.POST.get('uid')
            login = req.POST.get('login')

            if not uid or not login:
                output.error('invalid format', 400)

            login = login.lower()
            user = users.Factory.get(login)

            if (not user) or (user.uid != uid):
                output.error('unknown acess', 404)

            user.activate = 0

            storage.Db().get('auth_users').update({
                'login': login,
                'uid': uid
            }, user)

            storage.Memcache().delete(login, 'auth')

            output.success('user deactivated', 200)

        except app.Error:
            pass

        return app.Controller().getResponse(True)
