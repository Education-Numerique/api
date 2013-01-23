import datetime

from lxxl.lib import router, output
from lxxl.lib.app import Controller, Error
from lxxl.lib.storage import Db
from lxxl.lib.flush import FlushRequest
from lxxl.model.users import Factory as UserFactory


class Acl(router.Root):

    def set(self, environ, params):
        try:
            Controller().checkToken()
            #relation = Controller().getRelation()
            me = Controller().getUid()
            apikey = Controller().getApiKey()

            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)

            me = UserFactory.get(me)

            if me.level < 3:
                output.error('forbidden', 403)

            user = UserFactory.get(params['uid'])
            newLevel = params['role']

            if newLevel == 'admin':
                user.level = 3
            elif newLevel == 'reviewer':
                user.level = 2
            else : 
                user.level = 1


            Db().get('users').update({'uid': user.uid}, user)

            output.success('acl changed', 200)

        except Error:
            pass

        return Controller().getResponse(True)