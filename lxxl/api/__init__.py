import requests
import time
import hashlib
import datetime
import json
from requests.auth import HTTPDigestAuth
import email.utils as eut

from .exceptions import *

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError('A json library is required to use ')


class Lxxl(object):

    def __init__(self, key, secret, host=None, version=None, api_section=''):
        self._r = LxxlRequest(key, secret, host, version)
        if api_section != '':
            self.api_section = api_section
        else:
            for x in ['users']:
                setattr(self, x, Lxxl(key, secret, host, version, x))

    def setCredentials(self, login, password):
        LxxlRequest.setCredentials(login, password)

    def call(self, method, params=None):
        try:
            # if params:
            #     params = tuple(params.values())
            # else:
            #     params = ''

            if method == 'create':
                resp = self._r.post('/%s/' % (self.api_section), params)
            elif params.keys():
                resp = self._r.post(
                    '/%s/%s' % (self.api_section, method),
                    params
                )
            else:
                resp = self._r.get(
                    '/%s/%s/%s' % (self.api_section, method, '/'.join(params)))

        except requests.exceptions.RequestException as e:
            raise HTTPRequestException(e)

        if resp.status_code != 200:
            raise HTTPRequestException(resp)

        return json.loads(resp.content.decode('utf-8'))

    def __getattr__(self, method_name):

        def get(self, *args, **kwargs):
            params = dict((i, j) for (i, j) in enumerate(args))
            params.update(kwargs)
            return self.call(method_name.replace('_', '-'), params)

        return get.__get__(self)

    def __getitem__(self, method_name):
        def get(self, *args, **kwargs):
            params = dict((i, j) for (i, j) in enumerate(args))
            params.update(kwargs)
            return self.call(method_name.replace('_', '-'), params)

        return get.__get__(self)


class LxxlRequest(object):
    SESSION = requests.session()
    AUTH = None

    def __init__(self, key, secret, host=None, version=None):
        self.key = key
        self.secret = secret
        self.host = host if host else 'api.lxxl.net'
        self.version = version if version else '1.0'

        self.api_url = "http://%s/%s" % (self.host, self.version)
        self.algo = "md5"
        self._auth = None
        self._delta = 0

    @classmethod
    def setCredentials(self, login, password):
        self.AUTH = HTTPDigestAuth(login, password)

    def get(self, url, params={}):
        return self.request('GET', url, params=params)

    def post(self, url, params={}):
        return self.request('POST', url, data=json.dumps(params))

    def request(self, method, url, **args):
        if 'headers' not in args:
            args['headers'] = {}

        if LxxlRequest.AUTH:
            args['auth'] = LxxlRequest.AUTH

        args['headers']['User-Agent'] = 'PyLxxl 0.1'

        args['hooks'] = {'pre_request': self._setSignature,
                         'response': self._postHook}

        return LxxlRequest.SESSION.request(method, '%s%s' % (
            self.api_url, url
        ), **args)

    def _setSignature(self, req):
        ts = int(time.time()) + self._delta
        ha = self.__hash('%s:%s:%s' % (self.key, self.secret, ts))
        signature = self.__hash('%s:%s:%s' % (
            req.method, requests.utils.urlparse(req.url).path, ha))
        sig = 'access '
        sig += 'Timestamp="%s", Signature="%s", KeyId="%s", Algorithm="%s"' % (
            ts, signature, self.key, self.algo
        )

        req.headers.update({'X-Signature': sig})

    def _postHook(self, resp):
        if 'signature expired' not in resp.content.decode('utf-8'):
            return

        delta = datetime.datetime.utcnow() - datetime.datetime(
            *eut.parsedate(resp.headers.get('Date'))[:6])
        self._delta = int(delta.total_seconds())
        self._setSignature(resp.request)

        resp.request.send(anyway=True)

        _r = resp.request.response
        _r.history.append(resp)

        return _r

    def __hash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()
