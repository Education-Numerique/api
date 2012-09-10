import router
from app import Controller, Error
import output
from storage import *
from flush import FlushRequest
import datetime

class Preferences(router.Root):
    
    def set(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()
            apikey = Controller().getApiKey()
            
            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)
                
            if relation != 2:
                output.error('#ApiKeyUnauthorized : none of your business', 403)
            
            data = Controller().getPostJson()
            
            if not data:
                output.error('bad json format', 400)
            
            Db().get('preferences').update({ 'uid' : me, 'apikey' : apikey}, {'datas' : data, 'apikey' : apikey, 'uid' : me, 'updated' : datetime.datetime.utcnow()}, True)
            
            
            
            #Let's flush a few stuff
            FlushRequest().request('users.Preferences.[get]', {'uid' : me})
            
            output.success('preferences updated', 200)
            
        except Error:
            pass
        
        return Controller().getResponse(True)
    
    
    def get(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            me = Controller().getUid()
            apikey = Controller().getApiKey()

            if relation != 2:
                output.error('#ApiKeyUnauthorized : none of your business', 403)
                
            Db().get('preferences').ensure_index([('uid', ASCENDING), ('apikey', ASCENDING)], { 'background' : True })
            prefs = Db().get('preferences').find_one({ 'uid' : me, 'apikey' : apikey})
            
            if not prefs:
                prefs = {}
                prefs['datas'] = {}
            
            output.noCache()
            output.varnishCacheManager('1 year', ['Rox-User-Relation', 'Rox-Api-Key'])
            
            output.success(prefs['datas'], 200)
            
        except Error:
            pass
        
        return Controller().getResponse(True)
