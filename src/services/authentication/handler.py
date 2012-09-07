from lib import router, output
from lib.app import Error, Controller


class Handler(router.Root):
    
    def check (self, environ, params):
        try:
            output.success('woooohooooo', 202)
        except Error:
            pass
        
        return Controller().getResponse(True) 
    
