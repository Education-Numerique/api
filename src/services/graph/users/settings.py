import router
from app import Controller, Error
import output
from storage import *
from flush import FlushRequest
import datetime


class Settings(router.Root):
    
    def set(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()
            
            if Controller().getApiType() != 1:
                output.error('#ApiKeyUnauthorized : none of your business', 403)
                
            if relation != 2:
                output.error('#UserUnauthorized : none of your business', 403)
            
            data = Controller().getPostJson()
            
            if not data:
                output.error('bad json format', 400)
            
            Db().get('settings').update({ 'uid' : me}, {'datas' : data, 'uid' : me, 'updated' : datetime.datetime.utcnow()}, True)
            
            #Let's flush a few stuff
            FlushRequest().request('users.Settings.[get]', {'uid' : me})
            
            output.success('settings updated', 200)
            
        except Error:
            pass
        
        return Controller().getResponse(True)
    
    def get(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()

            if relation != 2:
                output.error('#UserUnauthorized : none of your business', 403)
            
            Db().get('settings').ensure_index([('uid', ASCENDING)], { 'background' : True })
            settings = Db().get('settings').find_one({ 'uid' : me})
            
            if not settings:
                settings = {}
                settings['datas'] = {}
            
            output.noCache()
            output.varnishCacheManager('1 year', 'Rox-User-Relation')
            
            output.success(settings['datas'], 200)
            
        except Error:
            pass
        
        return Controller().getResponse(True)