from lxxl.lib import output, utils
from lxxl.lib.storage import Db, DbError
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

        self.__dict__.update(entries)

        #clear exclude fields
        try:
            del self.friends
        except:
            pass

    def addConnect(self, type, id):
        self.connect[type] = id

        if hasattr(self, '_id') and self._id:
            return

        try:
            Db().get('users').ensure_index([
                ('connect.%s' % type, storage.DESCENDING)],
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
            [('uid', storage.ASCENDING)],
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

    def generateUid(self, id):
        self.seq = id
        self.uid = md5(str(id).encode('utf-8')).hexdigest()


class FriendFactory:

    def getFriends(self, uid, start=0, limit=10):
        try:
            Db().get('users').ensure_index(
                [('friends.uid', storage.ASCENDING)], {'background': True})
            friends = Db(
            ).get('users').find_one({'uid': uid}, {'friends.uid': 1})

            if not friends:
                return ([], 0)

            if 'friends' not in friends:
                return ([], 0)

            list = []
            for friend in friends['friends']:
                list.append(friend['uid'])

            data = Db().get('users').find({
                'uid': {"$in": list},
                'activate': 1,
                'friends.uid': uid,
                'activate': 1
            }, {'friends': {'$slice': 0}})

            total = data.count()
            data = data.skip(start).limit(limit)

            result = []
            for friend in data:
                result.append(User(**friend))

            return (result, total)

        except DbError:
            output.error('cannot access db', 503)

    def getMyRequests(self, uid, start=0, limit=10):
        try:
            Db().get('users').ensure_index(
                [('friends.uid', storage.ASCENDING)], {'background': True})

            friends = Db(
            ).get('users').find_one({'uid': uid}, {'friends.uid': 1})

            if not friends:
                return ([], 0)

            if 'friends' not in friends:
                return ([], 0)

            list = []
            for friend in friends['friends']:
                list.append(friend['uid'])
            data = Db().get('users').find({
                'uid': {"$in": list},
                'activate': 1,
                'friends.uid': {'$nin': [uid]},
                'activate': 1
            }, {'friends': {'$slice': 0}})

            total = data.count()
            data = data.skip(start).limit(limit)

            result = []
            for friend in data:
                result.append(User(**friend))

            return (result, total)

        except DbError:
            output.error('cannot access db', 503)

    def getFriendRequests(self, uid, start=0, limit=10):
        try:
            Db().get('users').ensure_index(
                [('friends.uid', storage.ASCENDING)], {'background': True})

            friends = Db(
            ).get('users').find_one({'uid': uid}, {'friends.uid': 1})

            if not friends:
                return ([], 0)

            if 'friends' not in friends:
                friends['friends'] = []

            list = []
            for friend in friends['friends']:
                list.append(friend['uid'])

            '''db.users.find({_id:{$nin : []}, friends : {$in : [3]}})'''
            data = Db().get('users').find({'uid': {"$nin": list}, 'activate': 1, 'friends.uid': {'$in': [uid]}}, {'friends': {'$slice': 0}})
            total = data.count()
            data = data.skip(start).limit(limit)

            result = []
            for friend in data:
                result.append(User(**friend))

            return (result, total)

        except DbError:
            output.error('cannot access db', 503)

    def getMutualFriends(self, me, friend, start=0, limit=10):
        try:
            Db().get('users').ensure_index(
                [('friends.uid', storage.ASCENDING)], {'background': True})

            aggr = Db().get('users').group({},
                                           {'uid': {'$in': [me, friend]}, 'activate': 1, 'friends': {'$exists': True}},
                                           {'count': {}},
                                           'function (doc, out) {  \
                                                  doc.friends.forEach(function(value) { \
                                                      if (!out.count[value.uid]) { \
                                                          out.count[value.uid] = 1 \
                                                      } else { \
                                                          out.count[value.uid] ++ \
                                                      } \
                                                   }); \
                                                }'
                                           )
            aggr = aggr.pop()
            mutual = []
            for uid, cnt in aggr['count'].items():
                if cnt == 1:
                    continue
                mutual.append(uid)

            if len(mutual) == 0:
                return []

            data = Db().get('users').find({'uid': {"$in": mutual}, 'friends.uid': {'$all': [me, friend]}, 'activate': 1}, {'friends': {'$slice': 0}}).skip(start).limit(limit)
            total = data.count()

            if total == 0:
                return ([], total)

            result = []
            for user in data:
                result.append(User(**user))

            return (result, total)
        except DbError:
            output.error('cannot access db', 503)

    def request(self, me, uid):
        try:
            checkMe = Db(
            ).get('users').find({'uid': me, 'friends.uid': uid}).count()

            if checkMe > 0:
                return False

            checkFriend = Db().get('users').find(
                {'uid': uid, 'activate': 1, 'friends.uid': me}).count()

            if checkFriend == 0:
                Db().get('users').update({'uid': me}, {'$push': {'friends':
                                                                 {'uid': uid, 'date': datetime.datetime.utcnow()}}})

                return True

            #Friend already requested, need approve
            raise NeedApprove('approve')
        except DbError:
            output.error('cannot access db', 503)

    def approve(self, me, uid):
        try:
            checkMe = Db(
            ).get('users').find({'uid': me, 'friends.uid': uid}).count()

            if checkMe > 0:
                return False

            checkFriend = Db(
            ).get('users').find({'uid': uid, 'friends.uid': me}).count()

            if checkFriend == 1:
                Db().get('users').update({'uid': me}, {'$inc': {'friends_count': 1}, '$push': {'friends': {'uid': uid, 'date': datetime.datetime.utcnow()}}})
                Db().get('users').update({'uid': uid, "friends.uid": me}, {'$inc': {'friends_count': 1}, '$set': {"friends.$.date": datetime.datetime.utcnow()}})

                #we are done here
                return True

            raise NeedRequest('request')

        except DbError:
            output.error('cannot access db', 503)

    def remove(self, me, uid):
        try:
            Db().get('users').update({'uid': me}, {'$inc': {'friends_count': -1}, '$pull': {'friends': {'uid': uid}}})  # remove from my friends
            Db().get('users').update({'uid': uid}, {'$inc': {'friends_count': -
                                                             1}, '$pull': {'friends': {'uid': me}}})  # remove from his friend

            return True
        except DbError:
            output.error('cannot access db', 503)

    def deny(self, me, uid):
        try:
            checkMe = Db(
            ).get('users').find({'uid': uid, 'friends.uid': me}).count()

            if not checkMe:
                return False

            Db().get('users').update({'uid': uid}, {'$pull':
                                                    {'friends': {'uid': me}}})  # remove from his friend

            return True
        except DbError:
            output.error('cannot access db', 503)

    def cancel(self, me, uid):
        try:
            checkMe = Db(
            ).get('users').find({'uid': me, 'friends.uid': uid}).count()

            if checkMe == 0:
                return False

            Db().get('users').update({'uid': me}, {'$pull': {
                                                   'friends': {'uid': uid}}})  # remove from my requests

            return True
        except DbError:
            output.error('cannot access db', 503)


class NeedApprove(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NeedRequest(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserFactory:

    def get(self, search):
        try:
            if isinstance(search, str):
                search = {'uid': search}
            else:
                tmp = {}
                for (key, value) in search.items():
                    tmp[key] = value.lower()
                search = tmp
                del tmp

            data = storage.Db().get(
                'users').find_one(search, {'friends': {'$slice': 0}})

        except storage.DbError:
            output.error('cannot access db', 503)

        if data is None:
                return None

        return User(**data)

    def getAllUsers(self):
        data = Db().get('users').find({'activate': 1, 'seq': {
                                       '$gt': 0}}, {'friends': {'$slice': 0}})
        result = []
        for friend in data:
            result.append(User(**friend))

        total = data.count()
        return (result, total)

    def new(self, obj):
        #Db().get('users').ensure_index([('username', storage.DESCENDING)], { 'unique' : True, 'background' : False, 'dropDups' : True })
        Db().get('users').ensure_index([('uid', storage.DESCENDING)
                                        ], {'unique': True, 'background': False, 'dropDups': True})
        Db().get('users').ensure_index([('email', storage.DESCENDING)
                                        ], {'unique': True, 'background': False, 'dropDups': True})
        Db().get('users').ensure_index([('connect.facebook', storage.DESCENDING)], {'unique': True, 'background': False, 'sparse': True, 'dropDups': True})

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
