from .config import Config
from json import JSONDecoder
import requests


class AdminRequest():
    SESSION = requests.session()

    class __impl ():

        def __init__(self):
            self.__cfg = Config().get('auth')['admin']
            self.host = 'http://%s:%s' % (
                self.__cfg['host'], self.__cfg['port'])
            self.__headers = {'Content-type':
                              'application/x-www-form-urlencoded'}

        def request(self, uri, datas={}, method='post'):
            #try:

            try:
                resp = AdminRequest.SESSION.request(
                    method.upper(),
                    self.host + uri,
                    data=datas, headers=self.__headers, timeout=2)
            except Exception as err:  # timeout error
                raise AdminError(err)

            return AdminResponse(resp)

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if AdminRequest.__instance is None:
            AdminRequest.__instance = AdminRequest.__impl()

        self.__dict__['_AdminRequest__instance'] = AdminRequest.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class AdminResponse:

    def __init__(self, obj):
        self.__headers = obj.headers
        self.__body = obj.content
        self.__headers['status'] = obj.status_code

    def getHeader(self, name, default=None):
        try:
            return self.__headers[name]
        except:
            pass

        return default

    def getBody(self):
        try:
            return JSONDecoder().decode(self.__body.decode('utf-8'))
        except:
            return self.__body


class AdminError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
