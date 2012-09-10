from lib.config import Config
from lib import app, output, storage
from model.auth import users, access
import python_digest
import time
import hashlib
import random
import re


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

DIGEST_AUTH = 1
ANONYM_AUTH = 2
ADMIN_AUTH = 3
API_ONLY = 4


class Auth(object):

    def __init__(self):
        self.__uid = ''
        self.__env = app.Controller().getEnv()
        self.__cfg = Config()
        self.__req = app.Controller().getRequest()
        self.__resp = app.Controller().getResponse()

    def check(self, mode=DIGEST_AUTH, requestedUid=None):
        try:
            if mode == ADMIN_AUTH:
                self.checkAcessKey(False, True)
            elif mode == API_ONLY:
                self.checkAcessKey(True)
            else:
                self.checkAcessKey()

            #CAREFUL, this revoke user auth
            if mode == API_ONLY:
                return True

            if mode == ANONYM_AUTH or mode == ADMIN_AUTH:
                self.checkUserId(requestedUid, True)
            else:
                self.checkUserId(requestedUid)

        except AuthError as msg:
            output.error(str(msg), msg.getCode(), msg.getInternal())

    def checkUserId(self, requestedUid=None, anonymous=False):

        if ('Authorization' not in self.__req.headers):
            self.__setAuthenticate()
            raise AuthError('User#auth need user Authentification', 401, 2)

        #XXX check header validity
        http_authorization_header = self.__req.headers['Authorization']

        digest_response = python_digest.parse_digest_credentials(
            http_authorization_header)

        if digest_response is None:
            self.__setAuthenticate()
            raise AuthError('User#Auth need digest authentification', 401, 2)

        if digest_response.uri != self.__req.path_qs:
            self.__setAuthenticate()
            raise AuthError('User#Auth invalid uri', 403, 2)

        if (anonymous is True and
                digest_response.username.lower() != "anonymous") or \
            (anonymous is False and
                digest_response.username.lower() == "anonymous"):
            self.__setAuthenticate()
            raise AuthError('User#Auth forbidden', 403, 2)

        if python_digest.validate_nonce(
            digest_response.nonce,
            self.__cfg.get('nonce_secret')
        ) is not True:
            self.__setAuthenticate(True)
            raise AuthError('User#auth invalid nonce', 401, 2)

        #fetch user
        obj = users.UserFactory().get(digest_response.username)

        if not obj:
            self.__setAuthenticate()
            raise AuthError('User#auth unknown user', 404, 2)

        if obj.activate == 0:
            self.__setAuthenticate()
            raise AuthError('User#auth unactivated user', 403, 2)

        expected_request_digest = python_digest \
            .calculate_request_digest(
                self.__req.method,
                obj.digest,
                digest_response)
        #nonce lifetime
        delta = time.time(
        ) - python_digest.get_nonce_timestamp(digest_response.nonce)

        if delta > self.__cfg.get('nonce_ttl'):
            self.__setAuthenticate(True)
            raise AuthError('User#auth nonce expired', 401, 2)

        #grab session
        sessId = hashlib.sha1(
            digest_response.nonce.encode('utf-8')).hexdigest()
        prevRequest = storage.Memcache().get(sessId, 'session')

        #if not, check memcache status
        if not prevRequest:
            try:
                storage.Memcache().checkAlive()
                self.__setAuthenticate(True)
                raise AuthError('User#auth nonce expired', 401, 2)
            except storage.MemcacheError:
                raise AuthError('Service unavailable', 503, 2)

        #Check nc:
        if not prevRequest or prevRequest['nc'] >= digest_response.nc:
            self.__setAuthenticate(True)
            raise AuthError('User#auth invalid nonce count', 401, 2)

        #check opaque
        if prevRequest['opaque'] != digest_response.opaque:
            self.__setAuthenticate(True)
            raise AuthError('User#auth invalid opaque', 401, 2)

        #check digest response
        if expected_request_digest != digest_response.response:
            self.__setAuthenticate()
            raise AuthError('User#auth invalid credentials', 401, 2)

        #store nonce count
        self.__storeSession(sessId, digest_response.opaque, digest_response.nc)

        if anonymous is False:
            self.__resp.headers['Rox-User-Token'] = str(obj.getToken())
            self.__resp.headers['Rox-User-id'] = str(obj.uid)

        #get level
        if not requestedUid:
            return True

        friends = users.FriendsFactory().get(obj.uid)

        if not friends:
            raise AuthError('User#auth error computing level', 500, 2)

        self.__resp.headers['Rox-User-Relation'] = str(
            friends.getLevel(requestedUid))

        return True

    def checkAcessKey(self, apiOnly=False, needAdmin=False):

        if ('X-Signature' not in self.__req.headers):
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth need api signature', 401, 1)

        infos = self.__parseAuthorization(
            self.__req.headers['X-Signature'], 'access')

        if not infos:
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth invalid signature format', 401, 1)

        for k in ['timestamp', 'keyid', 'algorithm', 'signature']:
            if not k in infos:
                if not apiOnly:
                    self.__setAuthenticate()
                raise AuthError('api#auth invalid signature format', 401, 1)

        if infos['algorithm'].lower() != 'md5':
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth invalid algorithm', 401, 1)

        keyId = infos['keyid']
        timestamp = infos['timestamp']

        try:
            timestamp = float(timestamp)
        except:
            raise AuthError('api#auth invalid timestamp', 401, 1)

        # Tolerate a time offset of 5 min
        if abs(time.time() - timestamp) > 300:
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth signature expired', 401, 1)

        obj = access.KeyFactory().get(keyId)

        if not obj:
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth unknow app key', 401, 1)

        if needAdmin and obj.admin != 1:
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth unauthorized app key', 403, 1)

        if not self.__checkOrigin(obj.hosts):
            raise AuthError('api#auth unauthorized host', 403, 1)

        ha = self.__hash('%s:%s:%s' % (keyId, obj.secret, infos['timestamp']))
        signature = self.__hash(
            '%s:%s:%s' % (self.__req.method, self.__req.path_info, ha))

        if infos['signature'] != signature:
            if not apiOnly:
                self.__setAuthenticate()
            raise AuthError('api#auth invalid signature', 401, 1)

        self.__resp.headers['Rox-Api-Key'] = str(obj.key)

        if obj.admin is True:
            self.__resp.headers['Rox-Api-Type'] = "1"
        else:
            self.__resp.headers['Rox-Api-Type'] = "0"

        return True

    def __checkOrigin(self, whitelist):
        origin = False
        xgate = False

        if 'origin' in self.__req.headers:
            origin = self.__req.headers['origin'].lower(
            ).replace('http://', '').replace('https://', '')
            if ':' in origin:
                origin = origin.split(':').pop(0)

        if 'x-gate-origin' in self.__req.headers:
            xgate = self.__req.headers['x-gate-origin'].lower(
            ).replace('http://', '').replace('https://', '')
            if ':' in xgate:
                xgate = xgate.split(':').pop(0)

        if origin:

            if origin == app.Controller().getHost():

                if not xgate:
                    return False

                if xgate in whitelist:
                    return True

            else:

                if origin in whitelist:
                    return True

        else:

            if not xgate:
                return True

            if xgate in whitelist:
                return True

        return False

    def __setAuthenticate(self, stale=False):
        random.seed()
        opaque = str(random.getrandbits(128))

        www_authenticate_header = python_digest.build_digest_challenge(
            time.time(),
            self.__cfg.get('nonce_secret'),
            Config().get('realm'),
            opaque,
            stale
        )

        #grab nonce and calculate reqId
        m = re.search('nonce="([a-z-A-Z0-9.:]+)"', www_authenticate_header)
        sessId = hashlib.sha1(m.group(1).encode('utf-8')).hexdigest()

        self.__storeSession(sessId, opaque, 0)

        self.__resp.headers['WWW-Authenticate'] = www_authenticate_header

    def __parseAuthorization(self, header, schema):
        sc = header.split(' ').pop(0).lower()

        if sc != schema:
            return
        auth = header[len(schema):].split(',')
        info = {}
        for a in auth:
            tab = a.split('=')
            if len(tab) < 2:
                return False
            key = tab.pop(0).strip().lower()
            value = tab.pop(0).strip('" ')
            info[key] = value
        return info

    def __storeSession(self, sessId, opaque, nc):

        storage.Memcache().set(sessId,
                               {'opaque': opaque,
                                'nc': nc},
                               'session')

    def __hash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()
