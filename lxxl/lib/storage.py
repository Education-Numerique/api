import pymongo
import bson
from pymongo import errors
from gridfs import GridFS
from gridfs.errors import NoFile

import memcache
from .config import Config


class DbError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING
ObjectId = bson.objectid.ObjectId


class Db:

    class __impl ():

        def __init__(self):
            self.__cfg = Config().get('db')
            self.__collections = {}
            self.connect()

            for seq in self.__cfg.get('seq'):
                self.__ensureSeq(seq)

        def connect(self):
            try:
                connection = pymongo.Connection(
                    self.__cfg.get('host'), self.__cfg.get('port'))
                self.db = connection[self.__cfg.get('db')]
            except errors.ConnectionFailure:
                raise DbError("no connection")

        def get(self, name):
            if not name:
                return None

            if not self.db:
                self.connect()

            if name not in self.__collections:
                self.__collections[name] = MyCollection(self.db[name])

            return self.__collections[name]

        def getGridFs(self, name):
            if not name:
                return None

            if not self.db:
                self.connect()

            if name not in self.__collections:
                self.__collections[name] = GridFS(self.db, name)

            return self.__collections[name]

        def __ensureSeq(self, name):
            exists = self.get('seq').find_one({'_id': name})

            if exists:
                return True

            self.get('seq').insert({"_id": name, "seq": 1})

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if Db.__instance is None:
            Db.__instance = Db.__impl()

        self.__dict__['_Db__instance'] = Db.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class MyCollection:

    def __init__(self, obj):
        self.__cnx = obj

    def find_one(self, search, *args, **kwargs):
        try:
            return self.__cnx.find_one(search, *args, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def find(self, *args, **kwargs):
        try:
            return self.__cnx.find(*args, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def insert(self, data, safe=False):
        try:
            return self.__cnx.insert(data, True, safe)
        except errors.ConnectionFailure:
            self.__failHandler()

    def ensure_index(self, key_or_list, kwargs):
        try:
            return self.__cnx.ensure_index(key_or_list, ttl=600, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()
        #except:
        #    pass

    def update(self, search, data, upsert=False, manipulate=False,
               safe=False, multi=False, **kwargs):
        try:
            data = data.__dict__
        except:
            pass

        try:
            return self.__cnx.update(search, data, upsert, manipulate, safe, multi, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def find_and_modify(self, query, update=None, upsert=False, **kwargs):
        try:
            return self.__cnx.find_and_modify(query, update, upsert, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()
        except:
            pass

    def increment(self, namespace=None):
        key = self.__cnx.name if not namespace else '%s.%s' % (
            self.__cnx.name, namespace)
        resp = Db().get('seq').find_and_modify(
            {'_id': key}, {'$inc': {"seq": 1}}, True, new=True)
        return resp['seq']

    def remove(self, obj, safe=False, **kwargs):
        try:
            return self.__cnx.remove(obj, safe, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def group(self, key, condition, initial, reduce, finalize=None):
        try:
            return self.__cnx.group(key, condition, initial, reduce, finalize)
        except errors.ConnectionFailure:
            self.__failHandler()

    def map_reduce(self, map, reduce, out, merge_output=False,
                   reduce_output=False, full_response=False, **kwargs):
        try:
            return self.__cnx.map_reduce(map, reduce, out, merge_output,
                                         reduce_output, full_response, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def inline_map_reduce(self, map, reduce, full_response=False, **kwargs):
        try:
            return self.__cnx.inline_map_reduce(map, reduce, full_response, **kwargs)
        except errors.ConnectionFailure:
            self.__failHandler()

    def drop(self):
        try:
            return self.__cnx.drop()
        except errors.ConnectionFailure:
            self.__failHandler()

    def __failHandler(self):
        raise DbError("no connection")


class MemcacheError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Memcache:

    class __impl ():

        def __init__(self):
            instances = Config().get('memcache')['instances']
            self.mc = memcache.Client(instances, debug=0)
            self.ttl = Config().get('memcache')['ttl']

        def set(self, key, value, domain=''):
            return self.mc.set("%s_%s" % (domain.encode('utf-8'), key.encode('utf-8')), value, self.ttl)

        def get(self, key, domain=''):
            return self.mc.get("%s_%s" % (domain.encode('utf-8'), key.encode('utf-8')))

        def delete(self, key, domain=''):
            return self.mc.delete("%s_%s" % (domain.encode('utf-8'), key.encode('utf-8')))

        def incr(self, key, domain=''):
            return self.mc.incr("%s_%s" % (domain.encode('utf-8'), key.encode('utf-8')))

        def decr(self, key, domain=''):
            return self.mc.decr("%s_%s" % (domain.encode('utf-8'), key.encode('utf-8')))

        def checkAlive(self):
            resp = self.get('internal_alive', '')

            if resp:
                return True

            check = self.set('internal_alive', True)
            if not check:
                raise MemcacheError('memcache is down')

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if Memcache.__instance is None:
            Memcache.__instance = Memcache.__impl()

        self.__dict__['_Controller__instance'] = Memcache.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
