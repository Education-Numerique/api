# from httplib2 import Http
from .config import Config
from .app import Controller
import requests


class FlushRequest():
    SESSION = requests.session()

    class __impl ():

        def __init__(self):
            self.__cfg = Config().get('flush')
            self.host = 'http://%s' % Controller().getFullHost()
            self.__headers = {'Host': Controller().getFullHost()}
            FlushRequest.SESSION.config['keep_alive'] = True

        def request(self, matching, values):

            urls = Controller().getRouter().matchRoutes(matching, values)

            try:
                for url in urls:
                    try:
                        resp = FlushRequest.SESSION.request('ROX-PURGE', self.host + url, headers=self.__headers, timeout=2)
                        #(resp, content) = self.__cnx.request(self.host + url, 'ROX-PURGE', headers = self.__headers)
                    except Exception as err:
                        raise FlushError(err)

            except FlushError as err:
                print("FLUSH FAIL %s " % err)
                return False
            else:
                return True

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if FlushRequest.__instance is None:
            FlushRequest.__instance = FlushRequest.__impl()

        self.__dict__['_FlushRequest__instance'] = FlushRequest.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class FlushError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
