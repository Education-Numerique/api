import router
from app import Controller, Error
import output

from config import Config
from flush import FlushRequest

from storage import Db
from gridfs import NoFile
from gridfs.errors import CorruptGridFile

from PIL import Image, ImageOps
import io



class Avatar(router.Root):
    
    def get(self, environ, params):
        file = im = tmp = None
        try:
            filename = params['uid']
            
            if 'size' not in params:
                output.error('need size param', 400)
            
            
            size = self.__getSize(params['size'])
            
            if not size:
                output.error('invalid size', 400)
            
            
            try:
                file = Db().getGridFs('avatar').get_last_version(filename)
            except NoFile:
                output.cacheManager(3600 * 24 * 2)
                output.error('not found', 404)
            
            im = Image.open(file)
            tmp = io.BytesIO()
            
            width, height = im.size
            if size['mode'] == 'crop':
                width = int(size['width'])
                height = int(size['height'])
                im = ImageOps.fit(im, (width, height), Image.ANTIALIAS, 0, (.5, .5))
            else:
                im.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
            
            if im.mode != 'RGB':
                im = im.convert('RGB')
                    
            im.save(tmp, 'JPEG', quality=70)
            
            
            
            resp = Controller().getResponse()
            resp.headers['Content-Type'] = str('image/jpeg')
            resp.headers['Content-Length'] = str(file.length)
            resp.headers['Last-Modified'] =  file.upload_date.strftime("%a, %d %b %Y "
                                                                  "%H:%M:%S GMT")
            
            resp.body = tmp.getvalue()
            
            
            output.varnishCacheManager('1 year')
            output.cacheManager(3600 * 24)
            #cleanup
            tmp.close()
            
        except Error:
            pass
        finally:
            del file, im, tmp
        
        return Controller().getResponse(True)
    
    def set(self, environ, params):
        file = img = None
        try:
            
            Controller().checkToken()
            relation = Controller().getRelation()
            
            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)
                
            if relation != 2:
                output.error('#ApiKeyUnauthorized : none of your business', 403)
            
            req = Controller().getRequest()
            uid = params['uid']
            limits = Config().get('upload')['images']
            requestLength = int(req.headers['Content-Length'])
            
            if requestLength > int(limits['size']):
                output.error('file too fat', 413)
            
            
            try:
                file = req.body
                req.make_body_seekable()
                img = Image.open(req.body_file)
                img.verify()
                
                (width, height) = img.size

                if width  > int(limits['width']) or \
                   height > int(limits['height']) or \
                   img.format.lower() not in limits['formats']:
                    raise Exception("bad bad bad")
                
               
                
                Db().getGridFs('avatar').put(file, content_type="image/%s" % img.format.lower(), filename=uid)
                Db().get('users').update({'uid' : uid}, {'$set' : { 'hasAvatar' : True}})  
            
            except:
                output.error('bad image', 400)
                
                
            #clean old stuff
            try:
                file = Db().getGridFs('avatar').get_version(uid, -2)
                Db().getGridFs('avatar').delete(file._id)
                
                self.__flushAll(uid)
            except NoFile:
                pass
            except CorruptGridFile:
                pass
            
           
        except Error:
            pass
        finally:
            del img, file
        
        
                
        return Controller().getResponse(True)
    
    
    def delete(self, environ, params):
        file = None
        try:
            Controller().checkToken()
            relation = Controller().getRelation()
            
            if Controller().getApiType() != 1:
                output.error('Not your api business', 403)
                
            if relation != 2:
                output.error('#ApiKeyUnauthorized : none of your business', 403)
                
                
            uid = params['uid']
            
            #try to delete
            try:
                file = Db().getGridFs('avatar').get_version(uid, -1)
                Db().getGridFs('avatar').delete(file._id)
                
                self.__flushAll(uid)
            except NoFile:
                pass
            except CorruptGridFile:
                pass
            
            
            output.access('avatar deleted', 200)
        except Error:
            pass
        finally:
            del file
        
                
        return Controller().getResponse(True)
    
    
    
    def __getSize(self, name):
        wlSize = Config().get('avatar')['sizes']
         
        for size, value in wlSize.items():
            if name.lower() == size.lower():
                return value
            
        return None
    
    def __flushAll(self, uid):
        wlSize = Config().get('avatar')['sizes']

        for size in wlSize:
            FlushRequest().request('users.Avatar.get', {'uid' : uid, 'size': size})