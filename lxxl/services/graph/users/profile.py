from lxxl.lib import router, output
from lxxl.lib.app import Controller, Error
from lxxl.lib.storage import Db
from lxxl.lib.flush import FlushRequest

from lxxl.model.users import User, Factory as UserFactory, Duplicate

import datetime


class Profile(router.Root):

    def get(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()

            # fix privacy
            # if relation < 1:
            #     output.error('#ApiKeyUnauthorized', 403)

            user = UserFactory.get(params['uid'])

            if not user:
                output.error('unknown user', 404)

            #XXX uncomment me ?
            # if user.activate == 0:
            #   output.error('unactivated user', 404)

            result = {}

            Db().get('profile').ensure_index(
                [('uid', ASCENDING)], {'background': True})
            profile = Db().get('profile').find_one({'uid': params['uid']})

            if not profile:
                profile = {}
                profile['datas'] = {}

            result['profile'] = profile['datas']
            result['email'] = user.email
            result['username'] = user.username

            if user.premium:
                result['premium'] = True

            if user.hasAvatar is True:
                result['hasAvatar'] = True
            else:
                result['hasAvatar'] = False

            result['friends'] = user.friends_count
            result['relation'] = relation

            output.noCache()
            output.varnishCacheManager('1 year', ['Rox-User-Relation'])

            output.success(result, 200)

        except Error:
            pass

        return Controller().getResponse(True)

    def set(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()
            apikey = Controller().getApiKey()

            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)

            if relation != 2:
                output.error(
                    '#ApiKeyUnauthorized : none of your business', 403)

            user = UserFactory.get(params['uid'])

            if not user:
                output.error('unknown user', 404)

            data = Controller().getPostJson()

            if not data:
                output.error('bad json format', 400)

            Db().get('profile').update({'uid': me}, {
                'datas': data,
                'uid': me,
                'updated': datetime.datetime.utcnow()
            }, True)

            #Let's flush a few stuff
            FlushRequest().request('users.Profile.[get]', {'uid': me})

            try:
                UserSync.update(user)
            except:
                print('////####\\\\\\\\ user index error')

            output.success('profile updated', 200)

        except Error:
            pass

        return Controller().getResponse(True)
