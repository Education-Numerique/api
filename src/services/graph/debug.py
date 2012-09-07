from lib import router, output
from lib.app import Error, Controller
import os

class Debug(router.Root):

    def debug (self, environ, params):
        try:
            resp = Controller().getResponse()
            path = os.path.join(Controller().ROOT, 'static/debug.html')
            resp.text = open(path).read()
            resp.content_type = "text/html; charset=UTF-8"
        except Error:
            pass
        
        return Controller().getResponse(True)
    
