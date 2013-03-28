from lxxl.lib import output, utils
from lxxl.lib.storage import Db, DbError, DESCENDING, ASCENDING
from lxxl.lib.config import Config
from hashlib import md5
import datetime


class User:

    def __init__(self, **entries):
        self.uid = None
        self.seq = None
        self.username = None
        self.firstname = None
        self.lastname = None
        self.email = None
        self.activate = 0
        self.activation_code = None
        self.friends_count = 0
        self.hasAvatar = False
        self.date = None
        self.premium = False
        self.connect = {}
        self.level = 1
        self.password_reminder = None

        self.__dict__.update(entries)

        #clear exclude fields
        try:
            del self.friends
        except:
            pass

    def makeAdmin(self):
        self.level = 3

    def makeAuthor(self):
        self.level = 1

    def makeReviewer(self):
        self.level = 2

    def toObject(self):
        obj = self.__dict__.copy()

        if '_id' in obj:
            del obj['_id']

        obj['uid'] = str(obj['uid'])
        return obj

    def addConnect(self, type, id):
        self.connect[type] = id

        if hasattr(self, '_id') and self._id:
            return

        try:
            Db().get('users').ensure_index([
                ('connect.%s' % type, DESCENDING)],
                {
                    'unique': True,
                    'background': False,
                    'sparse': True,
                    'dropDups': True
                })

            Db().get('users').update(
                {'uid': self.uid},
                {'$set': {'connect.%s' % type: id}}
            )
        except DbError:
            output.error('cannot access db', 503)

    def hasConnect(self, type):
        if type in self.connect and self.connect[type]:
            return True

    def getProfile(self):
        Db().get('profile').ensure_index(
            [('uid', ASCENDING)],
            {'background': True}
        )
        profile = Db().get('profile').find_one({'uid': self.uid})

        if profile:
            return profile

        return {
            'uid': self.uid,
            'updated': datetime.datetime.utcnow(),
            'datas': {}
        }

    def generateActivationCode(self):
        self.activation_code = utils.randomBase62()

    def generatePasswordReminder(self):
        self.password_reminder = utils.randomBase62()

    def generateUid(self, id):
        self.seq = id
        self.uid = md5(str(id).encode('utf-8')).hexdigest()


class Factory:

    @staticmethod
    def get(search):
        try:
            if isinstance(search, str):
                search = {'uid': search}
            else:
                tmp = {}
                for (key, value) in search.items():
                    tmp[key] = value.lower()
                search = tmp
                del tmp

            data = Db().get(
                'users').find_one(search, {'friends': {'$slice': 0}})

        except DbError:
            output.error('cannot access db', 503)

        if data is None:
                return None

        return User(**data)

    @staticmethod
    def getAllUsers():
        data = Db().get('users').find({'activate': 1, 'seq': {
                                       '$gt': 0}}, {'friends': {'$slice': 0}})
        result = []
        for friend in data:
            result.append(User(**friend))

        total = data.count()
        return (result, total)

    @staticmethod
    def setAvatar(uid, value):
        Db().get('users').update(
            {'uid': uid},
            {'$set': {'hasAvatar': value}}
        )

    @staticmethod
    def new(obj):
        #Db().get('users').ensure_index([('username', storage.DESCENDING)], { 'unique' : True, 'background' : False, 'dropDups' : True })
        Db().get('users').ensure_index([('uid', DESCENDING)
                                        ], {'unique': True, 'background': False, 'dropDups': True})
        Db().get('users').ensure_index([('email', DESCENDING)
                                        ], {'unique': True, 'background': False, 'dropDups': True})
        Db().get('users').ensure_index([('connect.facebook', DESCENDING)], {'unique': True, 'background': False, 'sparse': True, 'dropDups': True})

        c = Db().get('users')

        try:
            id = c.insert(obj.__dict__, True)
            obj._id = id
        except Exception as e:
            e = '%s' % e
            err = e
            if 'username' in e:
                err = 'username'
            elif 'email' in e:
                err = 'email'

            raise Duplicate(err)

        return obj


class Duplicate(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
