from lib import router, log
from lib.config import Config
from hashlib import sha1
from webob import Request, Response
from json import loads
import urllib.parse


class Error(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Controller:

    class __impl ():

        def __init__(self):
            self._req = None
            self._router = router.Router()
            self._environ = None
            self._resp = None
            self._json = {}
            self.ROOT = None

        def __call__(self, environ, start_response):

            isJson = False

            if 'application/json' in environ.get('CONTENT_TYPE'):
                environ['CONTENT_TYPE'] = environ['CONTENT_TYPE'].replace(
                    'application/json', 'application/x-www-form-urlencoded')
                isJson = True

            for (key, value) in environ.items():
                if not key.startswith('HTTP_'):
                    continue

                environ[key] = value.encode('latin1').decode()

            self._req = Request(environ)

            if self._req.method == 'POST' and isJson:
                self._req.charset = 'utf8'

                try:
                    self._json = loads(self._req.body.decode(
                        'utf-8'), encoding=self._req.charset)
                except Exception as e:
                    self._json = None

                if self._json is not None and isinstance(self._json, dict):
                    post = []
                    for key, value in self.getPostJson().items():
                        #XXX danger
                        # if not isinstance( value, int ):
                        #     value = value.encode('utf-8')

                        post.append((key, value))

                    self._req.body = urllib.parse.urlencode(
                        post).encode('utf-8')

                elif self._json is not None and isinstance(self._json, list):
                    post = []
                    for value in self.getPostJson():
                        #XXX danger
                        # if not isinstance( value, int ):
                        #     value = value.encode('utf-8')

                        post.append(value)

                    self._req.body = urllib.parse.urlencode(
                        post).encode('utf-8')

            self._environ = environ
            return self._router.__call__(environ, start_response)

        def getRequest(self):
            return self._req

        def getPostJson(self):
            return self._json

        def checkToken(self):
            token = self.getToken()
            info = token.split(':')

            if not token or len(info) != 2:
                raise InvalidToken('Need rox-user-level')

            challenge = sha1((str(info[0]) + Config(
            ).get('token_secret')).encode('utf-8')).hexdigest()

            if challenge == info[1]:
                return True

            raise InvalidToken('failed to authenticate token')

        def getApiKey(self):
            return self._environ.get('HTTP_ROX_API_KEY', None)

        def getApiType(self):
            return int(self._environ.get('HTTP_ROX_API_TYPE', 0))

        def getRelation(self):
            return int(self._environ.get('HTTP_ROX_USER_RELATION', 0))

        def getToken(self):
            return self._environ.get('HTTP_ROX_USER_TOKEN', '')

        def getInstanceId(self):
            return self._environ.get('HTTP_ROX_INSTANCE_ID', '')

        def getOriginalHost(self):
            host = self._environ.get('HTTP_HOST', '')

            if not host:
                return ''

            return 'http://%s' % host

        def getHost(self):
            return self._environ.get('HTTP_HOST', '')

        def getUid(self):
            return self._environ.get('HTTP_ROX_USER_ID', None)

        def addRouting(self, domain, urls):
            self._router[domain] = urls

        def addRoutingFromConfig(self, domain, routing):
            entries = ()

            for entry in routing:
                vars = []

                if 'vars' not in entry:
                    entry['vars'] = []

                params = entry['params']
                if 'method' not in entry or not entry['method']:
                    params['method'] = '*'
                else:
                    params['method'] = entry['method']

                url = entry['url']
                params['pattern'] = url

                for name in entry['vars']:
                    vars.append(name)
                    url = url.replace(':' + name, entry['vars'][name])

                entries += (url, ServiceLoader(
                ).get(params['service'], params['module']), vars, params)

            self.addRouting(domain, entries)

        def getRouter(self):
            return self._router

        def getEnv(self):
            return self._environ

        def getResponse(self, flush=False):
            if (self._resp is None):
                self._resp = Response(
                    content_type='application/json', charset='UTF-8')
                self._resp.headers['Rox-Adult'] = "1"
                self._resp.headers['Access-Control-Allow-Origin'] = '*'

            if (flush == True):
                resp = self._resp
                self._resp = None
                self._req = None
                return resp

            return self._resp

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if Controller.__instance is None:
            Controller.__instance = Controller.__impl()

        self.__dict__['_Controller__instance'] = Controller.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    def __call__(self, environ, start_response):
        return self.__instance.__call__(environ, start_response)


class InvalidToken(Exception):
    pass


class ServiceLoader:
    _instance = {}

    def get(self, service, module):
        id = str(service + '_' + module).lower()
        if id not in self._instance:
            self._instance[id] = self.__load(service, module)

        return self._instance[id]

    def __load(self, service, module):
        print ('===> Mounting %s::%s service' % (service, module))
        exec ('from services.%s import %s' % (service.lower(), module))
        return locals()[module]()
