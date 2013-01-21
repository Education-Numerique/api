import requests
from .config import Config
from json import JSONDecoder
from hashlib import sha1


class AuthError(Exception):
    def __init__(self, value, code=400, internal=0):
        self.value = value
        self.code = code
        self.internal = internal

    def __str__(self):
        return repr(self.value)

    def getCode(self):
        return self.code

    def getInternal(self):
        return self.internal


class PictureError(Exception):
    pass


class Auth:
    SESSION = requests.session()

    class __impl():

        def __init__(self):
            #self.__cfg = Config().get('auth')['admin']
            self.host = 'https://%s:443' % ('graph.facebook.com')
            #self.__cnx = Http('.cache')
            #self.__headers = {}

        def check(self, fbid, token):
            uri = '/me?access_token=%s' % token

            try:
                resp = Auth.SESSION.get(
                    self.host + uri, verify=True, timeout=5)
            except Exception as e:
                raise AuthError('facebook error : %s' % e, 500)

            if resp.status_code != 200:
                raise AuthError('invalid token', 400)

            datas = JSONDecoder().decode(resp.content.decode('utf-8'))

            if datas['id'] != fbid:
                raise AuthError('Invalid user', 401)

            return datas

        def getPicture(self, fbid):
            try:
                resp = Auth.SESSION.get(self.host + '/%s/picture?type=large' %
                                        fbid, verify=True, timeout=5)
            except Exception as e:
                raise PictureError('picture fetch error : %s' % e)

            if resp.status_code != 200:
                raise PictureError(
                    'picture fetch error : status code' % resp.status)

            return resp.content

        def getSalt(self, token):
            secret = (token + Config().get('social_secret')).encode('utf-8')
            return sha1(secret).hexdigest()

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        if Auth.__instance is None:
            Auth.__instance = Auth.__impl()

        self.__dict__['_Auth__instance'] = Auth.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)
