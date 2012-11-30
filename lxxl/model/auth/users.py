from lxxl.lib import storage, output
from lxxl.lib.config import Config
from hashlib import sha1
import python_digest


class User:

    def __init__(self, **entries):
        self.uid = None
        self.login = None
        self.realm = None
        self.digest = None
        self.activate = 0

        self.__dict__.update(entries)

    def setDigest(self, password):
        self.digest = python_digest.calculate_partial_digest(
            self.login.lower(), self.realm, password)

    def getToken(self):
        salt = "%s%s" % (
            self.uid,
            Config().get('token_secret')
        )

        return "%s:%s" % (self.uid, sha1(salt.encode('utf-8')).hexdigest())


class Factory:

    @staticmethod
    def get(login):
        login = login.lower()
        try:
            data = None
            data = storage.Memcache().get(login, 'auth')

        except Exception:
            pass

        if not data:

            try:
                storage.Db().get('auth_users').ensure_index(
                    [('login', storage.ASCENDING)],
                    {'unique': True, 'background': True}
                )

                storage.Db().get('auth_users').ensure_index(
                    [('uid', storage.DESCENDING)],
                    {'unique': False, 'background': True}
                )

                if login == 'anonymous':
                    data = Factory.getAnonymous().__dict__
                else:
                    data = storage.Db().get('auth_users').find_one(
                        {"login": login}
                    )

                storage.Memcache().set(login, data, 'auth')
            except storage.DbError:
                output.error('cannot access db', 503)
            except:
                pass

        if not data:
            return None

        return User(**data)

    @staticmethod
    def getAnonymous():
        user = User()
        user.login = 'anonymous'
        user.realm = Config().get('realm')
        user.activate = 1
        user.setDigest('860b9dbbda6ee5f71ddf3b44e54c469e')

        return user

    @staticmethod
    def new(obj):
        c = storage.Db().get('auth_users')

        id = c.insert(obj.__dict__)
        obj._id = id

        return obj
