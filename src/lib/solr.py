from pysolr import *
from model.users import User, UserFactory
from lib.config import Config


class SolrError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Solr:

    class __impl ():

        def __init__(self):
            self.__solr = Config().get('solr')
            self.__cnx = {}
            self.connect()

        def connect(self, path=None):
            if not path:
                path = self.__solr['path']
            try:
                self.__cnx[path.lower()] = pysolr.Solr('http://%s:%s/%s' % (
                    self.__solr['host'], self.__solr['port'], path))
            except Exception as msg:
                raise SolrError("no connection" + str(msg))

        def get(self, path=None):
            if not path:
                path = self.__solr['path']

            if not path in self.__cnx:
                self.connect(path)

            return self.__cnx[path.lower()]

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if Solr.__instance is None:
            Solr.__instance = Solr.__impl()

        self.__dict__['_Solr__instance'] = Solr.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
