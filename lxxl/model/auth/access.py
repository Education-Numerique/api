from lxxl.lib import storage, output
from lxxl.lib.config import Config
import python_digest
import random
import hashlib


class ApiKey:

    def __init__(self, **entries):
        self.key = None
        self.secret = None
        self.admin = False

        self.hosts = []

        self.__dict__.update(entries)

    def generateSecret(self):
        random.seed()
        rnd = str(random.getrandbits(128))
        self.secret = hashlib.sha1(rnd.encode('utf-8')).hexdigest()


class KeyFactory:

    def get(self, key):

        try:
            data = None
            data = storage.Memcache().get(key, 'access')
        except Exception:
            pass

        if not data:
            try:
                storage.Db().get('auth_access').ensure_index(
                    [('key', storage.ASCENDING)],
                    {'unique': True, 'background': True}
                )

                data = storage.Db().get('auth_access').find_one({"key": key})
                storage.Memcache().set(key, data, 'access')
            except storage.DbError:
                output.error('cannot access db', 503)
            except:
                pass

        if not data:
            return None

        return ApiKey(**data)

    def new(self, obj):
        c = storage.Db().get('auth_access')

        id = c.insert(obj.__dict__)
        obj._id = id
        print(id)

        return obj
